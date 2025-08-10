#!/usr/bin/env python3
"""
Trading Randomizer - Intelligent Crypto Trading Recommendations
Использует CoinGecko API для получения реальных рыночных данных
"""

import json
import random
from datetime import datetime
from typing import Dict, List
from api_client import coingecko_client
from analyzer import technical_analyzer
from config import TICKERS, TICKER_MAPPING, LEVERAGES, DIRECTIONS

class TradingRecommendationSystem:
    def __init__(self):
        self.results_file = "results.md"
        
    def get_smart_recommendation(self, preferred_ticker: str = None) -> Dict:
        """Получить умную рекомендацию на основе анализа данных"""
        print("🔄 Получение данных с CoinGecko...")
        
        # Выбираем тикер для анализа
        if preferred_ticker and preferred_ticker.upper() in TICKER_MAPPING:
            selected_ticker = preferred_ticker.upper()
            coin_id = TICKER_MAPPING[selected_ticker]
            tickers_to_analyze = [coin_id]
        else:
            # Анализируем все тикеры и выбираем лучший
            tickers_to_analyze = TICKERS
            selected_ticker = None
        
        best_recommendation = None
        best_score = 0
        
        for coin_id in tickers_to_analyze:
            # Получаем исторические данные
            historical_data = coingecko_client.get_historical_data(coin_id, days=7)
            
            if not historical_data:
                continue
                
            # Анализируем данные
            recommendation = technical_analyzer.get_recommendation_score(historical_data)
            
            if recommendation['confidence'] > best_score:
                best_score = recommendation['confidence']
                best_recommendation = recommendation
                if not selected_ticker:
                    # Находим символ тикера по coin_id
                    selected_ticker = next(
                        (symbol for symbol, cid in TICKER_MAPPING.items() if cid == coin_id),
                        coin_id.upper()
                    )
        
        if not best_recommendation:
            return self._get_fallback_recommendation()
        
        # Получаем текущую цену
        current_price_data = coingecko_client.get_current_prices([TICKER_MAPPING[selected_ticker]])
        current_price = 0
        if current_price_data and TICKER_MAPPING[selected_ticker] in current_price_data:
            current_price = current_price_data[TICKER_MAPPING[selected_ticker]]['usd']
        
        return {
            'ticker': selected_ticker,
            'direction': best_recommendation['direction'],
            'leverage': f"x{best_recommendation['leverage']}",
            'confidence': best_recommendation['confidence'],
            'reasoning': best_recommendation['reasoning'],
            'current_price': current_price,
            'rsi': best_recommendation['rsi'],
            'volatility': best_recommendation['volatility'],
            'trend': best_recommendation['trend'],
            'price_change_24h': best_recommendation['price_change_24h']
        }
    
    def get_random_recommendation(self) -> Dict:
        """Получить случайную рекомендацию (старый метод)"""
        ticker = random.choice(list(TICKER_MAPPING.keys()))
        leverage = f"x{random.choice(LEVERAGES)}"
        direction = random.choice(DIRECTIONS)
        
        return {
            'ticker': ticker,
            'direction': direction,
            'leverage': leverage,
            'confidence': random.randint(30, 70),
            'reasoning': 'Случайная рекомендация',
            'current_price': 0,
            'rsi': 50,
            'volatility': 0,
            'trend': 'UNKNOWN',
            'price_change_24h': 0
        }
    
    def _get_fallback_recommendation(self) -> Dict:
        """Резервная рекомендация при проблемах с API"""
        return {
            'ticker': 'BTC',
            'direction': 'LONG',
            'leverage': 'x5',
            'confidence': 40,
            'reasoning': 'Консервативная рекомендация (проблемы с получением данных)',
            'current_price': 0,
            'rsi': 50,
            'volatility': 0,
            'trend': 'UNKNOWN',
            'price_change_24h': 0
        }
    
    def format_recommendation(self, rec: Dict) -> str:
        """Форматировать рекомендацию для вывода"""
        confidence_emoji = "🔥" if rec['confidence'] > 70 else "⚡" if rec['confidence'] > 50 else "🎯"
        
        output = f"""
## {confidence_emoji} **Рекомендация на {datetime.now().strftime('%d.%m.%Y')}:**

### **{rec['ticker']} + {rec['leverage']} + {rec['direction']}**

**Уверенность:** {rec['confidence']:.1f}%
**Текущая цена:** ${rec['current_price']:.4f} (изменение 24ч: {rec['price_change_24h']:+.1f}%)

**Технический анализ:**
- RSI: {rec['rsi']:.1f}
- Волатильность: {rec['volatility']:.1f}%
- Тренд: {rec['trend']}

**Обоснование:** {rec['reasoning']}

**Рекомендации по торговле:**
"""
        
        # Рекомендации по размеру позиции
        if rec['confidence'] > 70:
            output += "- Размер позиции: 3-5% от депозита\n"
        elif rec['confidence'] > 50:
            output += "- Размер позиции: 2-3% от депозита\n"
        else:
            output += "- Размер позиции: 1-2% от депозита\n"
        
        # Рекомендации по риск-менеджменту
        leverage_num = int(rec['leverage'][1:])
        if leverage_num >= 20:
            output += "- Стоп-лосс: 2-3%\n- Тейк-профит: 5-10%\n"
        elif leverage_num >= 10:
            output += "- Стоп-лосс: 4-6%\n- Тейк-профит: 10-20%\n"
        else:
            output += "- Стоп-лосс: 5-8%\n- Тейк-профит: 15-25%\n"
        
        return output

def main():
    """Основная функция"""
    system = TradingRecommendationSystem()
    
    print("🚀 Trading Randomizer - Intelligent Recommendations")
    print("=" * 50)
    
    while True:
        print("\n📊 Выберите действие:")
        print("1. Умная рекомендация (на основе анализа)")
        print("2. Случайная рекомендация") 
        print("3. Анализ конкретного тикера")
        print("4. Выход")
        
        choice = input("\nВаш выбор (1-4): ").strip()
        
        if choice == "1":
            print("\n⏳ Анализируем рынок...")
            recommendation = system.get_smart_recommendation()
            print(system.format_recommendation(recommendation))
            
        elif choice == "2":
            recommendation = system.get_random_recommendation()
            print(system.format_recommendation(recommendation))
            
        elif choice == "3":
            print(f"\nДоступные тикеры: {', '.join(TICKER_MAPPING.keys())}")
            ticker = input("Введите тикер для анализа: ").strip().upper()
            if ticker in TICKER_MAPPING:
                print(f"\n⏳ Анализируем {ticker}...")
                recommendation = system.get_smart_recommendation(ticker)
                print(system.format_recommendation(recommendation))
            else:
                print("❌ Неизвестный тикер!")
                
        elif choice == "4":
            print("👋 До свидания!")
            break
            
        else:
            print("❌ Неверный выбор!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Программа завершена пользователем")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        print("Проверьте подключение к интернету и повторите попытку")
