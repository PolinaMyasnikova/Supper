#!/usr/bin/env python
# coding: utf-8

# Основной модуль, в котором происходит сбор ссылок, обновление базы данных и генерирование ссылок 



import pandas as pd

from FuncParsing import ParsingSite
from CompleteData import UpdateData
from DictionaryGeneration import DictionaryGeneration

# In[6]:


site = 'https://www.e1.ru/text/health/2021/09/09/70127297/'


print("Сбор ссылок")
file_links = ParsingSite(site)
print("Сбор ссылок завершён")
file_data = UpdateData(site, file_links)
print("Обучение модели")
l = DictionaryGeneration(file_data, 'https://www.e1.ru/text/health/2021/09/09/70127297/')


print(l)




