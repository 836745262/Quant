import talib as ta
import numpy as np
import pandas as pd

"""
将kdj策略需要用到的信号生成器抽离出来
"""

class adxSignal():

    def __init__(self):
        self.author = 'ChannelCMT'

    def adxsignal(self, am, paraDict):
        ADXPeriod = paraDict["ADXPeriod"]

        ADX = ta.ADX(am.high,am.low,am.close,ADXPeriod)
        # ADXR = ta.ADXR(am.high,am.low,am.close,ADXPeriod)
        PLUS_DI = ta.PLUS_DI(am.high,am.low,am.close,ADXPeriod)
        MINUS_DI = ta.MINUS_DI(am.high,am.low,am.close,ADXPeriod)
        # SHORTMA = ta.SMA(am.close,ADXPeriod)
        # LONGMA = ta.SMA(am.close,ADXPeriod)
        # breakup = SHORTMA[-1]>LONGMA[-1] and SHORTMA[-2]<LONGMA[-2] and ADX[-1]>ADX[-2] and PLUS_DI[-1]>MINUS_DI[-1]
        # breakdown = SHORTMA[-1]<LONGMA[-1] and SHORTMA[-2]>LONGMA[-2] and ADX[-1]<ADX[-2] and PLUS_DI[-1]<MINUS_DI[-1]
        breakup =   PLUS_DI[-2]<MINUS_DI[-2] and PLUS_DI[-1]>=MINUS_DI[-1]
        breakdown =   PLUS_DI[-2]>MINUS_DI[-2] and PLUS_DI[-1]<=MINUS_DI[-1]

        CrossSignal = 0
        if breakup:
            CrossSignal = 1
        elif breakdown:
            CrossSignal = -1
        else:
            CrossSignal = 0
        return CrossSignal, PLUS_DI, ADX, MINUS_DI
    
        