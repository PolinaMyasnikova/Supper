import urllib.request

from dictionary_generation.FuncParsing import ParsingSite
from dictionary_generation.CompleteData import UpdateData
from dictionary_generation.LinksGeneration import LinksGeneration


def GetDictionaryURLs(link):
    """Генерирование скрытых фрагментов URLs"""

    # Проверка на существование страницы
    try:
        urllib.request.urlopen(link)
    except:
        print("Введите рабучую ссылку")
        return ""

    print("Сбор ссылок")
    file_links = ParsingSite(link)
    print("Сбор ссылок завершён")
    file_data = UpdateData(link, file_links)
    print("Обучение модели")
    file = LinksGeneration(file_data, 'https://www.e1.ru/text/health/2021/09/09/70127297/')
    print(f"Cгенерированный словарь находится в файле {file}")
    return file


def main():
    link = 'https://www.e1.ru/text/health/2021/09/09/70127297/'
    file = GetDictionaryURLs(link)
    print(file)


if __name__ == "__main__":
    main()
