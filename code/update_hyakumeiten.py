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

    # columns to update: use col_list from config, skip prev columns
    cols_to_update = [c for c in df_new.columns if c not in ('tabelog_site', 'prev_rating', 'prev_rating_users', 'prev_save_users')]

    # Sync data types: ensure df_new matches df_old's dtypes to avoid TypeErrors
    for col in cols_to_update:
        if col in df_old_indexed.columns:
            try:
                df_new_indexed[col] = df_new_indexed[col].astype(df_old_indexed[col].dtype)
            except (ValueError, TypeError):
                # If conversion fails, convert to common safe type (object or numeric)
                if pd.api.types.is_numeric_dtype(df_old_indexed[col].dtype):
                    df_new_indexed[col] = pd.to_numeric(df_new_indexed[col], errors='coerce')
                else:
                    df_new_indexed[col] = df_new_indexed[col].astype('object')

    # Find existing and new sites using set operations (faster than iterating)
    existing_sites = df_new_indexed.index.intersection(df_old_indexed.index)
    new_sites = df_new_indexed.index.difference(df_old_indexed.index)

    # Update existing sites using vectorized operation
    if len(existing_sites) > 0:
        df_old_indexed.loc[existing_sites, cols_to_update] = df_new_indexed.loc[existing_sites, cols_to_update]

    # Add new sites efficiently using concat instead of row-by-row assignment
    if len(new_sites) > 0:
        df_new_for_append = df_new_indexed.loc[new_sites].copy()
        # Ensure all columns from df_old_indexed exist in df_new_for_append, fill missing with NaN
        for col in df_old_indexed.columns:
            if col not in df_new_for_append.columns:
                df_new_for_append[col] = None
        # Append new rows with proper column order
        df_old_indexed = pd.concat([df_old_indexed, df_new_for_append[df_old_indexed.columns]], ignore_index=False)

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
