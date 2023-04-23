import concurrent.futures
import threading
import time

from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

Number_Of_Pages = 0
Rows_global = 0


def scrape(collections_id, start_page=1):
    counter = 0
    data = []

    Rows = 0
    data = []
    url = f'https://www.trismegistos.org/coll/detail.php?coll_id={collections_id}&charttype=1&language=&material=&p=1'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    Number_Of_Pages = 0
    try:
        Number_Of_Pages = int(soup.find('span', style="padding: 0 6px 0 3px").text.replace('Page 1 of ', ''))
    except:
        Number_Of_Pages = 0
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
            Rows += 1

            TMnumber_Html = item.find('td', class_='TM_id')
            Collection_Html = item.find('td', class_='mus')
            Material_Html = item.find('td', class_='mat')
            Language_Html = item.find('td', class_='lang')
            Century_Html = item.find('td', class_='cent')
            Publications = item.find('td', class_='publ')

            print("main data scraped")
            time.sleep(1)
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
                TM_number_Url_Data_Auth_Text = TM_number_Url_soup.find('p', id="authors-works")
                TM_number_Url_Data_arch = TM_number_Url_div.find('div', id="text-arch").text.replace('Archive',
                                                                                                     '') if TM_number_Url_div.find(
                    'div', id="text-arch") else None
                culture = ''
                TM_number_publ_html = TM_number_Url_div.find('div', id="text-publs", class_="text-info")
                publs = TM_number_publ_html.find_all_next('p')
                TM_number_publ = ''
                for publ in publs:
                    if publ.text.find('Select') != -1 or publ.text.find('subscribe') != -1 or publ.text.find(
                            'Trismegistos') != -1 or publ.text.find('currently') != -1:
                        pass
                    else:
                        TM_number_publ += publ.text

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
                    TM_number_Url_Data_div_Text = (TM_number_Url_Data_div[item].text.replace('Date:', ''))
                for string in TM_number_Url_Data_p_Text:
                    if 'Culture & genre:' in string:
                        culture = string.replace('Culture & genre:', '')

            except:
                print("failed")

            New_data = []
            New_data_name = []

            for string in TM_number_Url_Data_p_Text:
                i = 0  # loop through each string in the original list
                for word in words_to_remove:  # loop through each word to remove
                    if word in string:
                        if i > 1:
                            break
                        i += 1

                        string = string.replace(word, '')  # remove the word from the string
                        for data_number in range(len(words_to_remove)):
                            try:
                                if (word == words_to_remove[data_number]):
                                    New_data.append(string)
                                    New_data_name.append(word)
                            except:
                                pass
            data.append({
                'TM Link': TM_number_Url,
                'TM number': TMnumber_Html.text if TMnumber_Html else None,
                'Collection': Collection_Html.text if Collection_Html else None,
                'Material': Material_Html.text if Material_Html else None,
                'Language': Language_Html.text if Language_Html else None,
                'Century': Century_Html.text if Century_Html else None,
                'Publication': Publications.text if Publications.text else None,
                'Date': TM_number_Url_Data_div_Text if TM_number_Url_Data_div_Text else None,
                'Authors / works:': TM_number_Url_Data_Auth_Text.text.replace('Authors / works:',
                                                                              '') if TM_number_Url_Data_Auth_Text else None,
                words_to_remove[0]: None,
                words_to_remove[1]: None,
                words_to_remove[2]: None,
                'Culture & genre:': culture if culture else None,
                'Archive': TM_number_Url_Data_arch,
                'MetaData Publications': TM_number_publ if TM_number_publ else None

            })

            for i in range(len(New_data)):
                if words_to_remove[i] == New_data_name[i]:
                    data[Rows - 1][words_to_remove[i]] = New_data[i]

    return data


def save(scrapped, file_name):
    df = pd.DataFrame(scrapped)

    desktop_path = os.path.expanduser("~/Desktop/collections")

    file_path = os.path.join(desktop_path, f'{file_name}.xlsx')
    df.to_excel(file_path, index=False)
    print(f"Excel file saved to: {file_path}")

done_collections=[]
with open('missingfiles.txt') as f:
    data = f.read()
    all_collections = data.split(',')


print(all_collections)

words_to_remove = ["Provenance:", "Content (beta!):", "Recto/Verso:"]


def scrape_and_save(Collection_id):
    print(f'starting collection {Collection_id}')
    data = scrape(int(Collection_id))
    save(data, f'collection {Collection_id}')
    time.sleep(1)

failed_collections = []

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    # Queue up tasks for each collection ID

    futures = [executor.submit(scrape_and_save, Collection_id) for Collection_id in all_collections]

    # Wait for all tasks to complete
    for future in concurrent.futures.as_completed(futures):
        try:
            result = future.result()


        except Exception as e:
            print(f'Error occurred: {str(e)}')


            # Write failed collections to file


