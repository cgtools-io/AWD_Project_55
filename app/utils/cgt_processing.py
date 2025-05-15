import os
import pandas as pd
import re

def clean_float(value):
    try:
        # Remove all non-digit, non-dot, and non-minus characters
        cleaned = re.sub(r'[^0-9.\-]', '', str(value))
        return float(cleaned)
    except:
        return 0.0

def parse_binance_csv(filename):

    file_path = os.path.join('app/static/uploads', filename)

    if not os.path.exists(file_path):
        return f"File {filename} does not exist in 'app/static/uploads'."

    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        df['datetime'] = pd.to_datetime(df['Date(UTC)'], utc=True)
        df = df.rename(columns={
            'Side': 'Side',
            'Price': 'Price',
            'Executed': 'executed_amount',
            'Fee': 'fee_amount',
            'Pair': 'base_asset'
        })

        df['fee_amount'] = df['fee_amount'].apply(clean_float)
        df['executed_amount'] = df['executed_amount'].apply(clean_float)
        df['Price'] = df['Price'].apply(clean_float)
        
        return df
    
    except Exception as e:
        
        return f"Error processing file: {e}"

def calculate_cgt_binance(binance_df):

    binance_df = binance_df.sort_values(by='datetime')
    buy_pool = []
    cgt_results = []

    for _, row in binance_df.iterrows():
        if row['Side'] == 'BUY':
            buy_pool.append({
                'datetime': row['datetime'],
                'asset': row['base_asset'],
                'amount': clean_float(row['executed_amount']),
                'price': clean_float(row['Price']),
                'fee': clean_float(row['fee_amount'])
            })

        elif row['Side'] == 'SELL':
            sell_asset = row['base_asset']
            sell_amount = clean_float(row['executed_amount'])
            sell_price = clean_float(row['Price'])
            fee_amount = clean_float(row['fee_amount'])
            sale_proceeds = sell_amount * sell_price - fee_amount
            cost_base = 0.0

            while sell_amount > 0 and buy_pool:
                earliest = buy_pool[0]
                if earliest['asset'] != sell_asset:
                    buy_pool.pop(0)
                    continue

                used = min(sell_amount, earliest['amount'])
                cost = used * earliest['price']
                cost_base += cost

                earliest['amount'] -= used
                if earliest['amount'] <= 0:
                    buy_pool.pop(0)

                sell_amount -= used

            capital_gain = sale_proceeds - cost_base
            cgt_results.append(capital_gain)

    return round(sum(cgt_results), 2)