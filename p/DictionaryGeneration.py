#!/usr/bin/env python
# coding: utf-8

# Основная модель генерации ссылки (база данных уже с добавлением исследуемого домена)

# In[17]:


import numpy as np
import pandas as pd
import pickle
import copy
import datetime

from tensorflow.keras.layers import Dense, SimpleRNN, Input, Embedding, Bidirectional, LSTM, GRU, TimeDistributed
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.text import Tokenizer, text_to_word_sequence
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


# In[23]:


def DictionaryGeneration(file, link):
    # Найти такое число, которое будет разделять 0 и 1
    def FindMinimum(x, y):
        accuracyResults = []
        minimums = [0.1, 0.01, 0.001, 0.0001, 0.00001]
        for m in minimums:
            y_refined = [[['0' for j in range(y.shape[2])] for i in range(y.shape[1])] for i in range(y.shape[0])]
            for i in range(len(y)):
                for j in range(len(y[i])):
                    for c in range(len(y[i][j])):
                        y_refined[i][j][c] = '1' if y[i][j][c] > m else '0'
            y_refined = np.array(y_refined).astype(int)
            accuracyResults.append(СalculatedAccuracy(x, y_refined))
        MaxAccuracyResults = np.array(accuracyResults).argmax()
        return minimums[MaxAccuracyResults]
    
    # Расчитывает оценку точности для 3х мерный массивов
    def СalculatedAccuracy(x, y):
        accuracyScore = 0
        first = True
        for i in range(len(x)):
            for j in range(len(x[i])):
                if first:
                    accuracyScore = accuracy_score(list(x[i][j]), y[i][j])
                    first = False
                    continue
                accuracyScore = (accuracyScore + accuracy_score(x[i][j], y[i][j])) / 2
        return accuracyScore
    
    def create_links(test_x, y_proba_example):
        generatedLinks = []
        index = test_x.shape[0] - 1
        for i in range(1, len(y_proba_example[index])):
            part2 = tokenizer.index_word[test_x[index][i-1][0]] + '/' + tokenizer.index_word[y_proba_example[index][i-1]]
            part3 = tokenizer.index_word[y_proba_example[index][i]]
            generatedLinks.append(part2)
            generatedLinks.append('/'.join([part2, part3]))
        generatedLinks = set(generatedLinks)
        return generatedLinks
    
    # Импортирует
    with open(file, 'rb') as f:  
        df = pickle.load(f)     # базу данных с активным доменом 
        words = pickle.load(f)  # список всевозможных токенов
        
    maxWordsCount = 2047
    lenMWC = len(np.binary_repr(maxWordsCount)) # количество цифр в двоичном виде числа 2000
    tokenizer = Tokenizer(num_words=maxWordsCount, # отбирает 2000 самых популярных слов в words
                          lower=True, char_level=False) # и присваивает каждому токену свой номер
    tokenizer.fit_on_texts(words)
    
    # y - массив массиво, где [кол-во доменов в базе данных][словарб токенов данного домена]
    y = []
    for index in range(df.shape[0]): 
        y.append(df.loc[index,'dictionary']) 
        
    # Преобразования слова в число, данное этому слову Tokenizer
    y = tokenizer.texts_to_sequences(y) 
    
    # Максимальная длинна массива токенов среди всех доменов
    m_l = 0 
    for i in y: 
        if m_l < len(i):
            m_l = len(i)
            
    # Приведение к всех массивов токенов к m_l путём повторения массива каждого домена
    for i in range(len(y)): 
        while len(y[i]) < m_l: 
            y[i].extend(y[i])
        y[i] = y[i][:m_l]
        
    # Формированиея входных данных
    x = np.array(y) # где x[кол-во доменов в базе данных][словарб токенов данного домена][дополнительно расширение 1]
    x = x.reshape(df.shape[0], m_l, 1) 
    
    
    # Сдвиг каждого массива токенов на один влево, чтобы симитировать y[0][0] следующее слово за x[0][0]
    for i in range(len(y)): 
        el = y[i].pop(0)    
        y[i].append(el)
    
    # Приведенние y в вид y[кол-во доменов в базе данных][словарб токенов данного домена][бинарный вид номера слова]
    for i in range(len(y)):
        for j in range(len(y[i])):
            y[i][j] = list(np.binary_repr(y[i][j], width = lenMWC))
            
    # Преобразование массив массивов в вид матрицы 
    y = np.array(y) 
    
    # Преобразование str '0' и '1' в числа 0 и 1
    y = y.astype(int) 

    # Параметры модели и её обучения
    gru1 = 200
    b_s = 200
    ep = 5
    
    # Модель
    model = Sequential()  
    model.add(GRU(gru1,  # скрытый слой для всей модели
                        activation='relu',  # функция активации
                        return_sequences=True,  # возвращать предсказание для каждого входного экемпляра
                        input_shape=(x.shape[1], x.shape[2])))  # размерность входных данных
    model.add(TimeDistributed(Dense(lenMWC,  # полносвязный слой
                                    activation='softmax')))  # функция активации - выбор наиболее вероятного ответа
    
    model.compile(loss='categorical_crossentropy',  # функция оценки ошибки
                  metrics=['accuracy'],  # метрика точности
                  optimizer='adam')  # оптимизатор (метод поиска оптимальных параметров)
    
    # Обучение модели
    history = model.fit(x, y, batch_size=b_s, epochs=ep) 
    
    # Предсказывание модели на тестовых данных
    y_proba = model.predict(x, verbose=1)
    
    # Числа больше minimum будут счиаться еденичкой 
    minimum = FindMinimum(y, y_proba)
    
    link = link.split('/')[3:]
    link = tokenizer.texts_to_sequences(link)
    link = [list(filter(lambda x: x != [], link))]
    while len(link[0]) < m_l:
        link[0].extend(link[0]) 
    link = [link[0][:m_l]]
    link = np.array(link)
    link_proba = model.predict(link, verbose=1)
    
    # В будущем массив массивов слов в виде числа 
    y_proba_example = [[0 for j in range(link_proba.shape[1])] for i in range(link_proba.shape[0])]
    
    # В будущем массив массивов слов в двоичном виде
    y_proba_test = [[['0' for j in range(link_proba.shape[2])] for i in range(link_proba.shape[1])] 
                    for i in range(link_proba.shape[0])]
    
    
    for i in range(len(link_proba)):
        for j in range(len(link_proba[i])):
            for c in range(len(link_proba[i][j])):
                y_proba_test[i][j][c] = '1' if link_proba[i][j][c] > minimum else '0'
            y_proba_example[i][j] = int("".join(y_proba_test[i][j]), 2)
            
    urls = create_links(link, y_proba_example)
    
    
    # Сохраение всех ссылок в txt файле с текущеё данной
    d = datetime.date.today().strftime("%Y-%m-%d")
    indexDf = df.shape[0] - 1
    domain = df.loc[indexDf,'domain']
    file = f"generated_links_{domain}_{d}.txt"
    with open(file, "w") as file:
        for line in urls:
            file.write(line + '\n')
            
    return urls


# In[27]:


l = DictionaryGeneration('data_with_e1_2022-05-15.pickle', "https://www.e1.ru/text/health/2021/09/09/70127297/")


# In[28]:


print(l)


# In[ ]:




