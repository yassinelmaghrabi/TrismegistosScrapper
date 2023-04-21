import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
Number_Of_Pages=0

def scrape(collections_id, start_page=1):
    counter = 0
    global data
    data = []
    url = f'https://www.trismegistos.org/coll/detail.php?coll_id={collections_id}&charttype=1&language=&material=&p=1'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    global Number_Of_Pages
    Number_Of_Pages = int(soup.find('span', style="padding: 0 6px 0 3px").text.replace('Page 1 of ',''))
    Number_Of_Pages+=1
    print(str(Number_Of_Pages)+' pages')
    for page in range(start_page, Number_Of_Pages + 1):
        url = f'https://www.trismegistos.org/coll/detail.php?coll_id={collections_id}&charttype=1&language=&material=&p={page}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')

        print("pulled page " + str(page))
        counter += 1
        progress = counter / Number_Of_Pages
        subpage_progress = 0


        for item in soup.find_all('tr')[1:]:
            subpage_progress += 1
            TMnumber_Html = item.find('td', class_='TM_id')
            Collection_Html = item.find('td', class_='mus')
            Material_Html = item.find('td', class_='mat')
            Language_Html = item.find('td', class_='lang')
            Century_Html = item.find('td', class_='cent')
            Publication_Html = item.find('td', class_='publ')
            print("main data scraped")
            TM_number_Url = 'https://www.trismegistos.org' + TMnumber_Html.a.get('href')[
                                                             2:] if TMnumber_Html and TMnumber_Html.a else None
            TM_number_Url_response = requests.get(TM_number_Url)
            TM_number_Url_soup = BeautifulSoup(TM_number_Url_response.content, 'lxml')
            print(f"pulled page {page}'s subpage number {subpage_progress}")
            try:
                TM_number_Url_div = TM_number_Url_soup.find('div', class_="row flex-row flex-space-between")
                TM_number_Url_Data_p = TM_number_Url_div.find_all_next('p')
                TM_number_Url_Data_a = TM_number_Url_div.find_all_next('a')
                TM_number_Url_Data_div = TM_number_Url_div.find_all_next('div', class_="division")
                TM_number_Url_Data_p_Text = []
                TM_number_Url_Data_a_Text = []
                TM_number_Url_Data_div_Text = []

                for item in range(len(TM_number_Url_Data_p)):
                    if TM_number_Url_Data_p[item].text.find('Select') != -1 or TM_number_Url_Data_p[item].text.find(
                            'do not') != -1:
                        break
                    TM_number_Url_Data_p_Text.append(f'{TM_number_Url_Data_p[item].text} index {item}')
                for item in range(len(TM_number_Url_Data_a)):
                    if TM_number_Url_Data_a[item].text.find('Select') != -1 or TM_number_Url_Data_a[item].text.find(
                            'do not') != -1:
                        break
                    TM_number_Url_Data_a_Text.append(TM_number_Url_Data_a[item].text)
                for item in range(len(TM_number_Url_Data_div)):
                    if TM_number_Url_Data_div[item].text.find('Select') != -1 or TM_number_Url_Data_div[item].text.find(
                            'do not') != -1:
                        break
                    TM_number_Url_Data_div_Text.append(TM_number_Url_Data_div[item].text)






            except:
                print("failed")

            for string in TM_number_Url_Data_p_Text:  # loop through each string in the original list
                for word in words_to_remove:  # loop through each word to remove
                    if word in string:

                        string = string.replace(word, '')  # remove the word from the string
                        for data_number in range(len(words_to_remove)):
                            if (word == words_to_remove[data_number]):
                                data.append({

                                    'TM Link': TM_number_Url,
                                    'TM number': TMnumber_Html.text if TMnumber_Html else None,
                                    'Collection': Collection_Html.text if Collection_Html else None,
                                    'Material': Material_Html.text if Material_Html else None,
                                    'Language': Language_Html.text if Language_Html else None,
                                    'Century': Century_Html.text if Century_Html else None,
                                    'Publication': Publication_Html.text if Publication_Html else None,
                                    f'{word}': string,

                                })


    return data

def save(scrapped, file_name):
    df = pd.DataFrame(scrapped)

    desktop_path = os.path.expanduser("~/Desktop")

    file_path = os.path.join(desktop_path, f'{file_name}.xlsx')
    df.to_excel(file_path, index=False)
    print(f"Excel file saved to: {file_path}")


collections=[5]

words_to_remove = ["Provenance:","Content (beta!):","Recto/Verso:",]
for Collection_id in collections:
    print(f'starting collection {Collection_id}')
    save(scrape(Collection_id),f'collection {Collection_id}')
