#!/usr/bin/env python3
"""
Тест доступности тикеров
"""

from api_client import coingecko_client
from config import TICKER_MAPPING

def test_tickers():
    """Тестируем доступность всех тикеров"""
    print("🔄 Проверяем доступность тикеров...")
    
    all_coin_ids = list(TICKER_MAPPING.values())
    print(f"Тестируем {len(all_coin_ids)} тикеров: {all_coin_ids}")
    
    # Получаем данные
    market_data = coingecko_client.get_current_prices(all_coin_ids)
    
    print(f"\nПолучены данные для {len(market_data)} тикеров:")
    
    for symbol, coin_id in TICKER_MAPPING.items():
        if coin_id in market_data:
            data = market_data[coin_id]
            price = data.get('usd', 0)
            change_24h = data.get('usd_24h_change', 0)
            print(f"✅ {symbol:5} ({coin_id:15}): ${price:10,.4f} ({change_24h:+6.2f}%)")
        else:
            print(f"❌ {symbol:5} ({coin_id:15}): НЕТ ДАННЫХ")
    
    print(f"\n📊 Итого: {len(market_data)}/{len(all_coin_ids)} тикеров доступны")

if __name__ == "__main__":
    test_tickers()
