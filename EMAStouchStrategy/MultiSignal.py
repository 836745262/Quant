import talib as ta
import numpy as np
import pandas as pd

"""
将kdj策略需要用到的信号生成器抽离出来
"""

class MultiSignal():

    def __init__(self):
        self.author = 'BrianLee'
    
    def EMASignal(self, am, paraDict):
        EMAfastPeriod = paraDict["EMAfastPeriod"]
        EMAslowPeriod = paraDict["EMAslowPeriod"]
        EMA_short = ta.EMA(am.close, timeperiod=EMAfastPeriod)
        EMA_long = ta.EMA(am.close, timeperiod=EMAslowPeriod)
        return EMA_short, EMA_long
    
    def StochSignal(self,am, paraDict):
        slow_dPeriod = paraDict['slow_dPeriod']
        fast_kPeriod = paraDict['fast_kPeriod']
        slow_kPeriod = paraDict['slow_kPeriod']
        slowk, slowd = ta.STOCH(am.high,am.close,am.low,
                                   fastk_period=fast_kPeriod,
                                   slowk_period=slow_kPeriod,
                                   slowk_matype=0,
                                   slowd_period=slow_dPeriod,
                                   slowd_matype=0)
        return slowk, slowd

    
    
    def multiSignal(self,am,paraDict):
        EMA_short, EMA_long = self.EMASignal(am, paraDict)
        slowk, slowd = self.StochSignal(am, paraDict)
        multisignal = 0
        if (slowd[-1]<50 and (
            EMA_long[-1]<EMA_short[-1] and EMA_long[-2]>EMA_short[-2])) :
            multisignal = 1
        elif (slowd[-1]>50 and (
            EMA_long[-1]>EMA_short[-1] and EMA_long[-2]<EMA_short[-2])) :
            multisignal = -1
        else:
            multisignal = 0
        return multisignal
            
        
    
        