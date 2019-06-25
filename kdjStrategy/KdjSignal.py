import talib as ta
import numpy as np
import pandas as pd

"""
将kdj策略需要用到的信号生成器抽离出来
"""

class KdjSignal():

    def __init__(self):
        self.author = 'BrianLee'

    def kdjCross(self,am,paraDict):
        fast_kPeriod = paraDict["fast_kPeriod"]
        slow_kPeriod = paraDict["slow_kPeriod"]
        slow_dPeriod = paraDict["slow_dPeriod"]
        
        sig_k,sig_d = ta.STOCH(am.high,am.low,am.close,
            fastk_period=fast_kPeriod,slowk_period=slow_kPeriod,slowd_period=slow_dPeriod)
        sig_j = sig_k*3-sig_d*2

        CrossSignal = 0
        if sig_k[-1]>30 and sig_k[-2]<30:
            CrossSignal = 1
        elif sig_k[-1]<70 and sig_k[-2]>70:
            CrossSignal = -1
        else:
            CrossSignal = 0
        if CrossSignal == 1 and sig_k[-1]<sig_d[-1] and sig_k[-2]>sig_d[-2] and sig_k[-1]<70:
            CrossSignal = -1
        if CrossSignal == -1 and sig_k[-1]>sig_d[-1] and sig_k[-2]<sig_d[-2] and sig_k[-1]>30:
            CrossSignal = 1
        return CrossSignal, sig_k, sig_d, sig_j
    
        
