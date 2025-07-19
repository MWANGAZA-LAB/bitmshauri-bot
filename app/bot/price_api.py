import requests
# from app import app

def get_bitcoin_price():
    try:
        params = {'ids': 'bitcoin', 'vs_currencies': 'usd,kes'}
        gecko_api_url = "https://api.coingecko.com/api/v3/simple/price"
        response = requests.get(gecko_api_url, params=params)
        data = response.json()
        btc = data['bitcoin']
        return f"🏷️ *Bei ya Bitcoin sasa:*\nUSD: ${btc['usd']:,}\nKES: KSh {btc['kes']:,}"
    except:
        return "Samahani, bei haipatikani kwa sasa. Tafadhali jaribu tena baadaye."