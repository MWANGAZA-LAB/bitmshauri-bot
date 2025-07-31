import re
from typing import Optional, Dict, Tuple
from app.services.price_service import price_monitor
from app.utils.logger import logger

class BitcoinCalculator:
    """Advanced Bitcoin calculator with multiple conversion options"""
    
    def __init__(self):
        self.supported_currencies = {
            'USD': {'symbol': '$', 'name': 'US Dollar'},
            'KES': {'symbol': 'KSh', 'name': 'Kenyan Shilling'}
        }
    
    async def parse_calculation_request(self, text: str) -> Optional[Dict]:
        """Parse user input for calculation requests"""
        try:
            text = text.lower().strip()
            
            # Patterns for different calculation types
            patterns = [
                # "1000 kes to btc" or "1000 shillings to bitcoin"
                r'(\d+(?:\.\d+)?)\s*(?:kes|ksh|shillings?)\s*(?:to|into|=|in)\s*(?:btc|bitcoin)',
                # "500 usd to btc" or "500 dollars to bitcoin"
                r'(\d+(?:\.\d+)?)\s*(?:usd|dollars?)\s*(?:to|into|=|in)\s*(?:btc|bitcoin)',
                # "0.001 btc to kes" or "0.001 bitcoin to shillings"
                r'(\d+(?:\.\d+)?)\s*(?:btc|bitcoin)\s*(?:to|into|=|in)\s*(?:kes|ksh|shillings?)',
                # "0.001 btc to usd" or "0.001 bitcoin to dollars"
                r'(\d+(?:\.\d+)?)\s*(?:btc|bitcoin)\s*(?:to|into|=|in)\s*(?:usd|dollars?)',
                # "bitcoin price in kes" or "btc price in shillings"
                r'(?:bitcoin|btc)\s*price\s*(?:in|to)\s*(?:kes|ksh|shillings?)',
                # "bitcoin price in usd" or "btc price in dollars"
                r'(?:bitcoin|btc)\s*price\s*(?:in|to)\s*(?:usd|dollars?)',
            ]
            
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, text)
                if match:
                    if i == 0:  # KES to BTC
                        return {
                            'type': 'fiat_to_btc',
                            'amount': float(match.group(1)),
                            'from_currency': 'KES'
                        }
                    elif i == 1:  # USD to BTC
                        return {
                            'type': 'fiat_to_btc',
                            'amount': float(match.group(1)),
                            'from_currency': 'USD'
                        }
                    elif i == 2:  # BTC to KES
                        return {
                            'type': 'btc_to_fiat',
                            'amount': float(match.group(1)),
                            'to_currency': 'KES'
                        }
                    elif i == 3:  # BTC to USD
                        return {
                            'type': 'btc_to_fiat',
                            'amount': float(match.group(1)),
                            'to_currency': 'USD'
                        }
                    elif i == 4:  # Bitcoin price in KES
                        return {
                            'type': 'price_check',
                            'currency': 'KES'
                        }
                    elif i == 5:  # Bitcoin price in USD
                        return {
                            'type': 'price_check',
                            'currency': 'USD'
                        }
            
            return None
            
        except Exception as e:
            logger.log_error(e, {"operation": "parse_calculation_request", "text": text})
            return None
    
    async def calculate_fiat_to_btc(self, amount: float, currency: str) -> Optional[Dict]:
        """Convert fiat currency to Bitcoin"""
        try:
            current_prices = await price_monitor.get_current_price()
            if not current_prices or currency not in current_prices:
                return None
            
            btc_price = current_prices[currency]
            btc_amount = amount / btc_price
            
            # Calculate additional info
            satoshis = btc_amount * 100_000_000  # 1 BTC = 100M satoshis
            
            return {
                'fiat_amount': amount,
                'fiat_currency': currency,
                'btc_amount': btc_amount,
                'satoshis': int(satoshis),
                'btc_price': btc_price,
                'calculation_type': 'fiat_to_btc'
            }
            
        except Exception as e:
            logger.log_error(e, {
                "operation": "calculate_fiat_to_btc",
                "amount": amount,
                "currency": currency
            })
            return None
    
    async def calculate_btc_to_fiat(self, btc_amount: float, currency: str) -> Optional[Dict]:
        """Convert Bitcoin to fiat currency"""
        try:
            current_prices = await price_monitor.get_current_price()
            if not current_prices or currency not in current_prices:
                return None
            
            btc_price = current_prices[currency]
            fiat_amount = btc_amount * btc_price
            
            # Calculate additional info
            satoshis = btc_amount * 100_000_000
            
            return {
                'btc_amount': btc_amount,
                'fiat_amount': fiat_amount,
                'fiat_currency': currency,
                'satoshis': int(satoshis),
                'btc_price': btc_price,
                'calculation_type': 'btc_to_fiat'
            }
            
        except Exception as e:
            logger.log_error(e, {
                "operation": "calculate_btc_to_fiat",
                "btc_amount": btc_amount,
                "currency": currency
            })
            return None
    
    def format_calculation_result(self, result: Dict) -> str:
        """Format calculation result into user-friendly message"""
        try:
            if not result:
                return "Samahani, haikuweza kuhesabu. Tafadhali jaribu tena."
            
            currency_info = self.supported_currencies.get(result.get('fiat_currency', 'USD'))
            symbol = currency_info['symbol'] if currency_info else ''
            
            if result['calculation_type'] == 'fiat_to_btc':
                message = (
                    f"🧮 *Hesabu ya Bitcoin:*\n\n"
                    f"💰 *Kiasi:* {symbol}{result['fiat_amount']:,.2f} {result['fiat_currency']}\n"
                    f"₿ *Bitcoin:* {result['btc_amount']:.8f} BTC\n"
                    f"⚡ *Satoshi:* {result['satoshis']:,} sats\n\n"
                    f"📊 *Bei ya Bitcoin:* {symbol}{result['btc_price']:,.0f}\n"
                    f"🕒 *Hesabu ya sasa*"
                )
            
            elif result['calculation_type'] == 'btc_to_fiat':
                message = (
                    f"🧮 *Hesabu ya Bitcoin:*\n\n"
                    f"₿ *Bitcoin:* {result['btc_amount']:.8f} BTC\n"
                    f"💰 *Thamani:* {symbol}{result['fiat_amount']:,.2f} {result['fiat_currency']}\n"
                    f"⚡ *Satoshi:* {result['satoshis']:,} sats\n\n"
                    f"📊 *Bei ya Bitcoin:* {symbol}{result['btc_price']:,.0f}\n"
                    f"🕒 *Hesabu ya sasa*"
                )
            
            else:
                message = "Samahani, aina ya hesabu haijulikani."
            
            # Add helpful tip
            message += (
                f"\n\n💡 *Vidokezo vya Hesabu:*\n"
                f"• Andika: '1000 kes to btc'\n"
                f"• Au: '0.001 btc to kes'\n"
                f"• Au: 'bitcoin price in usd'"
            )
            
            return message
            
        except Exception as e:
            logger.log_error(e, {"operation": "format_calculation_result"})
            return "Kuna tatizo la kuonyesha matokeo. Tafadhali jaribu tena."
    
    async def get_price_comparison(self) -> str:
        """Get Bitcoin price comparison across currencies"""
        try:
            current_prices = await price_monitor.get_current_price()
            if not current_prices:
                return "Samahani, bei haipatikani kwa sasa."
            
            message = (
                f"💱 *Ulinganishi wa Bei ya Bitcoin:*\n\n"
                f"🇺🇸 *USD:* ${current_prices.get('USD', 0):,.0f}\n"
                f"🇰🇪 *KES:* KSh {current_prices.get('KES', 0):,.0f}\n\n"
                f"📊 *Kipimo cha Satoshi:*\n"
                f"• 1 sat = ${current_prices.get('USD', 0) / 100_000_000:.6f}\n"
                f"• 1 sat = KSh {current_prices.get('KES', 0) / 100_000_000:.4f}\n\n"
                f"🧮 *Hesabu Rahisi:*\n"
                f"• $1 = {1 / current_prices.get('USD', 1) * 100_000_000:.0f} sats\n"
                f"• KSh 100 = {100 / current_prices.get('KES', 1) * 100_000_000:.0f} sats"
            )
            
            return message
            
        except Exception as e:
            logger.log_error(e, {"operation": "get_price_comparison"})
            return "Kuna tatizo la kupata ulinganishi wa bei."

