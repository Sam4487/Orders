import os
from kiteconnect import KiteConnect
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

kite = KiteConnect(api_key=api_key)
access_token = None

def get_login_url():
    return kite.login_url()

def generate_session(request_token):
    global access_token
    data = kite.generate_session(request_token, api_secret=api_secret)
    access_token = data["access_token"]
    kite.set_access_token(access_token)
    return access_token

def place_order(symbol, quantity, price, exchange, order_type, transaction_type):
    quantity = int(quantity)

    if order_type == "LIMIT" and price:
        price = float(price)
    else:
        price = None

    order_id = kite.place_order(
        variety="regular",
        exchange=exchange,
        tradingsymbol=symbol,
        transaction_type=transaction_type,
        quantity=quantity,
        product="MIS",
        order_type=order_type,
        price=price
    )

    quote = kite.ltp(f"{exchange}:{symbol}")
    market_price = quote[f"{exchange}:{symbol}"]["last_price"]

    cost_price = float(price) if price else market_price
    pnl = (market_price - cost_price) * quantity
    if transaction_type == "SELL":
        pnl = -pnl

    return order_id, pnl

def get_position_pnl(symbol, exchange):
    positions = kite.positions()
    all_positions = positions['net']
    for pos in all_positions:
        if pos['tradingsymbol'].upper() == symbol.upper() and pos['exchange'] == exchange:
            return pos['unrealised']
    raise Exception(f"No open position found for {symbol} in {exchange}")
