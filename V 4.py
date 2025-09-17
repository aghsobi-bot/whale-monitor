# ================== Whale Monitor - سبحان v4 (Scheduled Task) ==================
# مانیتور نهنگ‌ها (Hyperliquid + On-chain ETH/BSC) + ذخیره لاگ + Heartbeat
# نسخه‌ی مخصوص Scheduled Task → یکبار اجرا و بلافاصله خروج

import requests
import json
from datetime import datetime, timedelta
from web3 import Web3

# ================== تنظیمات ==================
BOT_TOKEN = "8396611567:AAElTnh8kD9UPtJ35S0rHT7BEUgaevA4EEc"  # 🔑 توکن ربات
CHAT_ID = "7921910205"  # 🔢 آیدی عددی چت

# آدرس نهنگ‌ها
WHALES = [
    "0x5078c2fbea2b2ad61bc840bc023e35fce56bedb6",
    "0xf3f496c9486be5924a93d67e98298733bb47057c",
    "0x7ab8c59db7b959bb8c3481d5b9836dfbc939af21",
    "0x45d26f28196d226497130c4bac709d808fed4029",
    "0xe0c8d0d390454dc98977cf53123244d74c9478c1",
    "0xdd588eeebfa4c1b0112a9efffc7f0bc8529bfb1c",
    "0x64afae722a05b1d28e831b2c20a8ebfea9da6352",
    "0x6c50446ced034fb5617b005f0775746931a9db55",
    "0x960bb18454cd67b5a3edb4fa802b7c0b5b10e2ee",
    "0x6e4a971b81ca58045a2aa982eaa3d50c4ac38f42",
    "0x6c46422a0f7dbbad9bec3bbbc1189bfaf9794b05",
    "0x4fa2e5871dd9622c515f66a4b3230b73236e0d8d",
    "0xd2f83cf5c697e892a38f8d1830eb88ebc0809a0c",
    "0xbb92b9d18db99c3695bc820bf2c876d4b1527fa5",
    "0x1d52fe9bde2694f6172192381111a91e24304397",
    "0x15b325660a1c4a9582a7d834c31119c0cb9e3a42",
    "0xebb258660bfb0385ba14625f6876dafc4b9b0a03",
    "0x7ca165f354e3260e2f8d5a7508cc9dd2fa009235",
    "0x53babe76166eae33c861aeddf9ce89af20311cd0",
    "0xb28cf8649d1cda2975d290f04ea4cc4db7b3828e",
    "0x22268f7ad3c232ac9cbb96730411c9ed24ebb239",
]
WHALES = [w.lower() for w in WHALES]

HYPER_URL = "https://api.hyperliquid.xyz/info"
ETH_RPC = "https://eth.llamarpc.com"
BSC_RPC = "https://bsc-dataseed1.binance.org"

USD_FILTER_MIN = 10_000.0     # فیلتر حداقل تراکنش
LOG_FILE = "signals.json"     # فایل ذخیره لاگ

# ================== setup web3 ==================
w3_eth = Web3(Web3.HTTPProvider(ETH_RPC))
w3_bsc = Web3(Web3.HTTPProvider(BSC_RPC))

print("ETH connected:", w3_eth.is_connected(), " BSC connected:", w3_bsc.is_connected())

# ================== helpers ==================
sent_set = set()

def now_iran_str():
    utc = datetime.utcnow()
    iran = utc + timedelta(hours=3, minutes=30)
    return iran.strftime("%Y-%m-%d %H:%M:%S IRST")

def fmt_num(x):
    try:
        x = float(x)
        if abs(x) >= 1:
            return "{:,.2f}".format(x)
        else:
            return "{:.6f}".format(x)
    except:
        return str(x)

def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=8)
    except Exception as e:
        print("Telegram send error:", e)

def save_signal(data: dict):
    """ذخیره سیگنال در فایل"""
    try:
        try:
            with open(LOG_FILE, "r") as f:
                all_data = json.load(f)
        except:
            all_data = []
        all_data.append(data)
        with open(LOG_FILE, "w") as f:
            json.dump(all_data, f, indent=2)
    except Exception as e:
        print("Save error:", e)

# ================== Hyperliquid checker ==================
def check_hyper_positions():
    for addr in WHALES:
        try:
            payload = {"type": "clearinghouseState", "user": addr}
            r = requests.post(HYPER_URL, json=payload, timeout=8)
            if r.status_code != 200:
                continue
            data = r.json()
        except Exception:
            continue

        positions = data.get("assetPositions") or []
        for item in positions:
            pos = item.get("position", {})
            if not pos:
                continue

            coin = pos.get("coin", "")
            if not coin:
                continue

            side = pos.get("side", "").lower()
            szi = float(pos.get("szi", 0))
            notional = float(pos.get("notionalUsd", 0))
            entry = float(pos.get("entryPx", 0))
            market = float(pos.get("oraclePx", 0))
            lev = pos.get("leverage", "?")

            if szi == 0 or notional < USD_FILTER_MIN:
                continue

            unique = f"hyper|{addr}|{coin}|{side}|{entry}"
            if unique in sent_set:
                continue
            sent_set.add(unique)

            now_ir = now_iran_str()
            msg = (
                f"🛎️ *سیگنال نهنگ (Hyperliquid)* \n\n"
                f"📌 آدرس: `{addr}`\n"
                f"🕓 زمان (ایران): `{now_ir}`\n"
                f"💎 کوین: *{coin}*\n"
                f"{'🟢 خرید (Long)' if side == 'long' else '🔴 فروش (Short)'}\n"
                f"💰 حجم: *{fmt_num(abs(szi))}*\n"
                f"💲 ارزش دلاری: *${fmt_num(notional)}*\n"
                f"🎯 ورود: `${fmt_num(entry)}`\n"
                f"💹 قیمت لحظه‌ای: `${fmt_num(market)}`\n"
                f"⚡ اهرم: *{lev}*\n"
            )
            send_telegram(msg)
            print(f"[HYPER ALERT] {now_ir} {addr} {coin} {side} ${fmt_num(notional)}")

            save_signal({"type": "hyper", "time": now_ir, "addr": addr, "coin": coin,
                         "side": side, "notional": notional, "entry": entry, "market": market})

# ================== main (یکبار اجرا) ==================
print("🚀 مانیتور سبحان v4 (Scheduled Task) شروع شد. آستانه: 10,000$")
check_hyper_positions()

# پیام پایان
send_telegram(f"✅ اجرای Scheduled Task تمام شد ({now_iran_str()})")
          
