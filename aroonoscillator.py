# Commented out IPython magic to ensure Python compatibility.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

# %matplotlib inline
import warnings
warnings.filterwarnings('ignore')

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt

class Aroon_oscillator(bt.Strategy):
  params= (
      ('myperiod', 14),
      ('lowerband', 30))

  def log(self, txt, dt=None):
    dt = dt or self.datas[0].datetime.date(0)
    print('%s, %s' % (dt.isoformat(), txt))
  def __init__(self):
    self.dataclose = self.datas[0].close
    self.Aroon = bt.indicators.AroonOscillator(self.datas[0], period=self.params.myperiod)
    self.Aroon_EMA =  bt.indicators.ExponentialMovingAverage(self.Aroon, period=self.params.lowerband)
    self.Cross_Aroon= bt.indicators.CrossOver(self.Aroon,self.Aroon_EMA,plotname='Buy_Sell_Line')

    self.order = None
    self.buyprice = None
    self.buycomm = None

  def notify_order(self, order):
    if order.status in [order.Submitted, order.Accepted]:
      return
    # Check if an order has been completed
    # Attention: broker could reject order if not enough cash
    if order.status in [order.Completed]:
      if order.isbuy():
        self.log('BUY EXECUTED, %.2f' % order.executed.price)
      elif order.issell():
        self.log('SELL EXECUTED, %.2f' % order.executed.price)

      self.bar_executed = len(self)

    elif order.status in [order.Canceled, order.Margin, order.Rejected]:
      self.log('Order Canceled/Margin/Rejected')

    # Write down: no pending order
    self.order = None
  def next(self):
    if self.order:
      return
    if not self.position:
      if self.Cross_Aroon > 0:
        self.log('BUY CREATE, %.2f' % self.data.close[0])
        self.order = self.buy()

    else:
      if self.Cross_Aroon < 0:
        self.log('SELL CREATE, %.2f' % self.data.close[0])
        self.order = self.sell()

if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(Aroon_oscillator)

        # Create a Data Feed
    data = bt.feeds.YahooFinanceData(
        dataname='AAPL',
        # Do not pass values before this date
        fromdate=datetime.datetime(2018, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2019, 12, 31),
        # Do not pass values after this date
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)

    # Set the commission
    cerebro.broker.setcommission(commission=0.0)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()

    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Plot the result
    cerebro.plot(iplot = False)
