import requests
from app import app

def get_bitcoin_price():
    try:
        params = {'ids': 'bitcoin', 'vs_currencies': 'usd,kes'}
        response = requests.get(app.config['GECKO_API_URL'], params=params)
        data = response.json()
        btc = data['bitcoin']
        return f"🏷️ *Bei ya Bitcoin sasa:*\nUSD: ${btc['usd']:,}\nKES: KSh {btc['kes']:,}"
    except:
        return "Samahani, bei haipatikani kwa sasa. Tafadhali jaribu tena baadaye."