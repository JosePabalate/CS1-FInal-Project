import os
import telebot
import yfinance as yf
import yahoo_fin as y_f
from yahoo_fin.stock_info import *
import bob_telegram_tools.bot
from bob_telegram_tools.bot import TelegramBot
import matplotlib
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib.dates as mpl_dates
from mplfinance.original_flavor import candlestick_ohlc


token = "1859074916:AAFA20k6Qc4A-VLbnmVfjZyqH0b6Qx8HGig"
bot = telebot.TeleBot(token)

#help
@bot.message_handler(commands=['help'])
def help(message):
  help_message = "Hello\U0001F600! Thank you for using USAStockMarketBot. \n\nHere are the stock analytics commands: \n\U0001F4B5 price [ticker] - sends stock price and its monthly candlestick graph. \n\U0001F4D1 volume [ticker] - sends stock volume and its monthly graph. \n\U0001F4C8 /gainers - sends top five stock gainers today! \n\U0001F4C9/losers - sends top five stock losers today! \n\U0001F4CA	/mostactive - sends the top five most active stocks during the day! \n\nHere are the stock info commands\U0001F4DD: \n\U0001F4B4 dividend [ticker] - sends recorded stock dividends. \n\U0001F306	summary [ticker] - sends the company background info. \n\U0001F4C3	yahoo [ticker] - sends link to stock's yahoo finance page! \n\U0001F4B0	cap [ticker] - sends stock's current market cap. \n\U0001F4F0	news [ticker] - sends latest news about the stock!"
  bot.send_message(message.chat.id, help_message)


def error(message):
  error_message = "You have entered an invalid command. Please type /help to access all the valid commands \U0001F600."
  bot.send_message(message.chat.id, error_message)


#price
def price_request(message):
  request = message.text.split()
  if request[0].lower() == "price":
    return True
  else:
    return False


@bot.message_handler(func=price_request)
def send_price(message):
  request = message.text.split()[1]
  rawdata = yf.download(tickers=request, period='5d', interval='1d')
  graphdata = yf.download(tickers=request, period='1mo', interval='1d')
  if rawdata.size > 0 and graphdata.size >0:
    data = rawdata.reset_index()
    data["format_date"] = data['Date'].dt.strftime('%m/%d')
    data.set_index('format_date', inplace=True)
    print(data.to_string())
    bot.send_message(message.chat.id, data['Close'].to_string(header=False))
    graphbot = TelegramBot("1859074916:AAFA20k6Qc4A-VLbnmVfjZyqH0b6Qx8HGig",message.chat.id)
    plt.style.use('ggplot')
    graphdata = graphdata.reset_index()
    ohlc = graphdata.loc[:, ['Date','Open', 'High', 'Low', 'Close']]
    ohlc['Date'] = pd.to_datetime(ohlc['Date'])
    ohlc['Date'] = ohlc['Date'].apply(mpl_dates.date2num)
    fig, ax = plt.subplots()
    candlestick_ohlc(ax, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)
    ohlc['SMA5'] = ohlc['Close'].rolling(5).mean()
    ax.plot(ohlc['Date'], ohlc['SMA5'], color='blue',label='Simple Moving Average in a period of 5 days')
    plt.legend()
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    fig.suptitle('Monthly Candlestick Chart of {}'.format(request.upper()))
    date_format = mpl_dates.DateFormatter('%d-%m-%Y')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    fig.tight_layout()
    graphbot.send_plot(plt)
    graphbot.clean_tmp_dir()
  else:
    bot.send_message(message.chat.id, "No data!")


#volume
def volume_request(message):
  request = message.text.split()
  if request[0].lower() == "volume":
    return True
  else:
    return False


@bot.message_handler(func=volume_request)
def send_volume(message):
  request = message.text.split()[1]
  rawdata = yf.download(tickers=request, period= '5d', interval='1d')
  graphdata = yf.download(tickers=request, period= '1wk', interval='1d')
  if rawdata.size > 0:
    data = rawdata.reset_index()
    data["format_date"] = data['Date'].dt.strftime('%m/%d')
    data.set_index('format_date', inplace=True)
    print(data.to_string())
    bot.send_message(message.chat.id, data['Volume'].to_string(header=False))
    graphbot = TelegramBot("1859074916:AAFA20k6Qc4A-VLbnmVfjZyqH0b6Qx8HGig",message.chat.id)
    graphdata = graphdata.reset_index()
    graphdata["Date"] = graphdata['Date'].dt.strftime('%m/%d')
    fig, axes = plt.subplots()
    axes.plot(graphdata["Date"], graphdata["Volume"],color="purple", lw=1, ls='-', marker='o', markersize=4)
    axes.set_xlabel('Date')
    axes.set_ylabel('Volume')
    fig.suptitle('Weekly Volume Chart of {}'.format(request.upper()))
    fig.tight_layout()
    graphbot.send_plot(plt)
    graphbot.clean_tmp_dir()
  else:
    bot.send_message(message.chat.id, "No data!")


