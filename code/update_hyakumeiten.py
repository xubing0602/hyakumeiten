import pandas as pd
import sys
import time
import random
from config import *
from utils import get_session, generate_res_details


def update_output(path, session=None, max_workers=8, delay=0.5):
    df_old = pd.read_csv(path)

    # preserve previous values
    df_old['prev_rating'] = df_old.get('rating')
    df_old['prev_rating_users'] = df_old.get('rating_users')
    df_old['prev_save_users'] = df_old.get('save_users')

    # prepare urls
    urls = df_old['tabelog_site'].tolist()
    # generate_res_details expects list-of-lists
    total_res_list = [urls]

    if session is None:
        session = get_session()

    # call scraper (it uses session and concurrency internally)
    # we pass session and use a modest number of workers
    df_new = generate_res_details(total_res_list, session=session, max_workers=max_workers)

    if df_new.empty:
        print('No new data fetched. Exiting.')
        return

    # set index on tabelog_site for merging
    df_old_indexed = df_old.set_index('tabelog_site')
    df_new_indexed = df_new.set_index('tabelog_site')

    # columns to update: use col_list from config
    cols_to_update = [c for c in df_new.columns if c != 'tabelog_site']

    for site, row in df_new_indexed.iterrows():
        if site in df_old_indexed.index:
            for c in cols_to_update:
                # skip prev columns
                if c in ('prev_rating', 'prev_rating_users', 'prev_save_users'):
                    continue
                df_old_indexed.at[site, c] = row.get(c)
        else:
            # new site: append
            df_old_indexed.loc[site] = [row.get(c) for c in df_old_indexed.columns]

    # reset index
    df_updated = df_old_indexed.reset_index()

    # save backup and updated file
    backup_path = path.replace('.csv', f'.backup_{int(time.time())}.csv')
    df_old.to_csv(backup_path, index=False)
    df_updated.to_csv(path, index=False)
    print(f'Updated file saved to {path}; backup saved to {backup_path}')


if __name__ == '__main__':
    # default polite settings: modest concurrency and delay
    session = get_session()
    PATH = sys.argv[1] if len(sys.argv) > 1 else HYAKUMEITEN_OUTPUT_PATH
    update_output(path=PATH, session=session, max_workers=8, delay=0.6)
