# Description: This file is the main file that will be used to run the program. 
# It will call the functions from the other files to get the news and the stock data.

import datetime
from get_news import get_news

if __name__ == '__main__':
    COMPANY_LIST = ['AAPL', 'GOOGL', 'AMZN', 'MSFT', 'TSLA']    
    
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    news = get_news(COMPANY_LIST[0], yesterday)

