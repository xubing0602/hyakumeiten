from bs4 import BeautifulSoup
import requests
import pandas as pd
import urllib.request
import json
import pandas as pd
import time

from config import *
df_res = pd.read_csv(HYAKUMEITEN_OUTPUT_PATH)[['name', 'tabelog_site', 'lat', 'lng', 'address_region', 'main_genre', 'genre', 'price_range', 'rating_users', 'rating', 'image']]
df_res = df_res.rename(columns={'tabelog_site': 'url'})
# df_res = df_res[df_res.address_region != '東京都' ]
res_json = df_res.to_json(orient='records')


with open('../template_v2.html','r') as file:
    filedata = file.read()
    filedata = filedata.replace('{{restaurants}}', res_json)


with open('../index.html','w') as file:
    file.write(filedata)

