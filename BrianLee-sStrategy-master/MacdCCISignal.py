import talib as ta
import numpy as np
import pandas as pd

"""
将kdj策略需要用到的信号生成器抽离出来
"""

class MacdCCISignal():

    def __init__(self):
        self.author = 'BrianLee'

    def CCIsignal(self, am, paraDict):
        CCIshortPeriod = paraDict["CCIshortPeriod"]
        CCIlongPeriod = paraDict["CCIlongPeriod"]
        up = 100
        down = -100
        CCI_short = ta.CCI(am.high,am.low,am.close,CCIshortPeriod)
        CCI_long = ta.CCI(am.high,am.low,am.close,CCIlongPeriod)
        breakup = CCI_short[-1]>up and CCI_short[-2]<=up and CCI_long[-1]>up and CCI_long[-2]<=up
        breakdn = CCI_short[-1]<down and CCI_short[-2]>=down and CCI_long[-1]<down and CCI_long[-2]>=down
        return  CCI_short,CCI_long,breakup,breakdn       # cciCrossSignal, up,CCI,down
    
    
    def macdSignal(self, am, paraDict):
        short_win = paraDict['short_win']
        long_win = paraDict['long_win']
        macd_win = paraDict['macd_win']
        # macd, macdsignal, macdhist = ta.MACD(am.close, fastperiod=short_win, slowperiod=long_win, signalperiod=macd_win)
        DIFF,DEA,macd = ta.MACD(am.close, fastperiod=short_win, slowperiod=long_win, signalperiod=macd_win)
        return macd
    
    def multiSignal(self,am,paraDict):
        CCI_short,CCI_long,breakup,breakdn = self.CCIsignal(am, paraDict)
        macd = self.macdSignal(am, paraDict)
        multisignal = 0
        if (CCI_short[-1]<0 and CCI_long[-1]<0 and macd[-1]>0) or breakup:
            multisignal = 1
        elif (CCI_short[-1]>0 and CCI_long[-1]>0 and macd[-1]<0) or breakdn:
            multisignal = -1
        else:
            multisignal = 0
        return multisignal,CCI_short,CCI_long,macd
    
        
