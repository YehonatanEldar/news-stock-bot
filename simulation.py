import yfinance as yf
from AI_analysis import get_signal

def get_stock_price(company):
    stock = yf.Ticker(company)
    return stock.info['regularMarketPrice']

class Simulation:
    def __init__(self, companies, initial_money):
        self.companies = companies
        self.money = initial_money
        self.stocks = {company: 0 for company in companies}
        self.total_value = 0

    def run(self, days):
        for day in range(days):
            for company in self.companies:
                signal = get_signal(company)
                if signal == 1:
                    self.buy(company, 1)
                elif signal == -1:
                    self.sell(company, 1)

        


    def buy(self, company, quantity):
        if self.money >= get_stock_price(company) * quantity:
            self.money -= get_stock_price(company) * quantity
            self.stocks[company] += quantity
            self.total_value += get_stock_price(company) * quantity
        else:
            print("Not enough money to buy")

    def sell(self, company, quantity):
        if self.stocks[company] >= quantity:
            self.money += get_stock_price(company) * quantity
            self.stocks[company] -= quantity
            self.total_value -= get_stock_price(company) * quantity
        else:
            print("Not enough stocks to sell")

