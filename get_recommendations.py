#!/usr/bin/env python3

from simple_main import SimpleTradingRecommendationSystem

def get_multiple_recommendations(count=5):
    system = SimpleTradingRecommendationSystem()
    recommendations = []
    
    print(f'Получаю {count} рекомендаций...')
    for i in range(count):
        rec = system.get_market_based_recommendation()
        recommendations.append(rec)
        print(f'Рекомендация {i+1}: {rec["ticker"]} {rec["direction"]} x{rec["leverage"]} (уверенность: {rec["confidence"]:.1f}%)')
    
    print('\n=== ВСЕ РЕКОМЕНДАЦИИ ===')
    for i, rec in enumerate(recommendations, 1):
        print(f'\n{i}. {rec["ticker"]} + {rec["direction"]} + x{rec["leverage"]}')
        print(f'   Уверенность: {rec["confidence"]:.1f}%')
        print(f'   Цена: ${rec["current_price"]:.4f}')
        print(f'   Изменение 24ч: {rec["price_change_24h"]:+.1f}%')
        print(f'   Обоснование: {rec["reasoning"]}')
    
    return recommendations

if __name__ == "__main__":
    recommendations = get_multiple_recommendations(5)
