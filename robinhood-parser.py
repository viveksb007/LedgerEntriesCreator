import csv
import json
from datetime import datetime


class Transaction:
    def __init__(self, activity_date, process_date, settle_date, instrument, description, trans_code, quantity, price,
                 amount):
        self.activity_date = activity_date
        self.process_date = process_date
        self.settle_date = settle_date
        self.instrument = instrument
        self.description = description
        self.trans_code = trans_code
        self.quantity = quantity
        self.price = price
        self.amount = amount


class LedgerEntry:
    def __init__(self, date, title, quantity, price, credit_account, debit_account, currency, trade_type):
        self.date = date
        self.title = title
        self.quantity = float(quantity)
        self.price = float(price[1:].replace(',', ''))
        self.credit_account = credit_account
        self.debit_account = debit_account
        self.currency = currency
        self.debit_amount = round(self.quantity * self.price)
        self.credit_account_ticker = str(credit_account).split(":")[-1]
        self.trade_type = trade_type

    def __str__(self):
        if self.trade_type == 'Buy':
            credit_str = f'{self.credit_account} \t {self.quantity} {self.credit_account_ticker} @ {self.price} {self.currency}'
            debit_str = f'{self.debit_account} \t -{self.debit_amount} {self.currency}'
            # debit_str = 'Income:Salary:Genesis'
            return f'{self.date} {self.title}\n    {credit_str}\n    {debit_str}'
        elif self.trade_type == 'Sell':
            debit_str = f'{self.debit_account} \t {self.debit_amount} {self.currency}'
            credit_str = f'{self.credit_account} \t -{self.quantity} {self.credit_account_ticker} @ {self.price} {self.currency}'
            return f'{self.date} {self.title}\n    {debit_str}\n    {credit_str}'
        else:
            raise Exception("invalid trade type")


class Transformer:
    @staticmethod
    def parse(csv_file_path):
        transactions = []
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)  # Skip the header row
            for row in reader:
                # print(row)
                if len(row) != 9:
                    continue
                activity_date, process_date, settle_date, instrument, description, trans_code, quantity, price, amount = row
                activity_date = datetime.strptime(activity_date, '%m/%d/%Y').strftime('%Y/%m/%d')
                transaction = Transaction(activity_date, process_date, settle_date, instrument, description, trans_code,
                                          quantity, price, amount)
                transactions.append(transaction)
        sorted_transactions = sorted(transactions, key=lambda x: x.activity_date)
        return sorted_transactions


def create_ledger_entries():
    with open('config.json', 'r') as file:
        mf_mapping_data = json.load(file)
    entries_file = open("output/robinhood-ledger_entries.txt", "w")
    csv_file_path = "testdata/test-data-robinhood.csv"
    # csv_file_path = "realdata/rhood-2025.csv"
    transactions = Transformer.parse(csv_file_path)
    for transaction in transactions:
        if transaction.trans_code not in ["Buy", "Sell"]:
            continue
        description = transaction.description
        cusip_start_index = description.find("CUSIP:") + len("CUSIP:")
        cusip_end_index = description.find("\n", cusip_start_index)
        if cusip_end_index == -1:
            cusip_end_index = len(description)
        cusip = description[cusip_start_index:cusip_end_index].strip()
        title = description[:description.find("\n")]
        # print(cusip)
        # print(vars(transaction))
        ledger_entry = LedgerEntry(transaction.activity_date, title, transaction.quantity,
                                   transaction.price, mf_mapping_data[cusip],
                                   "Income:Salary:Genesis", "USD",
                                   transaction.trans_code)
        print(ledger_entry)
        print("\n")
        entries_file.write(str(ledger_entry) + '\n\n')


if __name__ == "__main__":
    create_ledger_entries()
