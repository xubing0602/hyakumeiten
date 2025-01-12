from bs4 import BeautifulSoup
import requests
import pandas as pd
import urllib.request
import json
import pandas as pd
import time
from config import *

data = requests.get(hyakumeiten_main_site)
soup = BeautifulSoup(data.content, 'html.parser')


def generate_sub_site_res_list(sub_site_list, start, end):
    total_res_list = []
    for sub_site in sub_site_list[start:end]:
        sub_site_full = award_main_site + sub_site
        print(sub_site_full)
        data = requests.get(sub_site_full)
        soup = BeautifulSoup(data.content, 'html.parser')
        res_site_list = soup.find_all('a', {'class': ['hyakumeiten-shop__target']})
        res_site_list = [res_site.attrs['href']  for res_site in res_site_list if res_site.has_attr('href')]
        print(len(res_site_list))
        total_res_list.append(res_site_list)
        time.sleep(1)
    return total_res_list

def generate_top_sub_site_res_list(start, end, ranking_main_site = ranking_main_site, ranking_suffix = ranking_suffix):
    total_res_list = []
    for i in range(start, end):
        ranking_site = ranking_main_site + str(i) + ranking_suffix
        print(ranking_site)
        data = requests.get(ranking_site)
        soup = BeautifulSoup(data.content, 'html.parser')
        sub_site_list = soup.find_all('a', {'class': ['list-rst__rst-name-target']})
        sub_site_list = [sub_site.attrs['href'] for sub_site in sub_site_list if sub_site.has_attr('href')]
        print(len(sub_site_list))
        total_res_list.append(sub_site_list)
        time.sleep(1)
    return total_res_list

