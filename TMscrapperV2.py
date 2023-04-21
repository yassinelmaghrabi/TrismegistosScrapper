
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

Number_Of_Pages = 0
Rows_global=0


def scrape(collections_id, start_page=1):
    counter = 0
    global data, TM_number_Url_Data_p_Text
    global Rows_global
    global Rows
    Rows=0
    data = []
    url = f'https://www.trismegistos.org/coll/detail.php?coll_id={collections_id}&charttype=1&language=&material=&p=1'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    global Number_Of_Pages
    try:
        Number_Of_Pages = int(soup.find('span', style="padding: 0 6px 0 3px").text.replace('Page 1 of ', ''))
    except:
        Number_Of_Pages=0
    Number_Of_Pages += 1
    print(str(Number_Of_Pages) + ' pages')
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
            Rows+=1
            Rows_global+=1
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
                TM_number_Url_Data_Auth_Text = TM_number_Url_soup.find('p',id="authors-works")
                TM_number_Url_Data_arch = TM_number_Url_div.find('div',id="text-arch").text.replace('Archive','') if TM_number_Url_div.find('div',id="text-arch") else None
                culture=''







                for item in range(len(TM_number_Url_Data_p)):
                    TM_number_Url_Data_p_Text.append(f'{TM_number_Url_Data_p[item].text}')

                for item in range(len(TM_number_Url_Data_a)):
                    if TM_number_Url_Data_a[item].text.find('Select') != -1 or TM_number_Url_Data_a[item].text.find(
                            'do not') != -1:
                        break
                    TM_number_Url_Data_a_Text.append(TM_number_Url_Data_a[item].text)
                for item in range(len(TM_number_Url_Data_div)):
                    if TM_number_Url_Data_div[item].text.find('Select') != -1 or TM_number_Url_Data_div[item].text.find(
                            'do not') != -1:
                        break
                    TM_number_Url_Data_div_Text=(TM_number_Url_Data_div[item].text.replace('Date:', ''))
                for string in TM_number_Url_Data_p_Text:
                    if 'Culture & genre:' in string:
                        culture=string.replace('Culture & genre:','')










            except:
                print("failed")

            New_data = []
            New_data_name = []

            for string in TM_number_Url_Data_p_Text:  # loop through each string in the original list
                for word in words_to_remove:  # loop through each word to remove
                    if word in string:

                        string = string.replace(word, '')  # remove the word from the string
                        for data_number in range(len(words_to_remove)):
                            if (word == words_to_remove[data_number]):
                                New_data.append(string)
                                New_data_name.append(word)
            data.append({
                'TM Link': TM_number_Url,
                'TM number': TMnumber_Html.text if TMnumber_Html else None,
                'Collection': Collection_Html.text if Collection_Html else None,
                'Material': Material_Html.text if Material_Html else None,
                'Language': Language_Html.text if Language_Html else None,
                'Century': Century_Html.text if Century_Html else None,
                'Publication': Publication_Html.text if Publication_Html else None,
                'Date': TM_number_Url_Data_div_Text if TM_number_Url_Data_div_Text else None,
                'Authors / works:': TM_number_Url_Data_Auth_Text.text.replace('Authors / works:','') if TM_number_Url_Data_Auth_Text else None,
                words_to_remove[0]: None,
                words_to_remove[1]: None,
                words_to_remove[2]: None,
                'Culture & genre:': culture if culture else None,
                'Archive': TM_number_Url_Data_arch



            })


            for i in range(len(New_data)):
                if words_to_remove[i]==New_data_name[i]:
                    data[Rows-1][words_to_remove[i]]=New_data[i]




    return data





def save(scrapped, file_name):
    df = pd.DataFrame(scrapped)

    desktop_path = os.path.expanduser("~/Desktop")

    file_path = os.path.join(desktop_path, f'{file_name}.xlsx')
    df.to_excel(file_path, index=False)
    print(f"Excel file saved to: {file_path}")


collections = [4150,903,5,1540,1434,1125,1213,1547,1388,434,540,1352,1046,1589,1317,1206,1301,1302,1377,1308,849,1559,1224,915,13,1405,857,1753,3851,1601,392,69,3858,3703,70,71,3610,72,3934,73,1149,4356,3696,74,1408,75,76,403,3628,1323,3753,4382,527,1173,542,485,1223,1085,1596,1036,1899,484,1222,648,1337,1453,1154,77,1701,1446,950,1901,4353,649,78,825,4344,432,3634,3924,1795,1175,1288,3837,1170,1164,1186,1331,1752,916,4082,1185,600,1711,1073,4270,1518,216,3311,1333,1182,3850,1168,3840,307,811,451,4464,1523, 4078,
]

words_to_remove = ["Provenance:", "Content (beta!):", "Recto/Verso:",'Culture']
for Collection_id in collections:
    print(f'starting collection {Collection_id}')
    save(scrape(Collection_id), f'collection {Collection_id}')
