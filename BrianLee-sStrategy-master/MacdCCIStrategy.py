"""
这里的Demo是一个MACD+CCI顺势策略实现
"""
from vnpy.trader.vtConstant import *
from vnpy.trader.app.ctaStrategy import CtaTemplate
import talib as ta
from datetime import datetime
from MacdCCISignal import MacdCCISignal

########################################################################
# 策略继承CtaTemplate
class MacdCCIStrategy(CtaTemplate):
    """MACD+CCI策略Demo"""
    className = 'MACDCCIStrategy'
    author = 'BrianLee'
    
    # 策略变量
    transactionPrice = None # 记录成交价格
    
    # 参数列表
    paramList = [
                 # 时间周期
                 'timeframeMap',
                 # 取Bar的长度
                 'barPeriod',
                 # CCI信号周期
                 "CCIlongPeriod","CCIshortPeriod",
                 # MACD信号周期
                 'short_win','long_win','macd_win'
                 # 止损比例
                 'stoplossPct',
                 # 交易品种
                 'symbolList',
                 # 交易手数
                 'lot',
                 # 加仓参数
                 "posTime", 'addPct'
                ]    
    
    # 变量列表
    varList = ['transactionPrice']  
    
    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['posDict', 'eveningDict']

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        # 首先找到策略的父类（就是类CtaTemplate），然后把DoubleMaStrategy的对象转换为类CtaTemplate的对象
        super().__init__(ctaEngine, setting)
        self.paraDict = setting
        self.symbol = self.symbolList[0]
        

        self.chartLog = {
                'datetime':[],
                'CCI_short':[],
                'CCI_long':[],
                'macd':[]
                }

    def prepare_data(self):
        for timeframe in list(set(self.timeframeMap.values())):
            self.registerOnBar(self.symbol, timeframe, None)

    def arrayPrepared(self, period):
        am = self.getArrayManager(self.symbol, period)
        if not am.inited:
            return False, None
        else:
            return True, am

    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略"""
        self.setArrayManagerSize(self.barPeriod)
        self.prepare_data()
        self.putEvent()

    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'策略启动')
        self.putEvent()
    
    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略"""
        self.writeCtaLog(u'策略停止')
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送"""
        pass
    
    def stoploss(self, bar):
        if self.posDict[self.symbol+'_LONG']>0:
            if bar.low<self.transactionPrice*(1-self.paraDict["stoplossPct"]):
                self.cancelAll()
                self.sell(self.symbol, bar.close*0.99, self.posDict[self.symbol+'_LONG'])
        if self.posDict[self.symbol+'_SHORT']>0:
            if bar.high>self.transactionPrice*(1+self.paraDict["stoplossPct"]):
                self.cancelAll()
                self.cover(self.symbol, bar.close*0.99, self.posDict[self.symbol+'_LONG'])

    def strategy(self, bar):
        print('strategystrategystrategystrategystrategy')
        
        signalPeriod= self.timeframeMap["signalPeriod"]
        # 根据出场信号出场
        exitSig = self.exitSignal(signalPeriod)
        print('exitSig:', exitSig)
        self.exitOrder(bar, exitSig)

        # 根据进场信号进场
        entrySig = self.entrySignal(signalPeriod)
        print('entrySig:', entrySig)
        self.entryOrder(bar, entrySig)
        self.addPosOrder(bar)
        # 触发止损
        if exitSig == 0:
            self.stoploss(bar)
    
    def on5MinBar(self, bar):
        self.strategy(bar)

    def exitSignal(self, signalPeriod):
        arrayPrepared1, amSignal = self.arrayPrepared(signalPeriod)
        CrossSignal = 0
        if arrayPrepared1:
            algorithm = MacdCCISignal()
            CrossSignal,CCI_short,CCI_long,macd = algorithm.multiSignal(amSignal, self.paraDict)
        return CrossSignal

    def exitOrder(self, bar, exitSig):
        if self.posDict[self.symbol+'_LONG']>0:
            if exitSig==-1:
                self.cancelAll()
                self.sell(self.symbol, bar.close*0.99, self.posDict[self.symbol+'_LONG'])
        if self.posDict[self.symbol+'_SHORT']>0:
            if exitSig==1:
                self.cancelAll()
                self.cover(self.symbol, bar.close*1.01, self.posDict[self.symbol+'_LONG'])

    def entrySignal(self,signalPeriod):
        
        arrayPrepared1, amSignal = self.arrayPrepared(signalPeriod)
        entrySignal = 0
        if arrayPrepared1 :
            algorithm = MacdCCISignal()
            CrossSignal,CCI_short,CCI_long,macd = algorithm.multiSignal(amSignal, self.paraDict)
            
            if CrossSignal==1:
                entrySignal = 1
            elif CrossSignal==-1:
                entrySignal = -1
            else:
                entrySignal = 0

            self.chartLog['datetime'].append(datetime.strptime(amSignal.datetime[-1], "%Y%m%d %H:%M:%S"))
            self.chartLog['CCI_short'].append(CCI_short[-1])
            self.chartLog['CCI_long'].append(CCI_long[-1])
            self.chartLog['macd'].append(macd[-1])
        return entrySignal

    def entryOrder(self, bar, entrySignal):
        # 没有多头持仓
        if (entrySignal==1) and (self.posDict[self.symbol+'_LONG']==0):
            # 如果没有空头持仓，则直接做多
            if  self.posDict[self.symbol+'_SHORT']==0:
                self.buy(self.symbol, bar.close*1.01, self.lot)  # 成交价*1.01发送高价位的限价单，以最优市价买入进场
            # 如果有空头持仓，则先平空，再做多
            elif self.posDict[self.symbol+'_SHORT'] > 0:
                self.cancelAll() # 撤销挂单
                self.cover(self.symbol, bar.close*1.01, self.posDict[self.symbol+'_SHORT']) 
                self.buy(self.symbol, bar.close*1.01, self.lot)
        # 没有空头持仓
        elif (entrySignal==-1) and (self.posDict[self.symbol+'_SHORT']==0):
            if self.posDict[self.symbol+'_LONG']==0:
                self.short(self.symbol, bar.close*0.99, self.lot) # 成交价*0.99发送低价位的限价单，以最优市价卖出进场
            elif self.posDict[self.symbol+'_LONG'] > 0:
                self.cancelAll() # 撤销挂单
                self.sell(self.symbol, bar.close*0.99, self.posDict[self.symbol+'_LONG'])
                self.short(self.symbol, bar.close*0.99, self.lot)
        # 发出状态更新事件
        self.putEvent()


        
    def addPosOrder(self, bar):
        lastOrder=self.transactionPrice
        if self.posDict[self.symbol+'_LONG'] ==0 and self.posDict[self.symbol + "_SHORT"] == 0:
            self.nPos = 0
        # 反马丁格尔加仓模块______________________________________
        if (self.posDict[self.symbol+'_LONG']!=0 and self.nPos < self.posTime):    # 持有多头仓位并且加仓次数不超过3次
            if bar.close/lastOrder-1>= self.addPct:   # 计算盈利比例,达到2%
                self.nPos += 1  # 加仓次数减少 1 次
                addLot = self.lot*(2**self.nPos)
                self.buy(self.symbol,bar.close*1.02,addLot)  # 加仓 2手、4手、8手
        elif (self.posDict[self.symbol + "_SHORT"] != 0 and self.nPos < self.posTime):    # 持有空头仓位并且加仓次数不超过3次
            if lastOrder/bar.close-1 >= self.addPct:   # 计算盈利比例,达到2%
                self.nPos += 1 # 加仓次数减少 1 次
                addLot = self.lot*(2**self.nPos)
                self.short(self.symbol,bar.close*0.98,addLot)  # 加仓 2手、4手、8手
    
    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
    
    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送"""
        if trade.offset == OFFSET_OPEN:  # 判断成交订单类型
            self.transactionPrice = trade.price # 记录成交价格

    #----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass
