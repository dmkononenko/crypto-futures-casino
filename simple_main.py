#!/usr/bin/env python3
"""
Упрощенная версия Trading Randomizer для работы с demo API ключом
"""

import random
from datetime import datetime
from typing import Dict, List
from api_client import coingecko_client
from config import TICKER_MAPPING, LEVERAGES, DIRECTIONS

class SimpleTradingRecommendationSystem:
    def __init__(self):
        self.results_file = "results.md"
        
    def get_market_based_recommendation(self) -> Dict:
        """Получить рекомендацию на основе текущих рыночных данных"""
        print("🔄 Получение рыночных данных...")
        
        # Получаем текущие цены всех тикеров
        all_coin_ids = list(TICKER_MAPPING.values())
        market_data = coingecko_client.get_current_prices(all_coin_ids)
        
        if not market_data:
            return self._get_fallback_recommendation()
        
        # Анализируем данные и собираем все возможности
        opportunities = []
        
        for symbol, coin_id in TICKER_MAPPING.items():
            if coin_id not in market_data:
                continue
                
            data = market_data[coin_id]
            
            # Рассчитываем скор для каждого актива
            score = self._calculate_simple_score(data)
            
            opportunities.append({
                'ticker': symbol,
                'coin_id': coin_id,
                'data': data,
                'score': score
            })
        
        if not opportunities:
            return self._get_fallback_recommendation()
        
        # Сортируем по скору и выбираем случайный из топ-5
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        top_opportunities = opportunities[:5]  # Топ-5 возможностей
        
        # Выбираем случайную из лучших
        selected_opportunity = random.choice(top_opportunities)
        
        print(f"📊 Проанализировано {len(opportunities)} активов, выбран {selected_opportunity['ticker']} (скор: {selected_opportunity['score']:.1f})")
        
        return self._create_recommendation(selected_opportunity)
    
    def _calculate_simple_score(self, coin_data: Dict) -> float:
        """Простой скоринг на основе доступных данных"""
        base_score = random.uniform(45, 55)  # Случайный базовый скор для разнообразия
        
        # Анализ 24-часового изменения
        price_change_24h = coin_data.get('usd_24h_change', 0)
        
        # Более гибкая система скоринга
        if abs(price_change_24h) > 8:
            base_score += 20  # Высокая волатильность = возможности
        elif abs(price_change_24h) > 4:
            base_score += 15  # Средняя волатильность
        elif abs(price_change_24h) > 2:
            base_score += 10  # Низкая волатильность
        else:
            base_score += 5   # Очень стабильная цена
        
        # Анализ объема (если доступен)
        volume_24h = coin_data.get('usd_24h_vol', 0)
        if volume_24h > 1000000000:  # > 1B
            base_score += 10  # Высокий объем = больше ликвидности
        elif volume_24h > 100000000:  # > 100M
            base_score += 5
        
        # Рыночная капитализация (стабильность)
        market_cap = coin_data.get('usd_market_cap', 0)
        if market_cap > 50000000000:  # > 50B - топ активы
            base_score += 8
        elif market_cap > 10000000000:  # > 10B
            base_score += 5  # Более стабильный актив
        
        # Добавляем случайность для разнообразия рекомендаций
        base_score += random.uniform(-10, 15)
        
        return max(base_score, 20)  # Минимальный скор 20
    
    def _create_recommendation(self, opportunity: Dict) -> Dict:
        """Создать рекомендацию на основе найденной возможности"""
        data = opportunity['data']
        ticker = opportunity['ticker']
        
        price_change_24h = data.get('usd_24h_change', 0)
        current_price = data.get('usd', 0)
        
        # Определяем направление
        if price_change_24h < -5:
            direction = 'LONG'
            reasoning = f"падение на {abs(price_change_24h):.1f}% за 24ч - потенциал отскока"
        elif price_change_24h > 8:
            direction = 'SHORT'  
            reasoning = f"рост на {price_change_24h:.1f}% за 24ч - возможна коррекция"
        else:
            direction = random.choice(['LONG', 'SHORT'])
            reasoning = f"стабильные изменения ({price_change_24h:+.1f}%), технический анализ"
        
        # Новая логика подбора плеча по уверенности
        confidence = min(opportunity['score'], 100)  # Максимум 100% уверенности
        
        if confidence >= 100:
            target_leverage = random.randint(75, 100)
        elif confidence >= 90:
            target_leverage = 50
        elif confidence >= 80:
            target_leverage = 25
        else:
            # Линейная интерполяция от x2 до x25 для уверенности < 80%
            target_leverage = 2 + (confidence / 80) * (25 - 2)

        # Находим ближайшее доступное плечо
        leverage = min(LEVERAGES, key=lambda x: abs(x - target_leverage))

        return {
            'ticker': ticker,
            'direction': direction,
            'leverage': f"x{leverage}",
            'confidence': confidence,
            'reasoning': reasoning,
            'current_price': current_price,
            'price_change_24h': price_change_24h,
            'volume_24h': data.get('usd_24h_vol', 0),
            'market_cap': data.get('usd_market_cap', 0)
        }
    
    def _get_fallback_recommendation(self) -> Dict:
        """Резервная рекомендация"""
        ticker = random.choice(list(TICKER_MAPPING.keys()))
        leverage = random.choice(LEVERAGES)
        direction = random.choice(DIRECTIONS)
        
        return {
            'ticker': ticker,
            'direction': direction,
            'leverage': f"x{leverage}",
            'confidence': 40,
            'reasoning': 'Консервативная рекомендация (ограниченные данные API)',
            'current_price': 0,
            'price_change_24h': 0,
            'volume_24h': 0,
            'market_cap': 0
        }
    
    def format_recommendation(self, rec: Dict) -> str:
        """Форматировать рекомендацию для вывода"""
        confidence_emoji = "🔥" if rec['confidence'] > 70 else "⚡" if rec['confidence'] > 50 else "🎯"
        
        output = f"""
## {confidence_emoji} **Рекомендация на {datetime.now().strftime('%d.%m.%Y')}:**

### **{rec['ticker']} + {rec['leverage']} + {rec['direction']}**

**Уверенность:** {rec['confidence']:.1f}%
**Текущая цена:** ${rec['current_price']:.4f}
**Изменение 24ч:** {rec['price_change_24h']:+.1f}%

**Обоснование:** {rec['reasoning']}

**Рыночные данные:**
"""
        
        if rec['volume_24h'] > 0:
            output += f"- Объем 24ч: ${rec['volume_24h']:,.0f}\n"
        if rec['market_cap'] > 0:
            output += f"- Рыночная кап: ${rec['market_cap']:,.0f}\n"
        
        # Рекомендации по торговле
        leverage_num = int(rec['leverage'][1:])
        if rec['confidence'] > 70:
            output += "\n**Торговые рекомендации:**\n"
            output += "- Размер позиции: 3-4% от депозита\n"
        elif rec['confidence'] > 50:
            output += "\n**Торговые рекомендации:**\n" 
            output += "- Размер позиции: 2-3% от депозита\n"
        else:
            output += "\n**Торговые рекомендации:**\n"
            output += "- Размер позиции: 1-2% от депозита\n"
        
        if leverage_num >= 20:
            output += "- Стоп-лосс: 2-3%\n- Тейк-профит: 5-10%\n"
        elif leverage_num >= 10:
            output += "- Стоп-лосс: 4-6%\n- Тейк-профит: 10-15%\n"
        else:
            output += "- Стоп-лосс: 5-8%\n- Тейк-профит: 15-25%\n"
        
        return output

def main():
    """Основная функция"""
    system = SimpleTradingRecommendationSystem()
    
    print("🚀 Trading Randomizer - Market Based Recommendations")
    print("=" * 55)
    
    while True:
        print("\n📊 Выберите действие:")
        print("1. Рекомендация на основе рынка")
        print("2. Случайная рекомендация")
        print("3. Выход")
        
        choice = input("\nВаш выбор (1-3): ").strip()
        
        if choice == "1":
            print("\n⏳ Анализируем рыночные данные...")
            recommendation = system.get_market_based_recommendation()
            print(system.format_recommendation(recommendation))
            
        elif choice == "2":
            fallback = system._get_fallback_recommendation()
            print(system.format_recommendation(fallback))
            
        elif choice == "3":
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
