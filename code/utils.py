from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time
import concurrent.futures
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from config import *


def get_session(max_retries=3, backoff_factor=0.3, pool_connections=100, pool_maxsize=100):
    session = requests.Session()
    retries = Retry(
        total=max_retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=pool_connections, pool_maxsize=pool_maxsize)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "hyakumeiten-scraper/1.0"})
    return session


def fetch_url(session, url, timeout=10, delay=0.3):
    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
        time.sleep(delay)
        return resp
    except Exception as e:
        print(f"Failed fetch {url}: {e}")
        return None


def generate_sub_site_res_list(sub_site_list, start, end, session=None, max_workers=8):
    if session is None:
        session = get_session()
    sub_list = sub_site_list[start:end]
    def worker(sub):
        sub_site_full = award_main_site + sub
        print(sub_site_full)
        resp = fetch_url(session, sub_site_full)
        if not resp:
            return []
        soup = BeautifulSoup(resp.content, 'html.parser')
        res_site_list = soup.find_all('a', {'class': ['hyakumeiten-shop__target']})
        res_site_list = [res_site.attrs['href'] for res_site in res_site_list if res_site.has_attr('href')]
        print(len(res_site_list))
        return res_site_list

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        results = list(ex.map(worker, sub_list))
    return results


def generate_top_sub_site_res_list(start, end, ranking_main_site=ranking_main_site, ranking_suffix=ranking_suffix, session=None, max_workers=8):
    if session is None:
        session = get_session()
    page_indices = list(range(start, end))
    def worker(i):
        ranking_site = ranking_main_site + str(i) + ranking_suffix
        print(ranking_site)
        resp = fetch_url(session, ranking_site)
        if not resp:
            return []
        soup = BeautifulSoup(resp.content, 'html.parser')
        sub_site_list = soup.find_all('a', {'class': ['list-rst__rst-name-target']})
        sub_site_list = [sub_site.attrs['href'] for sub_site in sub_site_list if sub_site.has_attr('href')]
        print(len(sub_site_list))
        return sub_site_list

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        results = list(ex.map(worker, page_indices))
    return results


