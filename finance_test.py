import yfinance as yf
t = yf.Ticker("DOGE-USD")
hist = t.history(period="1d", interval="1m")
print(hist.tail(1)["Close"])