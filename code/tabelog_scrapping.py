from bs4 import BeautifulSoup
import requests
import pandas as pd
import urllib.request
import json
import pandas as pd
import time
from config import *
from utils import *



site_df = pd.read_csv(TABELOG_INPUT_PATH)
tabelog_site_list = site_df['tabelog_site'].tolist()
tabelog_site_list = [tabelog_site_list]

df = generate_res_details(tabelog_site_list)

df.to_csv(TABELOG_OUTPUT_PATH, index = False)