#gainers
@bot.message_handler(commands=['gainers'])
def gainers(message):
  data = get_day_gainers()
  data = data.head()
  bot.send_message(message.chat.id,data[['Symbol','% Change']].to_string(justify = 'center',header = True, index = False, col_space = 4))
  graphbot = TelegramBot("1859074916:AAFA20k6Qc4A-VLbnmVfjZyqH0b6Qx8HGig",message.chat.id)
  fig, axes = plt.subplots()
  axes.bar(data["Symbol"], data["% Change"],align="center",color = 'green')
  axes.set_xlabel('Symbol')
  axes.set_ylabel('% Change')
  fig.suptitle("Today's Biggest Gainers")
  fig.tight_layout()
  graphbot.send_plot(plt)
  graphbot.clean_tmp_dir()


#losers
@bot.message_handler(commands=['losers'])
def losers(message):
  data = get_day_losers()
  data = data.head()
  bot.send_message(message.chat.id,data[['Symbol','% Change']].to_string(justify = 'center',header = True, index = False, col_space = 4))
  graphbot = TelegramBot("1859074916:AAFA20k6Qc4A-VLbnmVfjZyqH0b6Qx8HGig",message.chat.id)
  fig, axes = plt.subplots()
  axes.bar(data["Symbol"], data["% Change"],align='center',color = "r")
  axes.set_xlabel('Symbol')
  axes.set_ylabel('% Change')
  fig.suptitle("Today's Biggest Losers")
  fig.tight_layout()
  graphbot.send_plot(plt)
  graphbot.clean_tmp_dir()


#most active
@bot.message_handler(commands=['mostactive'])
def mostactive(message):
  data = get_day_most_active()
  data = data.head()
  bot.send_message(message.chat.id,data[['Symbol','Change','% Change']].to_string(justify = 'center',header = True, index = False, col_space = 8))


#dividends
def dividend_request(message):
  request = message.text.split()
  if request[0].lower() == "dividend":
    return True
  else:
    return False


@bot.message_handler(func=dividend_request)
def send_dividend(message):
  request = message.text.split()[1]
  data = get_dividends(request,'2017','2021')
  if data.size > 0:
    print(data.to_string())
    bot.send_message(message.chat.id, data['dividend'].to_string(header=False))
  else:
    bot.send_message(message.chat.id, "No dividend recorded for the specified ticker.")


#summary
def summary_request(message):
  request = message.text.split()
  if request[0].lower() == "summary":
    return True
  else:
    return False


@bot.message_handler(func=summary_request)
def send_summary(message):
  request = message.text.split()[1]
  ticker = yf.Ticker(request)
  data = ticker.info
  data = data['longBusinessSummary']
  bot.send_message(message.chat.id, data)


#yahoo page request
def yahoo_request(message):
  request = message.text.split()
  if request[0].lower() == "yahoo":
    return True
  else:
    return False


@bot.message_handler(func=yahoo_request)
def send_yahoo_page(message):
  request = message.text.split()[1]
  link = 'https://ca.finance.yahoo.com/quote/{}?p={}&.tsrc=fin-srch'.format(request,request)
  bot.send_message(message.chat.id, link)


#marketcap
def marketcap_request(message):
  request = message.text.split()
  if request[0].lower() == "cap":
    return True
  else:
    return False


@bot.message_handler(func=marketcap_request)
def send_marketcap(message):
  request = message.text.split()[1]
  data = get_quote_data(request)
  name = data['shortName']
  marketcap = data['marketCap']
  marketcap = float(marketcap)
  marketcap = ("{}'s current marketcap is at: ${:,.2f}".format(name,marketcap))
  bot.send_message(message.chat.id, marketcap)


#news
from yahoo_fin import news
def news_request(message):
  request = message.text.split()
  if request[0].lower() == "news":
    return True
  else:
    return error(message)


@bot.message_handler(func=news_request)
def send_news(message):
  request = message.text.split()[1]
  rss = []
  for i in news.get_yf_rss(request):
    rss.append(i['link'])
  bot.send_message(message.chat.id, rss[0])
  bot.send_message(message.chat.id, rss[1])
  bot.send_message(message.chat.id, rss[2])


bot.polling()
