import yfinance as yf
from AI_analysis import get_signal
import datetime
import pandas as pd

def get_stock_price(company):
    stock = yf.Ticker(company)
    return stock.info['regularMarketPrice']

def get_historical_prices(company, start_date, end_date):
    """
    Fetch historical closing prices for a given company and date range.

    Args:
        company (str): The stock ticker symbol (e.g., 'AAPL').
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.

    Returns:
        pd.Series: A pandas Series containing the closing prices for the given date range.
    """
    try:
        stock = yf.Ticker(company)
        hist = stock.history(start=start_date, end=end_date)

        # Check if the DataFrame is empty
        if hist.empty:
            print(f"No historical data found for {company} between {start_date} and {end_date}.")
            return None

        # Return the 'Close' column as a pandas Series
        return hist['Close']

    except Exception as e:
        print(f"Error fetching historical data for {company}: {e}")
        return None

class Simulation:
    def __init__(self, companies, initial_money):
        self.companies = companies
        self.initial_money = initial_money
        self.money = initial_money
        self.stocks = {company: 0 for company in companies}
        self.total_value = 0

    def run(self, start_date: str, end_date: str):
        date_range = pd.date_range(start=start_date, end=end_date)
        print('Running simulation...')
        for date in date_range:
            for company in self.companies:
                signal = get_signal(company, date.strftime('%Y-%m-%d'))
                print(f'Date: {date}, Signal: {signal}')
                prices = get_historical_prices(company, date.strftime('%Y-%m-%d'), (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
                if prices is None or prices.empty:
                    print(f"Skipping {company} on {date} due to missing price data.")
                    continue
                price = prices.iloc[0]
                if signal == 1:
                    self.buy(company, 1, price)
                elif signal == -1:
                    self.sell(company, 1, price)

    def buy(self, company, quantity, price):
        print('BUY!!!')
        if self.money >= price * quantity:
            self.money -= price * quantity
            self.stocks[company] += quantity
            self.total_value += price * quantity
        else:
            print("Not enough money to buy")

    def sell(self, company, quantity, price):
        print('SELL!!!')
        if self.stocks[company] >= quantity:
            self.money += price * quantity
            self.stocks[company] -= quantity
            self.total_value -= price * quantity
        else:
            print("Not enough stocks to sell")

    def get_results(self):
        return f"""
        Gain: {self.total_value - self.initial_money}
        Total: {self.total_value}
        Money: {self.money}
        Stock Money: {sum([self.stocks[company] * get_stock_price(company) for company in self.companies])}
                """


