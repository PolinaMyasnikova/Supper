#!/usr/bin/env python
# coding: utf-8

# Функция, считывающая все ссылки со страницы 

# In[1]:


from bs4 import BeautifulSoup
import urllib.request
import pickle
import datetime


# In[2]:


# Минимальное кол-во ссылок, которое надо набрать
n = 1000

def ParsingSite(site):
    def CorrectLink(domain, newL):
        """Проверка ссылки"""
        if (len(newL) <= 1):
            return False
        if newL[0] != 'h' and newL[0] != '/':
            return False
        if len(newL) > 1:
            if newL[0] == 'h' or newL[1] == '/':
                if domain not in newL.split('/')[2].split('.'):
                    return False
        return True
    
    def NewEditedLink(link):
        """Корректирует записываемую ссылку"""
        if link[0] == '/':
            if link[1] == '/':
                return "https:" + link
            else:
                return "https://www.e1.ru" + link
        else:
            return link
            
    # Вычленение домена
    domain = site.split('/')[2].split('.')[-2]
    
    # Считывает html разметку и преобразовать разметку в дерево синтаксического разбора. 
    resp = urllib.request.urlopen(site)
    soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'))
    
    # Будущий лист ссылок 
    linksList = []
    
    # Находит все ссылки и добавляетв в лист всех ссылок
    for link in soup.find_all('a', href=True):
        newL = link['href']
        if CorrectLink(domain, newL):
            linksList.append(NewEditedLink(newL))
            
    # Убирает повторения 
    links = set(linksList)
    
    # Лист с ссылками, по которым надо пройти 
    LinksForP = list(links)
    
    # В будущем будет хранить ссылки, которые были найдены, но не добавленны в основной лист ссылок
    newLinks = {}
    
    # Цикл, который повторяется, пока не набранно n (1000) кол-во ссылок
    while len(links) < n:
        # В будущем будет хранить ссылки, которые надо добавить в лист на прохождение
        linksForPNext = []
        
        # Переходит на новый сеттевой ресурс и считывает ссылки с него
        for link in LinksForP:
            linksForAdd = []
            if len(link) == 0: 
                continue
            try:
                resp = urllib.request.urlopen(link)
            except: 
                continue
            soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'))
            for link in soup.find_all('a', href=True):
                newL = link['href']
                if CorrectLink(domain, newL):
                    linksForAdd.append(NewEditedLink(newL))
                    
            # Вычленяет только те ссылки, которых нет в основном листе
            newLinks = set(linksForAdd) - links
            
            # Если были найденны новые ссылки, приводит их к корректному виду и записывает в лист ссылок
            if len(newLinks) != 0:
                links.update(newLinks)
                linksForPNext.extend(linksForAdd)
                #print(len(links))
                
            # Проверка на кол-во ссылок (Если набранно нужно кол-во выходит из цикла)
            if len(links) >= n:
                #print("Собранно нужное количество")
                break
        # Если новых ссылок больше не было найденно, но кол-во ещё меньше n, выходит из цикла
        if linksForPNext:
            #print('Больше нет новых ссылок')
            break
        # Обновляет лист ссылок для прохождения теми, на которых функия ещё не была
        LinksForP[:] = linksForPNext
        
    #создаёт файл ссылок с текущей датой
    d = datetime.date.today().strftime("%Y-%m-%d")
    file = f"links_{domain}_{d}.pickle"
    with open(file, 'wb') as f:
        pickle.dump(links, f)
    return file
    


# In[5]:


#name = ParsingSite("https://www.e1.ru/text/health/2021/09/09/70127297/")


# In[6]:


#name


# In[7]:


#with open(name, 'rb') as f:
#    links = pickle.load(f)


# In[8]:


#links


# In[ ]:




