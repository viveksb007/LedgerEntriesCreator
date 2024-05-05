import csv
import json
from datetime import datetime


class Record:
    def __init__(self, symbol, isin, trade_date, exchange, segment, series, trade_type, auction, quantity, price,
                 trade_id, order_id, order_execution_time):
        self.symbol = symbol
        self.isin = isin
        self.trade_date = trade_date
        self.exchange = exchange
        self.segment = segment
        self.series = series
        self.trade_type = trade_type
        self.auction = auction
        self.quantity = quantity
        self.price = price
        self.trade_id = trade_id
        self.order_id = order_id
        self.order_execution_time = order_execution_time


class LedgerEntry:
    def __init__(self, date, title, quantity, price, credit_account, debit_account, currency, trade_type):
        self.date = date
        self.title = title
        self.quantity = float(quantity)
        self.price = float(price)
        self.credit_account = credit_account
        self.debit_account = debit_account
        self.currency = currency
        self.debit_amount = round(self.quantity * self.price)
        self.credit_account_ticker = str(credit_account).split(":")[-1]
        self.trade_type = trade_type

    def __str__(self):
        if self.trade_type == 'buy':
            debit_str = f'{self.debit_account} \t -{self.debit_amount} {self.currency}'
            credit_str = f'{self.credit_account} \t {self.quantity} {self.credit_account_ticker} @ {self.price} {self.currency}'
            return f'{self.date} {self.title}\n    {debit_str}\n    {credit_str}'
        elif self.trade_type == 'sell':
            debit_str = f'{self.debit_account} \t {self.debit_amount} {self.currency}'
            credit_str = f'{self.credit_account} \t -{self.quantity} {self.credit_account_ticker} @ {self.price} {self.currency}'
            return f'{self.date} {self.title}\n    {debit_str}\n    {credit_str}'
        else:
            raise Exception("invalid trade type")


class Transformer:
    @staticmethod
    def parse(csv_file_path):
        records = []
        with open(csv_file_path, 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                trade_date = datetime.strptime(row['trade_date'], '%Y-%m-%d').strftime('%Y/%m/%d')
                record = Record(
                    symbol=row['symbol'],
                    isin=row['isin'],
                    trade_date=trade_date,
                    exchange=row['exchange'],
                    segment=row['segment'],
                    series=row['series'],
                    trade_type=row['trade_type'],
                    auction=row['auction'],
                    quantity=row['quantity'],
                    price=row['price'],
                    trade_id=row['trade_id'],
                    order_id=row['order_id'],
                    order_execution_time=row['order_execution_time']
                )
                records.append(record)
        return records


def create_ledger_entries():
    csv_file_path = 'testdata/test-data-zerodha-coin.csv'

    with open('config.json', 'r') as file:
        mf_mapping_data = json.load(file)

    entries_file = open("output/zerodha-coin-ledger_entries.txt", "w")

    records = Transformer.parse(csv_file_path)
    for record in records:
        # print(record.symbol, record.isin, record.trade_date, record.exchange, record.segment, record.series,
        #       record.trade_type, record.auction, record.quantity, record.price, record.trade_id, record.order_id,
        #       record.order_execution_time)

        # using "isin" to map to credit account defined in our ledger
        entry = LedgerEntry(
            date=record.trade_date,
            title=record.trade_type,
            quantity=record.quantity,
            price=record.price,
            credit_account=mf_mapping_data[record.isin],
            debit_account="Assets:Checking:HDFC",
            currency='INR',
            trade_type=record.trade_type
        )
        print(entry)
        print("\n")
        entries_file.write(str(entry) + '\n\n')


if __name__ == "__main__":
    create_ledger_entries()
