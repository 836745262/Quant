import talib as ta
import numpy as np
import pandas as pd

"""
将kdj策略需要用到的信号生成器抽离出来
"""

class AroonSignal():

    def __init__(self):
        self.author = 'BrianLee'

    def AroonCross(self,am,paraDict):
        AroonPeriod = paraDict["AroonPeriod"]
        aroondown, aroonup = ta.AROON(am.high, am.low, timeperiod=AroonPeriod)
        aroon = aroonup - aroondown
        goldenCross = aroonup[-1]>paraDict['threshold'] and aroon[-1]>0
        deathCross = aroondown[-1]<paraDict['threshold'] and aroon[-1]<0

        CrossSignal = 0
        if goldenCross:
            CrossSignal = 1
        elif deathCross:
            CrossSignal = -1
        else:
            CrossSignal = 0
        return CrossSignal, aroondown, aroonup, aroon
    
        
