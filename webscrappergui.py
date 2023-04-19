import tkinter as tk
from tkinter import ttk
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

scrappeddata = []
progress = 0


def scrape(collections_id, end_page, start_page=1):
    global progress
    counter = 0
    data = []
    for page in range(start_page, end_page + 1):
        url = f'https://www.trismegistos.org/coll/detail.php?coll_id={collections_id}&charttype=1&language=&material=&p={page}'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        print("scrapped page " + str(page))
        counter += 1
        progress = counter / end_page
        progress_bar['value'] = (progress * 100)
        root.update_idletasks()

        for item in soup.find_all('tr')[1:]:
            field0 = item.find('td', class_='TM_id')
            field1 = item.find('td', class_='TM_id')
            field2 = item.find('td', class_='mus')
            field3 = item.find('td', class_='mat')
            field4 = item.find('td', class_='lang')
            field5 = item.find('td', class_='cent')
            field6 = item.find('td', class_='publ')
            if field1 and field1.a:

                try:
                    field0_url = 'https://www.trismegistos.org' + field1.a.get('href')[2:]
                    field0_response = requests.get(field0_url)
                    field0_soup = BeautifulSoup(field0_response.content, 'lxml')
                    field0_div = field0_soup.find('div', class_='division')
                    field_div = field0_soup.find('p', class_='division')
                    field_div2 = field0_soup.find_all('p', class_='division')[1]
                    field_div3 = field0_soup.find('p', id='publ-default')
                    field7_span = field0_div.find('span', class_='semibold', string='Date:')
                    date = field7_span.find_next_sibling('a').text if field7_span else None
                    field8_span = field_div.find('span', class_='semibold', string='Provenance:')
                    provenance = field8_span.find_all_next('a')[0].text if field8_span else None
                    tooltip_texts = field8_span.find_all_next('a')[2].text if field8_span else None
                    place = field8_span.find_all_next('a')[1].text if field8_span else None
                    field9_span = field_div2.find('span', class_='semibold', string='Language/script:')
                    Language = field9_span.find_all_next('a')[0].text if field9_span else None
                    Material = field9_span.find_all_next('a')[1].text if field9_span else None
                    publisher = field_div3.text if field_div3 else None
                except:
                    print('error')
                    date = None
                    field_div2 = None
                    field0_url = None
                    date = None
                    field7_span = None
                    provenance = None
                    field8_span = None
                    place = None
                    tooltip_texts = None
                    Language = None
                    Material = None
                    publisher = None
                    pass


            else:
                field0_url = None
                date = None
                field7_span = None
                provenance = None
                field8_span = None
                place = None
                tooltip_texts = None
                Language = None
                Material = None
                publisher = None

            data.append({
                'TM Link': 'https://www.trismegistos.org' + field1.a.get('href')[2:] if field1 and field1.a else None,
                'TM number': field1.text if field1 else None,
                'Collection': field2.text if field2 else None,
                'Material': field3.text if field3 else None,
                'Language': field4.text if field4 else None,
                'Century': field5.text if field5 else None,
                'Publication': field6.text if field6 else None,
                'Date': date,
                'Provenance': provenance,
                'Place': place,
                'tooltips': tooltip_texts,
                'Language/script': Language,
                'Materialdet': Material,
                'Publisher': publisher

            })
    return data


def save(scrapped, file_name):
    df = pd.DataFrame(scrapped)

    desktop_path = os.path.expanduser("~/Desktop")

    file_path = os.path.join(desktop_path, f'{file_name}.xlsx')
    df.to_excel(file_path, index=False)
    print(f"Excel file saved to: {file_path}")


def run_example():
    collection_id = collection_id_entry.get()
    page_num = page_num_entry.get()
    file_name = file_name_entry.get()
    scrappeddata = scrape(int(collection_id), int(page_num))
    save(scrappeddata, file_name)


root = tk.Tk()
root.title("TM scrapper")

collection_id_label = tk.Label(root, text="Collection ID:")
collection_id_label.grid(column=0, row=0, padx=5, pady=5)

collection_id_entry = tk.Entry(root)
collection_id_entry.grid(column=1, row=0, padx=5, pady=5)

page_num_label = tk.Label(root, text="Page Number:")
page_num_label.grid(column=0, row=1, padx=5, pady=5)

page_num_entry = tk.Entry(root)
page_num_entry.grid(column=1, row=1, padx=5, pady=5)

file_name_label = tk.Label(root, text="File Name:")
file_name_label.grid(column=0, row=2, padx=5, pady=5)

file_name_entry = tk.Entry(root)
file_name_entry.grid(column=1, row=2, padx=5, pady=5)

run_button = tk.Button(root, text="Run", command=run_example)
run_button.grid(column=0, row=3, columnspan=2, padx=5, pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
progress_bar.grid(column=0, row=4, columnspan=2, padx=5, pady=5)

root.mainloop()
