import telebot
import yfinance as yf
import pandas as pd
import time
import os

# Получаем токен из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Создаём бота
bot = telebot.TeleBot(BOT_TOKEN)

# Список акций для сканирования
STOCKS_TO_SCAN = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA']

def calculate_rsi(prices, period=14):
    """Расчёт RSI (индекс относительной силы)"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@bot.message_handler(commands=['start'])
def start(message):
    """Обработчик команды /start"""
    bot.reply_to(message, "Привет! Я RSI бот. Отправь /scan для поиска перекупленных и перепроданных акций")

@bot.message_handler(commands=['scan'])
def scan(message):
    """Обработчик команды /scan - сканирование акций"""
    bot.reply_to(message, "🔍 Сканирую акции... Это займёт около минуты")
    
    overbought = []  # Перекупленные (RSI > 70)
    oversold = []    # Перепроданные (RSI < 30)
    
    for ticker in STOCKS_TO_SCAN:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1mo")
            
            if len(hist) > 14:
                rsi_values = calculate_rsi(hist['Close'])
                current_rsi = rsi_values.iloc[-1]
                current_price = hist['Close'].iloc[-1]
                
                if current_rsi > 70:
                    overbought.append(f"🔴 {ticker}: ${current_price:.2f} (RSI: {current_rsi:.1f})")
                elif current_rsi < 30:
                    oversold.append(f"🟢 {ticker}: ${current_price:.2f} (RSI: {current_rsi:.1f})")
            
            time.sleep(0.5)  # Задержка между запросами
        except Exception as e:
            print(f"Ошибка с {ticker}: {e}")
    
    # Формируем результат
    result = "📊 **РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ**\n\n"
    result += "**ПЕРЕКУПЛЕННЫЕ (RSI > 70):**\n"
    result += "\n".join(overbought) if overbought else "Нет перекупленных акций"
    result += "\n\n**ПЕРЕПРОДАННЫЕ (RSI < 30):**\n"
    result += "\n".join(oversold) if oversold else "Нет перепроданных акций"
    
    bot.reply_to(message, result, parse_mode="Markdown")

# Запуск бота с защитой от ошибок
if __name__ == "__main__":
    print("✅ Бот запущен и слушает команды...")
    print(f"📊 Отслеживается акций: {len(STOCKS_TO_SCAN)}")
    
    # Бесконечный цикл с обработкой возможных ошибок
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"❌ Бот упал с ошибкой: {e}")
            print("🔄 Перезапуск через 5 секунд...")
            time.sleep(5)
