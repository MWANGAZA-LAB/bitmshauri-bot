"""Advanced Bitcoin calculator with multiple conversion options."""

import re
from typing import Dict, Optional

from app.services.price_service import price_monitor
from app.utils.logger import logger


class BitcoinCalculator:
    """Advanced Bitcoin calculator with multiple conversion options."""

    def __init__(self):
        """Initialize the Bitcoin calculator."""
        self.supported_currencies = {
            "USD": {"symbol": "$", "name": "US Dollar"},
            "KES": {"symbol": "KSh", "name": "Kenyan Shilling"},
        }

    async def parse_calculation_request(self, text: str) -> Optional[Dict]:
        """Parse user input for calculation requests."""
        try:
            text = text.lower().strip()

            # Patterns for different calculation types
            patterns = [
                # "1000 kes to btc" or "1000 shillings to bitcoin"
                r"(\d+(?:\.\d+)?)\s*(?:kes|ksh|shillings?)\s*(?:to|into|=|in)\s*(?:btc|bitcoin)",
                # "500 usd to btc" or "500 dollars to bitcoin"
                r"(\d+(?:\.\d+)?)\s*(?:usd|dollars?)\s*(?:to|into|=|in)\s*(?:btc|bitcoin)",
                # "0.001 btc to kes" or "0.001 bitcoin to shillings"
                r"(\d+(?:\.\d+)?)\s*(?:btc|bitcoin)\s*(?:to|into|=|in)\s*(?:kes|ksh|shillings?)",
                # "0.001 btc to usd" or "0.001 bitcoin to dollars"
                r"(\d+(?:\.\d+)?)\s*(?:btc|bitcoin)\s*(?:to|into|=|in)\s*(?:usd|dollars?)",
                # "bitcoin price in kes" or "btc price in shillings"
                r"(?:bitcoin|btc)\s*price\s*(?:in|to)\s*(?:kes|ksh|shillings?)",
                # "bitcoin price in usd" or "btc price in dollars"
                r"(?:bitcoin|btc)\s*price\s*(?:in|to)\s*(?:usd|dollars?)",
            ]

            for i, pattern in enumerate(patterns):
                match = re.search(pattern, text)
                if match:
                    if i == 0:  # KES to BTC
                        return {
                            "type": "fiat_to_btc",
                            "amount": float(match.group(1)),
                            "from_currency": "KES",
                        }
                    elif i == 1:  # USD to BTC
                        return {
                            "type": "fiat_to_btc",
                            "amount": float(match.group(1)),
                            "from_currency": "USD",
                        }
                    elif i == 2:  # BTC to KES
                        return {
                            "type": "btc_to_fiat",
                            "amount": float(match.group(1)),
                            "to_currency": "KES",
                        }
                    elif i == 3:  # BTC to USD
                        return {
                            "type": "btc_to_fiat",
                            "amount": float(match.group(1)),
                            "to_currency": "USD",
                        }
                    elif i == 4:  # BTC price in KES
                        return {
                            "type": "price_in_currency",
                            "currency": "KES",
                        }
                    elif i == 5:  # BTC price in USD
                        return {
                            "type": "price_in_currency",
                            "currency": "USD",
                        }

            return None

        except Exception as e:
            logger.log_error(e, {"operation": "parse_calculation_request"})
            return None

    async def calculate(self, text: str) -> Optional[Dict]:
        """Perform Bitcoin calculation based on user input."""
        try:
            # Parse the calculation request
            calc_request = await self.parse_calculation_request(text)
            if not calc_request:
                return None

            # Get current Bitcoin price
            price_data = await price_monitor.get_current_price()
            if not price_data:
                return None

            btc_price_usd = price_data.get("usd", 0)
            btc_price_kes = price_data.get("kes", 0)

            if calc_request["type"] == "fiat_to_btc":
                amount = calc_request["amount"]
                from_currency = calc_request["from_currency"]

                if from_currency == "USD":
                    btc_amount = amount / btc_price_usd
                    result = {
                        "type": "fiat_to_btc",
                        "input_amount": amount,
                        "input_currency": "USD",
                        "btc_amount": btc_amount,
                        "btc_price_usd": btc_price_usd,
                        "formatted": f"${amount:,.2f} = {btc_amount:.8f} BTC",
                    }
                elif from_currency == "KES":
                    btc_amount = amount / btc_price_kes
                    result = {
                        "type": "fiat_to_btc",
                        "input_amount": amount,
                        "input_currency": "KES",
                        "btc_amount": btc_amount,
                        "btc_price_kes": btc_price_kes,
                        "formatted": f"KSh {amount:,.2f} = {btc_amount:.8f} BTC",
                    }

            elif calc_request["type"] == "btc_to_fiat":
                btc_amount = calc_request["amount"]
                to_currency = calc_request["to_currency"]

                if to_currency == "USD":
                    fiat_amount = btc_amount * btc_price_usd
                    result = {
                        "type": "btc_to_fiat",
                        "btc_amount": btc_amount,
                        "output_amount": fiat_amount,
                        "output_currency": "USD",
                        "btc_price_usd": btc_price_usd,
                        "formatted": f"{btc_amount:.8f} BTC = ${fiat_amount:,.2f}",
                    }
                elif to_currency == "KES":
                    fiat_amount = btc_amount * btc_price_kes
                    result = {
                        "type": "btc_to_fiat",
                        "btc_amount": btc_amount,
                        "output_amount": fiat_amount,
                        "output_currency": "KES",
                        "btc_price_kes": btc_price_kes,
                        "formatted": f"{btc_amount:.8f} BTC = KSh {fiat_amount:,.2f}",
                    }

            elif calc_request["type"] == "price_in_currency":
                currency = calc_request["currency"]
                if currency == "USD":
                    result = {
                        "type": "price_in_currency",
                        "currency": "USD",
                        "price": btc_price_usd,
                        "formatted": f"Bitcoin Price: ${btc_price_usd:,.2f}",
                    }
                elif currency == "KES":
                    result = {
                        "type": "price_in_currency",
                        "currency": "KES",
                        "price": btc_price_kes,
                        "formatted": f"Bitcoin Price: KSh {btc_price_kes:,.2f}",
                    }

            # Add additional information
            result["timestamp"] = price_data.get("timestamp")
            result["price_change_24h"] = price_data.get("price_change_24h", 0)
            result["market_cap"] = price_data.get("market_cap", 0)

            return result

        except Exception as e:
            logger.log_error(e, {"operation": "calculate"})
            return None

    def format_calculation_result(self, result: Dict, language: str = "sw") -> str:
        """Format calculation result for display."""
        try:
            if not result:
                return "Samahani, sijaweza kufanya hesabu hiyo."

            calc_type = result.get("type")
            formatted = result.get("formatted", "")

            if language == "sw":
                if calc_type == "fiat_to_btc":
                    return (
                        f"💰 **Hesabu ya Bitcoin**\n\n"
                        f"{formatted}\n\n"
                        f"📊 Bei ya Bitcoin: ${result.get('btc_price_usd', 0):,.2f}\n"
                        f"📈 Mabadiliko (24h): {result.get('price_change_24h', 0):+.2f}%\n"
                        f"💡 *Kidokezo: Bei ya Bitcoin inabadilika kila wakati*"
                    )
                elif calc_type == "btc_to_fiat":
                    return (
                        f"💰 **Hesabu ya Bitcoin**\n\n"
                        f"{formatted}\n\n"
                        f"📊 Bei ya Bitcoin: ${result.get('btc_price_usd', 0):,.2f}\n"
                        f"📈 Mabadiliko (24h): {result.get('price_change_24h', 0):+.2f}%\n"
                        f"💡 *Kidokezo: Bei ya Bitcoin inabadilika kila wakati*"
                    )
                elif calc_type == "price_in_currency":
                    return (
                        f"💰 **Bei ya Bitcoin**\n\n"
                        f"{formatted}\n\n"
                        f"📈 Mabadiliko (24h): {result.get('price_change_24h', 0):+.2f}%\n"
                        f"💡 *Kidokezo: Bei ya Bitcoin inabadilika kila wakati*"
                    )
            else:  # English
                if calc_type == "fiat_to_btc":
                    return (
                        f"💰 **Bitcoin Calculation**\n\n"
                        f"{formatted}\n\n"
                        f"📊 Bitcoin Price: ${result.get('btc_price_usd', 0):,.2f}\n"
                        f"📈 Change (24h): {result.get('price_change_24h', 0):+.2f}%\n"
                        f"💡 *Tip: Bitcoin price changes constantly*"
                    )
                elif calc_type == "btc_to_fiat":
                    return (
                        f"💰 **Bitcoin Calculation**\n\n"
                        f"{formatted}\n\n"
                        f"📊 Bitcoin Price: ${result.get('btc_price_usd', 0):,.2f}\n"
                        f"📈 Change (24h): {result.get('price_change_24h', 0):+.2f}%\n"
                        f"💡 *Tip: Bitcoin price changes constantly*"
                    )
                elif calc_type == "price_in_currency":
                    return (
                        f"💰 **Bitcoin Price**\n\n"
                        f"{formatted}\n\n"
                        f"📈 Change (24h): {result.get('price_change_24h', 0):+.2f}%\n"
                        f"💡 *Tip: Bitcoin price changes constantly*"
                    )

            return formatted

        except Exception as e:
            logger.log_error(e, {"operation": "format_calculation_result"})
            return "Samahani, kuna tatizo kiufundi. Jaribu tena."

    def get_supported_currencies(self) -> Dict:
        """Get list of supported currencies."""
        return self.supported_currencies

    def validate_amount(self, amount: float) -> bool:
        """Validate calculation amount."""
        try:
            return 0 < amount <= 1e12  # Reasonable range
        except (ValueError, TypeError):
            return False

    def get_calculation_examples(self, language: str = "sw") -> str:
        """Get calculation examples for user guidance."""
        if language == "sw":
            return (
                "📝 **Mifano ya Hesabu:**\n\n"
                "• `1000 kes to btc` - Badilisha shilingi 1000 kuwa Bitcoin\n"
                "• `500 usd to btc` - Badilisha dola 500 kuwa Bitcoin\n"
                "• `0.001 btc to kes` - Badilisha Bitcoin 0.001 kuwa shilingi\n"
                "• `0.001 btc to usd` - Badilisha Bitcoin 0.001 kuwa dola\n"
                "• `bitcoin price in kes` - Onyesha bei ya Bitcoin kwa shilingi\n"
                "• `btc price in usd` - Onyesha bei ya Bitcoin kwa dola\n\n"
                "💡 *Andika hesabu yako kwa lugha rahisi!*"
            )
        else:
            return (
                "📝 **Calculation Examples:**\n\n"
                "• `1000 kes to btc` - Convert 1000 shillings to Bitcoin\n"
                "• `500 usd to btc` - Convert 500 dollars to Bitcoin\n"
                "• `0.001 btc to kes` - Convert 0.001 Bitcoin to shillings\n"
                "• `0.001 btc to usd` - Convert 0.001 Bitcoin to dollars\n"
                "• `bitcoin price in kes` - Show Bitcoin price in shillings\n"
                "• `btc price in usd` - Show Bitcoin price in dollars\n\n"
                "💡 *Write your calculation in simple language!*"
            )


# Global calculator instance
bitcoin_calculator = BitcoinCalculator()