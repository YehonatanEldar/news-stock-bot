# Description: This file is the main file that will be used to run the program. 
# It will call the functions from the other files to get the news and the stock data.

import datetime
from get_news import get_news
from simulation import Simulation

if __name__ == '__main__':
    COMPANY_LIST = ['TSLA']    
    
    simulation = Simulation(COMPANY_LIST, 10000)
    simulation.run('2025-02-20', '2025-03-16')
    print(simulation.get_results())

