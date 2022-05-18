import pandas as pd
import pickle
import os.path


def CreateData(file):
    """Формирования базы данных"""

    # Проверка на нахождени файла для обработки не будет найден
    if not os.path.exists(file):
        print(f"Файл под именем {file} не был найен.")
        pass

    # Импорт списка ссылок 
    with open(file, 'r', encoding='utf-8') as f:
        texts = f.read()
    # Формирование из текста список ссылок     
    links = texts.split('\n')

    # Создание таблицы
    df = pd.DataFrame(columns=['domain', 'dictionary'])

    # Заполнение полей в таблице
    for i in links:
        if "http" not in i:
            continue
        link = i.split('/')
        entire_domain = link[2].split('.')
        if 'com' in entire_domain:
            index_domain = entire_domain.index('com') - 1
        else:
            index_domain = len(entire_domain) - 2
        if len(df.loc[df['domain'] == entire_domain[index_domain]]) != 0:
            index = df.loc[df['domain'] == entire_domain[index_domain]].index[0]
            df.loc[index, 'dictionary'].extend(link[3:])
        else:
            new_row = pd.DataFrame({'domain': entire_domain[index_domain], 'dictionary': [link[3:]]})
            df = pd.concat([df, new_row], ignore_index=True)

    # id строк с пустым dictionary
    idRowsDelet = []

    # Список всех слов
    words = []

    # В цикле собирается лист words, а так же записываются id с пустым dictionary
    for index in range(df.shape[0]):
        df.loc[index, 'dictionary'] = list(filter(lambda x: x != "", df.loc[index, 'dictionary']))
        if not df.loc[index, 'dictionary']:
            idRowsDelet.append(index)
        words.extend(df.loc[index, 'dictionary'])

        # Удаление строк с пустым dictionary
    for i in idRowsDelet:
        df.drop(labels=[i], axis=0, inplace=True)

    # Обновить id
    df = df.reset_index(drop=True)

    # Создётся или перезаписывается файл data.pickle
    with open('data.pickle', 'wb') as f:
        pickle.dump(df, f)
        pickle.dump(words, f)


def main():
    CreateData('links.txt')


if __name__ == "__main__":
    main()
