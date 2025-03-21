import yfinance as yf
from AI_analysis import get_signal
import datetime
from datetime import timedelta
import pandas as pd
from enum import Enum
from constants import TradeAction
import os

class Simulation:
    def __init__(self, initial_balance, company_list):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.company_list = company_list
        self.date = datetime.datetime.now()
        self.portfolio = {}

    def get_price(self, company: str) -> float | None:
        """
        Fetch the closing price of a company's stock on the specified date.

        Args:
            company (str): The stock ticker symbol (e.g., 'AAPL').
        
        Returns:
            float | None: The closing price on the given date, or None if unavailable.
        """
        # Format self.date as a string in 'YYYY-MM-DD' format
        date_str = self.date.strftime('%Y-%m-%d')

        try:
            # Fetch historical prices for the range including the target date
            start_date = self.date
            end_date = self.date + timedelta(days=1)  # Fetch one day ahead to include data for the target date
            stock = yf.Ticker(company)
            hist = stock.history(start=start_date, end=end_date)

            # Check if data exists for the target date
            if not hist.empty:
                # Filter for the exact date
                if date_str in hist.index.strftime('%Y-%m-%d').to_list():
                    closing_price = hist.loc[date_str]['Close']
                    return closing_price
                else:
                    print(f"No price data available for {company} on {date_str}.")
                    return None
            else:
                print(f"No price data available for {company} on {date_str}.")
                return None
        except Exception as e:
            print(f"Error fetching price for {company} on {date_str}: {e}")
            return None

    def trade(self, action, company, quantity):
        price = self.get_price(company)
        if price is None:
            return

        cost = price * quantity

        if action == TradeAction.BUY:
            if self.balance >= cost:
                self.balance -= cost
                if company in self.portfolio:
                    self.portfolio[company] += quantity
                else:
                    self.portfolio[company] = quantity
                print(f"Bought {quantity} shares of {company} at ${price:.2f} each.")
            else:
                print("Insufficient funds to buy shares.")
        
        elif action == TradeAction.SELL:
            if company in self.portfolio and self.portfolio[company] >= quantity:
                self.balance += cost
                self.portfolio[company] -= quantity
                print(f"Sold {quantity} shares of {company} at ${price:.2f} each.")
            else:
                print("Insufficient shares to sell.")

        elif action == TradeAction.NOTHING:
            print("No action taken.")

    def date_increment(self):
        self.date += datetime.timedelta(days=1)

    def run(self, days):
        self.date = datetime.datetime.now() - datetime.timedelta(days=days)

        for day in range(days):
            print(f"\033[1m\nDay {day + 1}: {self.date.strftime('%Y-%m-%d')}\033[0m")
            for company in self.company_list:
                signal = get_signal(company, self.date)
                self.trade(signal, company, 1)
                self.date_increment()
            os.system("cls" if os.name == "nt" else "clear")

    def get_results(self):
        """
        Calculate and return the simulation results.
        """
        total_stock_value = sum(
            self.portfolio[company] * self.get_price(company)
            for company in self.portfolio
            if self.get_price(company) is not None
        )
        total_value = self.balance + total_stock_value
        gain = total_value - self.initial_balance

        return f"""
        Simulation Results:
        Initial Balance: ${self.initial_balance:.2f}
        Final Balance: ${self.balance:.2f}
        Total Stock Value: ${total_stock_value:.2f}
        Total Portfolio Value: ${total_value:.2f}
        Net Gain/Loss: ${gain:.2f}
        Portfolio: {self.portfolio}
        """

    


