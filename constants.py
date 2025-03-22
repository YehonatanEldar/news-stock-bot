from enum import Enum

class TradeAction(Enum):
    BUY = 1
    SELL = -1
    NOTHING = 0

class RankingTypeFactors(Enum):
    POPULARITY = ('popularity', 0.5)
    RELEVANCY = ('relevancy', 0.3)
    BOTH = ('both', 0.8)

    def __init__(self, string: str, factor: float):
        self.string = string
        self.factor = factor