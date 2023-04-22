from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
data = []
url = 'https://www.trismegistos.org/coll/list_all.php'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'lxml')
main_div=soup.find_all('table', cellpadding="0", cellspacing="0", border="0")
Col_ids=main_div[1].find_all_next('td',width="100")
f=open("allcollections.txt","w")
i=0
for strings in Col_ids:
    i+=1
    f = open("allcollections.txt", "a")
    f.write(strings.text+',')
    f.close()

print(str(i))