# Global calculator instance
bitcoin_calculator = BitcoinCalculator()

async def process_calculation_request(text: str, user_id: int) -> str:
    """Process user calculation request"""
    try:
        # Log the calculation request
        logger.log_user_action(user_id, 'calculator_request', {'query': text})
        
        # Parse the request
        calculation_request = await bitcoin_calculator.parse_calculation_request(text)
        
        if not calculation_request:
            return (
                "🧮 *Hoja ya Hesabu*\n\n"
                "Andika moja ya hizi:\n"
                "• '1000 kes to btc' - Badilisha KES kuwa Bitcoin\n"
                "• '0.001 btc to kes' - Badilisha Bitcoin kuwa KES\n"
                "• '500 usd to btc' - Badilisha USD kuwa Bitcoin\n"
                "• '0.002 btc to usd' - Badilisha Bitcoin kuwa USD\n"
                "• 'bitcoin price' - Bei ya Bitcoin\n\n"
                "Pia unaweza kutumia: /calculate au /calc"
            )
        
        # Handle different calculation types
        if calculation_request['type'] == 'fiat_to_btc':
            result = await bitcoin_calculator.calculate_fiat_to_btc(
                calculation_request['amount'],
                calculation_request['from_currency']
            )
        elif calculation_request['type'] == 'btc_to_fiat':
            result = await bitcoin_calculator.calculate_btc_to_fiat(
                calculation_request['amount'],
                calculation_request['to_currency']
            )
        elif calculation_request['type'] == 'price_check':
            return await bitcoin_calculator.get_price_comparison()
        else:
            return "Aina ya hesabu haijulikani."
        
        # Format and return result
        formatted_result = bitcoin_calculator.format_calculation_result(result)
        
        # Log successful calculation
        logger.log_user_action(user_id, 'calculator_success', {
            'request_type': calculation_request['type'],
            'result': result
        })
        
        return formatted_result
        
    except Exception as e:
        logger.log_error(e, {"operation": "process_calculation_request", "user_id": user_id})
        return "Samahani, kuna tatizo la kuhesabu. Tafadhali jaribu tena."
