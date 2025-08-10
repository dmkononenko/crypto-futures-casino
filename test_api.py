#!/usr/bin/env python3
"""
Тест API CoinGecko
"""

from api_client import coingecko_client

def test_api():
    """Тестируем API ключ и соединение"""
    print("🔄 Тестируем API CoinGecko...")
    
    # Тест 1: Получение цены Bitcoin
    print("\n1. Тестируем получение цены Bitcoin...")
    btc_price = coingecko_client.get_current_prices(['bitcoin'])
    if btc_price:
        print(f"✅ Bitcoin цена: ${btc_price['bitcoin']['usd']:,.2f}")
    else:
        print("❌ Ошибка получения цены Bitcoin")
        return False
    
    # Тест 2: Получение исторических данных
    print("\n2. Тестируем исторические данные для Bitcoin...")
    historical = coingecko_client.get_historical_data('bitcoin', days=1)
    if historical and 'prices' in historical:
        prices_count = len(historical['prices'])
        print(f"✅ Получено {prices_count} точек исторических данных")
    else:
        print("❌ Ошибка получения исторических данных")
        return False
    
    # Тест 3: Рыночные данные
    print("\n3. Тестируем рыночные данные...")
    market_data = coingecko_client.get_market_data(['bitcoin', 'ethereum'])
    if market_data and len(market_data) > 0:
        print(f"✅ Получены рыночные данные для {len(market_data)} монет")
        for coin in market_data:
            print(f"   - {coin['name']}: ${coin['current_price']:,.2f}")
    else:
        print("❌ Ошибка получения рыночных данных")
        return False
    
    print("\n🎉 Все тесты пройдены! API работает корректно.")
    return True

if __name__ == "__main__":
    try:
        test_api()
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        print("Проверьте API ключ и подключение к интернету")
