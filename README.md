# ================== Whale Monitor - سبحان v4 (Hyperliquid, 50 whales) ==================
# مانیتور پوزیشن‌های فیوچرز Hyperliquid برای 50 نهنگ (نسخه‌ی Scheduled Task / GitHub Actions)
# تک اجرا (هر زمان که کرون اجرا کنه یک دور چک می‌کنه). شامل پیام Alive هر 30 دقیقه.
# pip install requests

import requests
import json
from datetime import datetime, timedelta

# ================== تنظیمات ==================
BOT_TOKEN = "8396611567:AAElTnh8kD9UPtJ35S0rHT7BEUgaevA4EEc"  # توکن ربات (همینی که دادی)
CHAT_ID = "7921910205"  # آیدی عددی چت (همینی که دادی)

HYPER_URL = "https://api.hyperliquid.xyz/info"
USD_FILTER_MIN = 10_000.0     # فیلتر حداقل تراکنش دلاری
LOG_FILE = "signals.json"     # فایل ذخیره لاگ محلی

# ================== لیست 50 نهنگ (نمونه) ==================
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
    "0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2",
    "0x742d35cc6634c0532925a3b844bc454e4438f44e",
    "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0",
    "0x28c6c06298d514db089934071355e5743bf21d60",
    "0xf977814e90da44bfa03b6295a0616a897441acec",
    "0x5a52e96bacdabb82fd05763e25335261b270efcb",
    "0x742d35cc6634c0532925a3b844bc454e4438f44f",
    "0x8ee7d9235e01e6b42345120b5d270bdb763624c7",
    "0x66f820a414680b5bcda5eeca5dea238543f42054",
    "0xbc47b5f1a1f77d5a8b19d3f8bb4b4ea3e65b1a7a",
    "0x0a57ef8b1b3f0f28a2b6a5d4e5f9c6a1b2c3d4e5",
    "0x1a2b3c4d5e6f7081928374655647382918273645",
    "0xabcdefabcdefabcdefabcdefabcdefabcdefabcd",
    "0x0123456789abcdef0123456789abcdef01234567",
    "0xa0df350d2637096571f7a701cbc1c5fdc5fa5b5d",
    "0xbe0eb53f46cd790cd13851d5eff43d12404d33e8",
    "0x3f5ce5fbfe3e9af3971d0ef6c5b9e9b1a9a3b2b1",
    "0x2a65aca4d5fc5b5c859090a6c34d164135398226",
    "0x6b175474e89094c44da98b954eedeac495271d0f",
    "0x00000000219ab540356cBB839Cbe05303d7705Fa",
    "0x7ef2e0048f5bAeDe046f6BF797943daF4ED8CB47",
    "0x281055afc982d96fab65b3a49cac8b878184cb16",
    "0x66f820a414680b5bcda5eeca5dea238543f42055",
    "0x5aeda56215b167893e80b4fe645ba6d5bab767de",
    "0x4e9ce36e442e55ecd9025b9a6e0d88485d628a67",
    "0x0d8775f648430679a709e98d2b0cb6250d2887ef",
    "0x742d35cc6634c0532925a3b844bc454e4438f449",
]
WHALES = [w.lower() for w in WHALES]

# ================== helpers ==================
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
        r = requests.post(url, data=payload, timeout=10)
        # چاپ برای لاگ GitHub Actions
        print("Telegram status:", r.status_code, r.text)
    except Exception as e:
        print("Telegram send error:", e)

def save_signal(data: dict):
    try:
        try:
            with open(LOG_FILE, "r") as f:
                all_data = json.load(f)
        except Exception:
            all_data = []
        all_data.append(data)
        with open(LOG_FILE, "w") as f:
            json.dump(all_data, f, indent=2)
    except Exception as e:
        print("Save error:", e)

# ================== Hyperliquid checker ==================
def check_hyper_positions():
    found = 0
    alerts = []
    for addr in WHALES:
        try:
            payload = {"type": "clearinghouseState", "user": addr}
            r = requests.post(HYPER_URL, json=payload, timeout=8)
            if r.status_code != 200:
                # برای دیباگ لاگ کن
                print(f"Hyper API non-200 for {addr}: {r.status_code}")
                continue
            data = r.json()
        except Exception as e:
            print("Request error for", addr, ":", e)
            continue

        positions = data.get("assetPositions") or []
        for item in positions:
            pos = item.get("position", {})
            if not pos:
                continue

            coin = pos.get("coin", "")
            side = pos.get("side", "").lower()
            szi = float(pos.get("szi", 0) or 0)
            notional = float(pos.get("notionalUsd", 0) or 0)
            entry = float(pos.get("entryPx", 0) or 0)
            market = float(pos.get("oraclePx", 0) or 0)
            lev = pos.get("leverage", "?")

            if szi == 0 or notional < USD_FILTER_MIN:
                continue

            now_ir = now_iran_str()
            unique_id = f"hyper|{addr}|{coin}|{side}|{entry}"
            # توجه: چون این اسکریپت به صورت تک-اجرا از کرون اجرا میشه، dedup بین اجراها ذخیره نمیشه.
            # اگر میخوای از تکرار جلوگیری کنی باید فایل یا DB نگه داری کنی (اینجا ساده نگه داشته شده).
            msg = (
                f"🛎️ *سیگنال نهنگ (Hyperliquid)*\n\n"
                f"📌 آدرس: `{addr}`\n"
                f"🕓 زمان (ایران): `{now_ir}`\n"
                f"💎 کوین: *{coin}*\n"
                f"{'🟢 خرید (Long)' if side == 'long' else '🔴 فروش (Short)'}\n"
                f"💰 حجم: *{fmt_num(abs(szi))}*\n"
                f"💲 ارزش دلاری: *${fmt_num(notional)}*\n"
                f"🎯 ورود: `${fmt_num(entry)}`\n"
                f"💹 قیمت لحظه‌ای: `${fmt_num(market)}`\n"
                f"⚡ اهرم: *{lev}*"
            )
            send_telegram(msg)
            print(f"[HYPER ALERT] {now_ir} {addr} {coin} {side} ${fmt_num(notional)}")

            save_signal({
                "type": "hyper",
                "time": now_ir,
                "addr": addr,
                "coin": coin,
                "side": side,
                "notional": notional,
                "entry": entry,
                "market": market
            })
            found += 1
            alerts.append((addr, coin, side, notional))
    return found, alerts

# ================== main (یکبار اجرا برای Scheduled Task) ==================
def main():
    print("🚀 Whale Monitor v4 (Hyperliquid only) start:", datetime.utcnow().isoformat())
    found, alerts = check_hyper_positions()

    # پیام Alive هر 30 دقیقه (اگر کرون هر 10 دقیقه و هر 30 دقیقه هر دو فعال باشند،
    # این شرط بسته به دقیقه فعلی تصمیم می‌گیرد)
    now = datetime.utcnow()
    if now.minute % 30 == 0:
        send_telegram(f"✅ Bot is alive and monitoring Hyperliquid whales. Time: {now_iran_str()}  | Signals found this run: {found}")

    print("Run finished. signals:", found)

if __name__ == "__main__":
    main()
    