def generate_res_details(total_res_list, col_list=col_list, session=None, max_workers=10):
    if session is None:
        session = get_session()

    # flatten list-of-lists to single list
    tabelog_urls = [u for sub in total_res_list for u in sub]
    records = []

    def parse_one(tabelog_site):
        try:
            resp = fetch_url(session, tabelog_site)
            if not resp:
                return None
            soup = BeautifulSoup(resp.content, 'html.parser')
            info_js = json.loads(soup.find_all('script', type="application/ld+json")[0].text.strip())

            restaurant_name = name_alias = add_region = add_locality = add_street = genre = main_genre = ''
            rating_count = rating_value = save_count = transit_plan = opening_hours = closed_dates = ''
            payment_method = dinner_budget = lunch_budget = dinner_budget_review = lunch_budget_review = ''
            no_of_seats = official_website = social_account = opening_date = remarks = branches = ''
            award_medal_list = []
            award_selection_list = []
            award_medal_text = award_selection_text = award_kamiawa = reservation_status = ''
            closest_station = lat = lng = image = name = price_range = ''

            restaurant_name = name = info_js.get('name', '')
            try:
                alias_tag = soup.find('div', {"class": "rdheader-rstname"}).find('span', {'class': "alias"})
                if alias_tag:
                    name_alias = alias_tag.text.strip()
                    restaurant_name = restaurant_name + name_alias
            except:
                pass

            price_range = info_js.get('priceRange', '')
            addr = info_js.get('address', {})
            add_region = addr.get('addressRegion', '')
            add_locality = addr.get('addressLocality', '')
            add_street = addr.get('streetAddress', '')
            geo = info_js.get('geo', {})
            lat = geo.get('latitude', '')
            lng = geo.get('longitude', '')
            image = info_js.get('image', '')

            try:
                closest_station = soup.find('dl', {'class': "rdheader-subinfo__item rdheader-subinfo__item--station"})\
                    .find('div', {'class': 'linktree__parent'}).text.strip()
            except:
                pass
            try:
                closed_dates = soup.find('dd', {'class': "rdheader-subinfo__closed-text"}).text.strip()
            except:
                pass

            genre = info_js.get('servesCuisine', '')
            main_genre = genre.split("、")[0] if genre else ''
            agg = info_js.get('aggregateRating', {})
            rating_count = agg.get('ratingCount', '')
            rating_value = agg.get('ratingValue', '')
            try:
                save_count = soup.find('span', {'class': "rdheader-rating__hozon-target"}).find('em', {'class': "num"}).text
            except:
                save_count = ''

            award_list = soup.find_all("div", {'class': ['rstinfo-table-badge-award__tooltip-wrap', 'rstinfo-table-badge-hyakumeiten__tooltip-wrap']})
            for a in award_list:
                award_text = a.text.strip()
                if "受賞店" in award_text:
                    award_medal_list.append(award_text)
                if "選出店" in award_text:
                    award_selection_list.append(award_text)
            try:
                restaurant_ranking = soup.find('div', {'class': 'rdheader-rstname-wrap'}).find('img').attrs.get('alt', '')
                if restaurant_ranking:
                    award_medal_list.append(restaurant_ranking)
            except:
                pass

            award_medal_text = ', '.join(award_medal_list)
            award_selection_text = ', '.join(award_selection_list)
            try:
                award_kamiawa = soup.find("div", {'class': 'rdheader-certification-label__target'}).text.strip()
            except:
                award_kamiawa = ''
            try:
                reservation_status = soup.find("p", {'class': 'rstinfo-table__reserve-status'}).text.strip()
            except:
                reservation_status = ''

            table_list = soup.find_all('table', {'class': 'c-table c-table--form rstinfo-table__table'})
            for table in table_list:
                for tr in table.find_all('tr'):
                    try:
                        th = tr.find('th').text.strip()
                        td = tr.find('td').text.strip()
                    except:
                        continue
                    if th == '交通手段':
                        transit_plan = td
                    if th == '営業時間':
                        opening_hours = td
                    if th == '支払い方法':
                        payment_method = td
                    if th == '予算':
                        try:
                            budget_info_list = tr.find('td').find_all("p", {'class': 'rstinfo-table__budget-item'})
                            for b in budget_info_list:
                                label = b.find('i').get('aria-label', '')
                                if label == 'Dinner':
                                    dinner_budget = b.text.strip()
                                if label == 'Lunch':
                                    lunch_budget = b.text.strip()
                        except:
                            pass
                    if th == '予算（口コミ集計）':
                        try:
                            budget_info_list = tr.find('td').find_all("span", {'class': 'rstinfo-table__budget-item'})
                            for b in budget_info_list:
                                label = b.find('i').get('aria-label', '')
                                if label == 'Dinner':
                                    dinner_budget_review = b.text.strip()
                                if label == 'Lunch':
                                    lunch_budget_review = b.text.strip()
                        except:
                            pass
                    if th == '席数':
                        no_of_seats = td
                    if th == 'ホームページ':
                        official_website = td
                    if th == '公式アカウント':
                        social_account = td
                    if th == 'オープン日':
                        opening_date = td
                    if th == '備考':
                        remarks = td
                    if th == '関連店舗情報':
                        try:
                            branches = 'tabelog.com' + tr.find('a').attrs['href']
                        except:
                            branches = ''

            result_list = [restaurant_name, rating_value, main_genre, add_region, add_locality, add_street, closest_station,
                           rating_count, save_count,
                           lunch_budget, dinner_budget, lunch_budget_review, dinner_budget_review,
                           award_medal_text, award_selection_text, award_kamiawa, genre,
                           transit_plan, closed_dates, opening_hours, reservation_status, payment_method, no_of_seats,
                           official_website, social_account, opening_date, remarks, branches, tabelog_site, lat, lng, image, name, price_range]
            return result_list
        except Exception as e:
            print(f"Error parsing {tabelog_site}: {e}")
            return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        for res in ex.map(parse_one, tabelog_urls):
            if res:
                records.append(res)

    if records:
        df = pd.DataFrame(records, columns=col_list)
    else:
        df = pd.DataFrame(columns=col_list)
    return df