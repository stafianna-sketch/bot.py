import telebot
import yfinance as yf
import pandas as pd
import time
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)
STOCKS_TO_SCAN = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я RSI бот. Отправь /scan для поиска акций")

@bot.message_handler(commands=['scan'])
def scan(message):
    bot.reply_to(message, "Сканирую акции... Подождите немного")
    
    overbought = []
    oversold = []
    
    for ticker in STOCKS_TO_SCAN:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            
            if len(hist) > 14:
                rsi_values = calculate_rsi(hist['Close'])
                current_rsi = rsi_values.iloc[-1]
                current_price = hist['Close'].iloc[-1]
                
                if current_rsi > 70:
                    overbought.append(f"{ticker}: ${current_price:.2f} (RSI: {current_rsi:.1f})")
                elif current_rsi < 30:
                    oversold.append(f"{ticker}: ${current_price:.2f} (RSI: {current_rsi:.1f})")
            
            time.sleep(0.5)
        except Exception as e:
            print(f"Ошибка с {ticker}: {e}")
    
    result = "📊 РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ:\n\n"
    result += "🔴 ПЕРЕКУПЛЕННЫЕ (RSI > 70):\n"
    result += "\n".join(overbought) if overbought else "Нет"
    result += "\n\n🟢 ПЕРЕПРОДАННЫЕ (RSI < 30):\n"
    result += "\n".join(oversold) if oversold else "Нет"
    
    bot.reply_to(message, result)

print("✅ Бот успешно запущен!")
bot.infinity_polling()
