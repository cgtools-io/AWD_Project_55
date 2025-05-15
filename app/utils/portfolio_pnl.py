import os 
import pandas as pd
import re

from .cgt_processing import clean_float

def calculate_total_cost(df):

    df = df.sort_values(by='datetime')
    buy_pool = []
    total_cost = 0.0

    print(df)

    for _, row in df.iterrows():

        print(row)
        
        if row['Side'] == 'BUY':
            buy_pool.append({
                'asset': row['base_asset'],
                'units': clean_float(row['executed_amount']),
                'cost': clean_float(row['Amount']) + clean_float(row['fee_amount'])
            })

            total_cost += clean_float(row['Amount']) + clean_float(row['fee_amount'])

        elif row['Side'] == 'SELL':
            sell_asset = row['base_asset']
            units_sold = clean_float(row['executed_amount'])

            i = 0

            while units_sold > 0 and buy_pool and i < len(buy_pool):
                earliest = buy_pool[i]
                if earliest['asset'] != sell_asset:
                    i += 1
                    continue
                
                if earliest['units'] > units_sold:
                    total_cost -= units_sold * earliest['cost'] / earliest['units']
                    earliest['cost'] -= units_sold * earliest['cost'] / earliest['units']
                    earliest['units'] -= units_sold
                    units_sold = 0
                else:
                    total_cost -= earliest['cost']
                    units_sold -= earliest['units']
                    buy_pool.pop(i)
                    i = 0
        
    return round(total_cost, 2)
