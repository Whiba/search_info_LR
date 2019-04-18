# -*- coding: utf-8 -*-
import requests
import bs4
import re
import json
import pymorphy2
import time

def get_all_links():
# ---------------------------- Шаг 1. Получение первичных данных с сайта
    url_main = 'https://radiokot.ru/'
    main_links = []
    all_links = []

    try:
        f = open('links.txt', 'r')
    except IOError as e:
        #print(u'не удалось открыть файл links.txt')
        # получение списка ссылок из главной страницы
        main_page = requests.get(url_main)
        main_page.encoding = 'utf-8'
        pars_of_main_page = bs4.BeautifulSoup(main_page.text, 'html.parser')
        for mp_part in pars_of_main_page.find_all('a', 'mmenu'):
            #print(mp_part)
            ref = mp_part.get('href')
            main_links.append(url_main + ref + '')

        # loop по полученным ссылкам и заполнение вторичных массивов
        for link in main_links:
            #print('----------------------' + link)
            curr_page = requests.get(link)
            curr_page.encoding = 'utf-8'
            pars_curr_page = bs4.BeautifulSoup(curr_page.text, 'html.parser')
            for page_part in pars_curr_page.find_all('a', 'ChapterMenu'):
                l = url_main + page_part.get('href')
                t = page_part.getText()
                all_links.append([l, t])
            for page_spart in pars_curr_page.find_all('a', 'ChapterSubMenu'):
                sl = url_main + page_spart.get('href')
                st = page_spart.getText()
                all_links.append([sl, st])
            for page_spart in pars_curr_page.find_all('a', 'forumlink'):
                sl = link + '/' + re.sub(r"[&]", "", page_spart.get('href')[2:20])
                st = page_spart.getText()
                all_links.append([sl, st])
                inside_page = requests.get(sl)
                inside_page.encoding = 'utf-8'
                pars_inside_page = bs4.BeautifulSoup(inside_page.text, 'html.parser')
                for page_spart in pars_inside_page.find_all('a', 'topictitle'):
                    sl = link + '/' + page_spart.get('href')[2:].split('&sid')[0]
                    #print('-------------------------------------------' + sl)
                    st = page_spart.getText()
                    all_links.append([sl, st])

        # запись полученных ссылок в файл
        f = open('links.txt', 'w')
        json.dump(all_links, f)
    else:
        with f:
            #print(u'делаем что-то с файлом links.txt')
            all_links = json.load(f)
    finally:
        f.close()
    return all_links

def get_text_for_links(all_links):
# ---------------------------- Шаг 2. Получение текстового соответствия для данных
    links_data = []
    vocabular = []
    morph = pymorphy2.MorphAnalyzer()

    for link in all_links:
        if link != '':
            text_hdr = ''
            text_usual = ''
            text_tag = ''
            my_link = link[0]
            link_text = link[1]
            #print('--------------------------' + my_link)
            curr_page = requests.get(my_link)
            curr_page.encoding = 'utf-8'
            pars_curr_page = bs4.BeautifulSoup(curr_page.text, 'html.parser')
            for page_part in pars_curr_page.find_all('p', 'ArticleHdr'):
                text_hdr = page_part.getText() + ' ' + text_hdr
            for page_part in pars_curr_page.find_all('a', 'titles'):
                text_hdr = page_part.getText() + ' ' + text_hdr
            for page_part in pars_curr_page.find_all('p', 'Usual'):
                text_usual = page_part.getText() + ' ' + text_usual
            for page_part in pars_curr_page.find_all('div', 'postbody'):
                text_usual = page_part.getText() + ' ' + text_usual
            for page_part in pars_curr_page.find_all('span', id='tagline'):
                text_tag = page_part.getText() + ' ' + text_tag
            links_data.append([my_link, link_text, [text_hdr, 10], [text_tag, 7], [text_usual, 4]])
        time.sleep(15)
    print(links_data)
    f = open('links_data.txt', 'w')
    json.dump(links_data, f)
    f.close()

    f = open('links_data.txt', 'r')
    links_data = json.load(f)
    f.close()

    for item in links_data:
        words_list = []
        temp = []
        for part in item[2:5]:
            text = part[0]
            weight = part[1]
            if (text != ''):
                for i in [',', '.', ':', ';', '!', '?', '-', '—', '(', ')', '«', '»']:
                    text = text.replace(i, ' ')
                mylist = text.split();
                for word in mylist:
                    #myword = word.decode('utf-8')
                    myword = word
                    p = morph.parse(myword)[0];
                    if ('NOUN' in p.tag) == True or ('VERB' in p.tag) == True or ('ADJF' in p.tag) == True:
                        norm_word = p.normal_form
                        words_list.append([norm_word, weight])
        words_list.sort()
        for el in words_list:
            if el not in temp:
                temp.append(el)
            else:
                for t in temp:
                    if t[0] == el[0]:
                        t[1] = t[1] + el[1]
        vocabular.append([item[0], item[1], temp])
    f = open('links_text.txt', 'w')
    json.dump(vocabular, f)
    f.close()
    return vocabular

def cleaning(data):
    temp_data = []
    flag = False
    stop_words = [
                    'быть',
                    'есть',
                    'этот',
                    'его',
                    'её',
                    'наш',
                    'весь',
                    'тот',
                    'такой',
                    'являться',
                    'идти',
                    'какой',
                    'каждый',
                    'который',
                    'мочь',
                    'ваш',
                 ]

    for item in data:
        #print('--' + item[0])
        temp_words = []
        words_mas = item[2]

        if not(item[0] == 'https://radiokot.ru/' and words_mas == []):
            for word in words_mas:
                if word[0] not in stop_words and not([s for s in word[0] if s in '123456789&=+']):
                    for t in temp_words:
                        if t[0] == word[0]:
                            t[1] = t[1] + word[1]
                            flag = True
                    if flag == False:
                        temp_words.append(word)
                    flag = False
            temp_data.append([item[0], item[1], temp_words])

    f = open('clear_links_text.txt', 'w')
    json.dump(temp_data, f)
    f.close()
    return temp_data

if __name__ == '__main__':
    web_links = []
    data = []
    data_clean = []
    result = []
    normal_search = []
    search = 'индикатор звуковых сигналов'
    morph = pymorphy2.MorphAnalyzer()

    try:
        f = open('clear_links_text.txt', 'r')
    except IOError as e:
        # Данные с сайта еще не выгружались
        # сперва получим данные, а потом приступим к поисковым запросам
        print(u'Не удалось открыть файл clear_links_text.txt')
        web_links = get_all_links()
        data = get_text_for_links(web_links)
        data_clean = cleaning(data)
    else:
        with f:
            # Данные с сайта уже были выгружены и хранятся в файлах
            # можно сразу приступать к выполнению поискавых запросов
            print(u'Делаем что-то с файлом clear_links_text.txt')
            data_clean = json.load(f)
            f.close()

            search_mas = search.split(' ')
            for myword in search_mas:
                p = morph.parse(myword)[0]
                normal_search.append(p.normal_form)

            for item in data_clean:
                words = item[2]
                for word in words:
                    if word[0] in normal_search and word[1] > 50:
                        result.append([item[0], item[1], word])
                        break

            result.sort(key=lambda i: i[2], reverse=1)
            for r in result:
                print(r)