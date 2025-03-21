from enum import Enum

class TradeAction(Enum):
    BUY = 1
    SELL = -1
    NOTHING = 0