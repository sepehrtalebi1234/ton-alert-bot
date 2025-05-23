import requests
import time
from datetime import datetime, timedelta

# اطلاعات تلگرام
TELEGRAM_BOT_TOKEN = '7298026834:AAEwedBFU0yS5gFTHeAbKaJozb1ZZ_4JVNI'
TELEGRAM_CHAT_ID = '7259307476'

# متغیرهای اولیه
last_signal = None
last_status_time = datetime.utcnow() - timedelta(hours=12)

# ارسال پیام به تلگرام
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=data)

# دریافت قیمت از API نوبیتکس
def fetch_price(symbol):
    url = f'https://api.nobitex.ir/market/stats'
    response = requests.post(url, data={'srcCurrency': symbol.split('/')[0], 'dstCurrency': symbol.split('/')[1]})
    return float(response.json()['stats'][symbol.replace('/', '')]['latest'])

# تحلیل MA ساده
def moving_average(prices, window):
    return sum(prices[-window:]) / window

# اجرای ربات
def run_bot():
    prices_ton_usdt = []
    prices_ton_irt = []
    prices_usdt_irt = []

    while True:
        try:
            # قیمت‌ها
            ton_usdt = fetch_price("ton/usdt")
            ton_irt = fetch_price("ton/irt")
            usdt_irt = fetch_price("usdt/irt")

            # اضافه به لیست
            prices_ton_usdt.append(ton_usdt)
            prices_ton_irt.append(ton_irt)
            prices_usdt_irt.append(usdt_irt)

            # نگه‌داشتن فقط 20 داده آخر
            if len(prices_ton_usdt) > 20:
                prices_ton_usdt.pop(0)
                prices_ton_irt.pop(0)
                prices_usdt_irt.pop(0)

            # محاسبه MA و بررسی سیگنال
            if len(prices_ton_usdt) >= 20:
                ma5 = moving_average(prices_ton_usdt, 5)
                ma20 = moving_average(prices_ton_usdt, 20)
                global last_signal

                if ma5 > ma20 and last_signal != "buy":
                    send_telegram(f"📈 سیگنال خرید: TON/USDT در {ton_usdt}$ (معادل حدودی {ton_irt} تومان)")
                    last_signal = "buy"

                elif ma5 < ma20 and last_signal != "sell":
                    send_telegram(f"📉 سیگنال فروش: TON/USDT در {ton_usdt}$ (معادل حدودی {ton_irt} تومان)")
                    last_signal = "sell"

            # پیام وضعیت هر ۱۲ ساعت
            global last_status_time
            if datetime.utcnow() - last_status_time >= timedelta(hours=12):
                send_telegram("✅ ربات فعال است و بازار در حال بررسی است.")
                last_status_time = datetime.utcnow()

            time.sleep(600)  # هر 10 دقیقه بررسی شود

        except Exception as e:
            send_telegram(f"❗ خطا: {e}")
            time.sleep(600)

# اجرای ربات
run_bot()
