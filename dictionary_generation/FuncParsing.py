from bs4 import BeautifulSoup
import urllib.request
import pickle
import datetime


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


def NewEditedLink(link, domain):
    """Корректирует записываемую ссылку"""
    if link[0] == '/':
        if link[1] == '/':
            return "https:" + link
        else:
            return f"https://{domain}" + link
    else:
        return link


def ParsingSite(site):
    """Фрмирование списка ссылок с данного сайта"""

    # Минимальное кол-во ссылок, которое надо набрать
    n = 1000

    # Вычленение домена
    all_domain = site.split('/')[2]
    domain = site.split('/')[2].split('.')[-2]
    
    # Считывает html разметку и преобразовать разметку в дерево синтаксического разбора. 
    resp = urllib.request.urlopen(site)
    soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'), features="html.parser")
    
    # Будущий лист ссылок 
    linksList = []
    
    # Находит все ссылки и добавляетв в лист всех ссылок
    for link in soup.find_all('a', href=True):
        newL = link['href']
        if CorrectLink(domain, newL):
            linksList.append(NewEditedLink(newL, all_domain))
            
    # Убирает повторения 
    links = set(linksList)
    
    # Лист с ссылками, по которым надо пройти 
    LinksForP = list(links)
    
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
            soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'), features="html.parser")
            for link in soup.find_all('a', href=True):
                newL = link['href']
                if CorrectLink(domain, newL):
                    linksForAdd.append(NewEditedLink(newL, all_domain))
                    
            # Вычленяет только те ссылки, которых нет в основном листе
            newLinks = set(linksForAdd) - links
            
            # Если были найденны новые ссылки, приводит их к корректному виду и записывает в лист ссылок
            if len(newLinks) != 0:
                links.update(newLinks)
                linksForPNext.extend(linksForAdd)
                
            # Проверка на кол-во ссылок (Если набранно нужно кол-во выходит из цикла)
            if len(links) >= n:
                break
        # Если новых ссылок больше не было найденно, но кол-во ещё меньше n, выходит из цикла
        if linksForPNext:
            break
        # Обновляет лист ссылок для прохождения теми, на которых функия ещё не была
        LinksForP[:] = linksForPNext
        
    # Создаёт файл ссылок с текущей датой
    d = datetime.date.today().strftime("%Y-%m-%d")
    file = f"links_{domain}_{d}.pickle"
    with open(file, 'wb') as f:
        pickle.dump(links, f)
    return file


def main():
    name = ParsingSite("https://www.e1.ru/text/health/2021/09/09/70127297/")
    with open(name, 'rb') as f:
        links = pickle.load(f)
    print("Первые десять ссылок")
    print(list(links)[:10])


if __name__ == "__main__":
    main()
