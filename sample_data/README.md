This folder contains raw **CSV ledger data** exported from cryptocurrency exchanges such as **Kraken**, **Coinbase**, and others. These files will be 
ingested and processed by the application to perform **Capital Gains Tax (CGT)** calculations.

## Folder Purpose

The purpose of this folder is to store **real transaction history** including:
- Trades (buy/sell)
- Deposits & withdrawals
- Fees
- Staking rewards (if applicable)

## File Format

All files should be in **CSV format** directly exported from the respective exchange platform. Each file should follow the original exchange-export format 
without manual editing to ensure accurate parsing.

## Example filenames: 

kraken.csv   coinbase.csv  binance.csv

## How to Add Files

1. Go to your exchange account (e.g., Kraken, Coinbase).
2. Export your full transaction history or ledger in **CSV** format.
3. Place the file inside this folder.
4. Optionally rename it using the pattern: name_of_broker.csv

## Warning

Please avoid committing sensitive or personal financial data to public repositories. Either:
- Add this folder to `.gitignore`, or  
- Only commit **anonymized** or **mock** data versions for testing.

## Next Steps

Once ledger data is added, the backend parser will:
1. Parse the CSV into normalized transaction objects
2. Match buys/sells using FIFO/LIFO or specific identification
3. Calculate CGT liabilities for the financial year
