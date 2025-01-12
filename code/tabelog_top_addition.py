from bs4 import BeautifulSoup
import requests
import pandas as pd
import urllib.request
import json
import pandas as pd
import time

from config import *
from utils import *

start = 1
end = 61

total_res_list = generate_top_sub_site_res_list(start, end)

df = generate_res_details(total_res_list)

df.to_csv("../output/tabelog_top_output.csv", index = False)
df.to_csv(TOP_ADDITION_PATH, index = False)