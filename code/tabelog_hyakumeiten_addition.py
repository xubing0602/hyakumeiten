from bs4 import BeautifulSoup
import requests
import pandas as pd
import urllib.request
import json
import pandas as pd
import time
from config import *
from utils import *

data = requests.get(hyakumeiten_main_site)
soup = BeautifulSoup(data.content, 'html.parser')

## generate sub url list     
sub_site_list = soup.find_all('a', {'class': hyakumeiten_genre_class_list})
sub_site_list = [sub_site.attrs['href'] for sub_site in sub_site_list]

## define start and end
start = 0
end = len(sub_site_list)

## generate restaurant list for each sub url
total_res_list = generate_sub_site_res_list(sub_site_list, start, end)


## generate details for each restaurant
df_addition = generate_res_details(total_res_list)
df_addition.to_csv(HYAKUMEITEN_ADDITION_PATH, index = False)

## combine output and addition
df_output = pd.read_csv(HYAKUMEITEN_OUTPUT_PATH)
df_output_trun = df_output[~df_output['tabelog_site'].isin(df_addition['tabelog_site'])] 
df_output = pd.concat([df_output_trun, df_addition])

df_output.to_csv(HYAKUMEITEN_OUTPUT_PATH, index = False)