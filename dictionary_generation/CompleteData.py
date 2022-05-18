import pandas as pd
import pickle
import datetime


def UpdateData(nameSite, fileLinks):
    
    # Домен сайта 
    domain = nameSite.split('/')[2].split('.')[-2]
    
    # Импорт
    with open(fileLinks, 'rb') as f:
        linksAfterParsing = pickle.load(f)  # собранных ссылок
        
    with open('data.pickle', 'rb') as f:
        df = pickle.load(f)  # базы данных
        words = pickle.load(f)  # список всевозможных токенов
         
    # Разделение ссылки сайта на состовнные части    
    nameSiteSplit = nameSite.split('/')
    
    # Формирования нового столбца с текущим доменом в базе данных
    new_row = pd.DataFrame({'domain': [nameSiteSplit[2].split('.')[-2]], 
                            'dictionary': [nameSiteSplit[3:] if len(nameSiteSplit) > 3 else []]})
    df = pd.concat([df, new_row], ignore_index=True)
    
    # id столбца с текущим доменом
    idDomain = df.loc[df['domain'] == nameSiteSplit[2].split('.')[-2]].index[0]
    
    # Заполнение массива токеонов по текущему домену
    for linkParsing in linksAfterParsing:
        link = linkParsing.split('/')[3:]
        df.loc[idDomain,'dictionary'].extend(link)
    
    # Избавления от пустых элементов в массиве токенов
    df.loc[df.shape[0]-1,'dictionary'] = list(filter(lambda x: x != "", df.loc[df.shape[0]-1,'dictionary']))
    
    # Добавление в списку всех токенов, токенов текущего домена
    words.extend(df.loc[df.shape[0]-1,'dictionary'])
    
    # Сохранение файла с обновлённо базо данных и списка всех токенов с текущей датой
    d = datetime.date.today().strftime("%Y-%m-%d")
    file = f"data_with_{domain}_{d}.pickle"
    with open(file, 'wb') as f:
        pickle.dump(df, f)
        pickle.dump(words, f)
    return file


def main():
    name = UpdateData("https://www.e1.ru/text/health/2021/09/09/70127297/", "links_e1_2022-05-11.pickle")
    with open(name, 'rb') as f:
        df = pickle.load(f)
        words = pickle.load(f)
    print(df)
    print(words[:20])


if __name__ == "__main__":
    main()
