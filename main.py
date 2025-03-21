# Description: This file is the main file that will be used to run the program. 
# It will call the functions from the other files to get the news and the stock data.

import datetime

from get_news import get_news
from simulation import Simulation

if __name__ == '__main__':
    COMPANY_LIST = ['GOOG', 'AAPL', 'MSFT', 'AMZN']    
    
    DAYS = 14
    simulation = Simulation(10000, COMPANY_LIST)
    simulation.run(DAYS)
    results = simulation.get_results()
    print(results)

