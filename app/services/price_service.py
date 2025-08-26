import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.enhanced_database import get_active_price_alerts, trigger_price_alert
from app.utils.logger import logger
import json


class BitcoinPriceMonitor:
    """Advanced Bitcoin price monitoring with alerts"""

    def __init__(self):
        self.current_prices = {}
        self.price_history = []
        self.is_monitoring = False
        self.monitor_task = None

    async def get_current_price(self) -> Dict[str, float]:
        """Get current Bitcoin price from multiple sources"""
        try:
            async with aiohttp.ClientSession() as session:
                # Primary source: CoinGecko
                try:
                    async with session.get(
                        "https://api.coingecko.com/api/v3/simple/price",
                        params={"ids": "bitcoin", "vs_currencies": "usd,kes"},
                        timeout=10,
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            prices = {
                                "USD": data["bitcoin"]["usd"],
                                "KES": data["bitcoin"]["kes"],
                            }
                            self.current_prices = prices

                            # Store price history
                            self.price_history.append(
                                {
                                    "timestamp": datetime.now(),
                                    "prices": prices.copy(),
                                }
                            )

                            # Keep only last 24 hours of history
                            cutoff_time = datetime.now() - timedelta(hours=24)
                            self.price_history = [
                                entry
                                for entry in self.price_history
                                if entry["timestamp"] > cutoff_time
                            ]

                            return prices
                except Exception as e:
                    logger.log_error(e, {"source": "coingecko"})

                # Fallback source: Coinbase
                try:
                    async with session.get(
                        "https://api.coinbase.com/v2/exchange-rates",
                        params={"currency": "BTC"},
                        timeout=10,
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            usd_price = float(data["data"]["rates"]["USD"])
                            # Approximate KES rate (you might want to get real exchange rate)
                            kes_price = (
                                usd_price * 129
                            )  # Approximate USD to KES

                            prices = {"USD": usd_price, "KES": kes_price}
                            self.current_prices = prices
                            return prices
                except Exception as e:
                    logger.log_error(e, {"source": "coinbase"})

                # If both fail, return cached prices
                return self.current_prices

        except Exception as e:
            logger.log_error(e, {"operation": "get_current_price"})
            return self.current_prices

    async def check_price_alerts(self, bot):
        """Check and trigger price alerts"""
        try:
            active_alerts = get_active_price_alerts()
            if not active_alerts:
                return

            current_prices = await self.get_current_price()
            if not current_prices:
                return

            for alert in active_alerts:
                try:
                    current_price = current_prices.get(alert["currency"], 0)
                    target_price = alert["target_price"]
                    condition = alert["condition"]

                    should_trigger = False

                    if condition == "above" and current_price >= target_price:
                        should_trigger = True
                    elif (
                        condition == "below" and current_price <= target_price
                    ):
                        should_trigger = True

                    if should_trigger:
                        await self.send_price_alert(bot, alert, current_price)
                        trigger_price_alert(alert["id"])

                        logger.log_user_action(
                            alert["user_id"],
                            "price_alert_triggered",
                            {
                                "target_price": target_price,
                                "current_price": current_price,
                                "currency": alert["currency"],
                                "condition": condition,
                            },
                        )

                except Exception as e:
                    logger.log_error(
                        e,
                        {
                            "operation": "process_price_alert",
                            "alert_id": alert.get("id"),
                        },
                    )

        except Exception as e:
            logger.log_error(e, {"operation": "check_price_alerts"})

    async def send_price_alert(self, bot, alert: Dict, current_price: float):
        """Send price alert notification to user"""
        try:
            currency_symbol = "$" if alert["currency"] == "USD" else "KSh"
            condition_text = (
                "juu ya" if alert["condition"] == "above" else "chini ya"
            )

            message = (
                f"🚨 *Onyo la Bei ya Bitcoin!*\n\n"
                f"Bei ya Bitcoin imefika {currency_symbol}{current_price:,.0f} "
                f"({alert['currency']}) - {condition_text} kikomo chako cha "
                f"{currency_symbol}{alert['target_price']:,.0f}!\n\n"
                f"📊 *Taarifa za Haraka:*\n"
                f"• Lengo: {currency_symbol}{alert['target_price']:,.0f}\n"
                f"• Bei ya Sasa: {currency_symbol}{current_price:,.0f}\n"
                f"• Wakati: {datetime.now().strftime('%H:%M, %d/%m/%Y')}\n\n"
                f"💡 *Je, unataka kuweka onyo jingine?*"
            )

            await bot.send_message(
                chat_id=alert["chat_id"], text=message, parse_mode="Markdown"
            )

        except Exception as e:
            logger.log_error(
                e,
                {
                    "operation": "send_price_alert",
                    "user_id": alert.get("user_id"),
                    "chat_id": alert.get("chat_id"),
                },
            )

    def get_price_trend(self, hours: int = 24) -> Dict:
        """Analyze price trend over specified hours"""
        try:
            if len(self.price_history) < 2:
                return {"trend": "insufficient_data"}

            cutoff_time = datetime.now() - timedelta(hours=hours)
            relevant_history = [
                entry
                for entry in self.price_history
                if entry["timestamp"] > cutoff_time
            ]

            if len(relevant_history) < 2:
                return {"trend": "insufficient_data"}

            start_price = relevant_history[0]["prices"]["USD"]
            end_price = relevant_history[-1]["prices"]["USD"]

            change_percent = ((end_price - start_price) / start_price) * 100

            # Calculate volatility
            prices = [entry["prices"]["USD"] for entry in relevant_history]
            if len(prices) > 1:
                price_changes = [
                    abs(prices[i] - prices[i - 1])
                    for i in range(1, len(prices))
                ]
                avg_change = sum(price_changes) / len(price_changes)
                volatility = (avg_change / start_price) * 100
            else:
                volatility = 0

            trend = (
                "bullish"
                if change_percent > 2
                else "bearish" if change_percent < -2 else "sideways"
            )

            return {
                "trend": trend,
                "change_percent": round(change_percent, 2),
                "start_price": start_price,
                "end_price": end_price,
                "volatility": round(volatility, 2),
                "time_period": f"{hours}h",
            }

        except Exception as e:
            logger.log_error(e, {"operation": "get_price_trend"})
            return {"trend": "error"}

    async def start_monitoring(self, bot):
        """Start continuous price monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        logger.logger.info("Starting Bitcoin price monitoring")

        while self.is_monitoring:
            try:
                await self.check_price_alerts(bot)
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.log_error(e, {"operation": "price_monitoring_loop"})
                await asyncio.sleep(60)

    def stop_monitoring(self):
        """Stop price monitoring"""
        self.is_monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
        logger.logger.info("Stopped Bitcoin price monitoring")


# Global price monitor instance
price_monitor = BitcoinPriceMonitor()


# Enhanced price API functions
async def get_enhanced_bitcoin_price():
    """Get enhanced Bitcoin price with trend analysis"""
    try:
        prices = await price_monitor.get_current_price()
        if not prices:
            return "Samahani, bei haipatikani kwa sasa. Tafadhali jaribu tena baadaye."

        trend_data = price_monitor.get_price_trend(24)

        trend_emoji = {"bullish": "📈", "bearish": "📉", "sideways": "➡️"}.get(
            trend_data.get("trend", "sideways"), "➡️"
        )

        trend_text = {
            "bullish": "Inapanda",
            "bearish": "Inashuka",
            "sideways": "Imara",
        }.get(trend_data.get("trend", "sideways"), "Imara")

        message = (
            f"🏷️ *Bei ya Bitcoin Sasa:*\n"
            f"USD: ${prices['USD']:,.0f}\n"
            f"KES: KSh {prices['KES']:,.0f}\n\n"
            f"{trend_emoji} *Mwelekeo (24h):* {trend_text}\n"
        )

        if trend_data.get("change_percent") is not None:
            change = trend_data["change_percent"]
            change_emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
            message += f"{change_emoji} *Mabadiliko:* {change:+.2f}%\n"

        message += f"\n🕒 *Imesasishwa:* {datetime.now().strftime('%H:%M')}"

        return message

    except Exception as e:
        logger.log_error(e, {"operation": "get_enhanced_bitcoin_price"})
        return "Samahani, kuna tatizo la kupata bei. Tafadhali jaribu tena baadaye."