def generate_res_details(total_res_list, col_list = col_list):
    df = pd.DataFrame(columns=col_list)
    for a in range(len(total_res_list)):
        print("List {}".format(a))
        tabelog_site_list = total_res_list[a]
        for tabelog_site in tabelog_site_list:
            try:
                restaurant_name = ''
                name_alias = ''
                add_region = ''
                add_locality = ''
                add_street = ''
                genre = ''
                main_genre = ''
                rating_count = ''
                rating_value = ''
                save_count = ''
                transit_plan = ''
                opening_hours = ''
                closed_dates = ''
                payment_method = ''
                dinner_budget = ''
                lunch_budget = ''
                dinner_budget_review = ''
                lunch_budget_review = '' 
                no_of_seats = ''
                official_website = ''
                social_account = ''
                opening_date = ''
                remarks = ''
                branches = ''
                award_medal_list = []
                award_selection_list = []  
                award_medal_text = ''
                award_selection_text = ''
                award_kamiawa = ''
                reservation_status = ''
                closest_station = ''
                lat = ''
                lng = ''
                image = ''
                name = ''
                price_range = ''
                data = requests.get(tabelog_site)
                soup = BeautifulSoup(data.content, 'html.parser')
                info_js = json.loads(soup.find_all('script', type="application/ld+json")[0].text.strip())
                ## name related
                restaurant_name = name = info_js['name']
                # soup.find('div', {"class": "rdheader-rstname"}).find('h2', {'class': "display-name"}).find('span').text.strip()
                # info_js['priceRange']
                name_alias = soup.find('div', {"class": "rdheader-rstname"}).find('span', {'class': "alias"}).text
                restaurant_name = restaurant_name + name_alias
                print(restaurant_name)
                price_range = info_js['priceRange']
                ## address related
                add_region = info_js['address']['addressRegion']
                add_locality = info_js['address']['addressLocality']
                add_street = info_js['address']['streetAddress']
                lat = info_js['geo']['latitude']
                lng = info_js['geo']['longitude']
                image = info_js['image']
                try:
                    closest_station = soup.find('dl', {'class': "rdheader-subinfo__item rdheader-subinfo__item--station"})\
                        .find('div', {'class':'linktree__parent'})\
                        .text.strip()
                except:
                    pass
                try: 
                    closed_dates = soup.find('dd', {'class': "rdheader-subinfo__closed-text"})\
                        .text.strip()
                except:
                    pass
                ## genre and ratings
                genre = info_js['servesCuisine']
                main_genre = genre.split("、")[0]
                rating_count = info_js['aggregateRating']['ratingCount']
                rating_value =info_js['aggregateRating']['ratingValue']
                save_count = soup.find('span', {'class': "rdheader-rating__hozon-target"}).find('em', {'class': "num"}).text
                # budget_info_list = soup.find('div', {"class":"rstinfo-table__budget"}).find_all("p", {'class': 'rstinfo-table__budget-item'})
                # for i in range(len(budget_info_list)):
                #     if budget_info_list[i].find('i')['aria-label'] == 'Dinner':
                #         dinner_budget = budget_info_list[i].text.strip()
                #     if budget_info_list[i].find('i')['aria-label'] == 'Lunch':
                #         lunch_budget = budget_info_list[i].text.strip()
                ## award       
                award_list = soup.find_all("div", {'class': ['rstinfo-table-badge-award__tooltip-wrap', 'rstinfo-table-badge-hyakumeiten__tooltip-wrap']})
                for i in range(len(award_list)):
                    award_text = award_list[i].text.strip()
                    if "受賞店" in award_text:
                        award_medal_list.append(award_text)
                    if "選出店" in award_text:
                        award_selection_list.append(award_text)
                try:
                    restaurant_ranking = soup.find('div', {'class': 'rdheader-rstname-wrap'}).find('img').attrs['alt']
                    award_medal_list.append(restaurant_ranking)
                except:
                    pass
                award_medal_text = ', '.join(award_medal_list)
                award_selection_text = ', '.join(award_selection_list)
                try:
                    award_kamiawa = soup.find("div", {'class': 'rdheader-certification-label__target'}).text.strip()
                except:
                    pass
                try:
                    reservation_status = soup.find("p", {'class': 'rstinfo-table__reserve-status'}).text.strip()
                except:
                    pass
                ## other info
                table_list = soup.find_all('table', {'class': 'c-table c-table--form rstinfo-table__table'})
                for i in range(len(table_list)):
                    info_table_list = table_list[i].find_all('tr')
                    for j in range(len(info_table_list)):
                        table_header = info_table_list[j].find('th').text.strip()
                        table_text = info_table_list[j].find('td').text.strip()
                        if table_header == '交通手段':
                            transit_plan = table_text
                        if table_header == "営業時間":
                            opening_hours = table_text
                        if table_header == "支払い方法":
                            payment_method = table_text
                        if table_header == "予算":
                            budget_info_list = info_table_list[j].find('td').find_all("p", {'class': 'rstinfo-table__budget-item'})
                            for k in range(len(budget_info_list)):
                                if budget_info_list[k].find('i')['aria-label'] == 'Dinner':
                                    dinner_budget = budget_info_list[i].text.strip()
                                if budget_info_list[k].find('i')['aria-label'] == 'Lunch':
                                    lunch_budget = budget_info_list[i].text.strip()
                        if table_header == "予算（口コミ集計）":
                            budget_info_list = info_table_list[j].find('td').find_all("span", {'class': 'rstinfo-table__budget-item'})
                            for k in range(len(budget_info_list)):
                                if budget_info_list[k].find('i')['aria-label'] == 'Dinner':
                                    dinner_budget_review = budget_info_list[i].text.strip()
                                if budget_info_list[k].find('i')['aria-label'] == 'Lunch':
                                    lunch_budget_review = budget_info_list[i].text.strip()
                        if table_header == "席数":
                            no_of_seats = table_text
                        if table_header == 'ホームページ':
                            official_website = table_text
                        if table_header == '公式アカウント':
                            social_account = table_text
                        if table_header == 'オープン日':
                            opening_date = table_text
                        if table_header == '備考':
                            remarks = table_text
                        if table_header == '関連店舗情報':
                            branches = 'tabelog.com' + info_table_list[j].find('a').attrs['href']
                result_list = [restaurant_name, rating_value, main_genre, add_region, add_locality, add_street, closest_station,
                        rating_count, save_count, 
                        lunch_budget, dinner_budget, lunch_budget_review, dinner_budget_review,
                        award_medal_text, award_selection_text, award_kamiawa, genre,
                        transit_plan, closed_dates, opening_hours, reservation_status, payment_method, no_of_seats,
                        official_website, social_account, opening_date, remarks, branches, tabelog_site, lat, lng, image, name, price_range]
                df.loc[len(df)] = result_list
            except:
                return df
        time.sleep(10)
    return df