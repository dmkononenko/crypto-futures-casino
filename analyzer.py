import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from api_client import coingecko_client
from config import TICKER_MAPPING, LEVERAGES, DIRECTIONS

class TechnicalAnalyzer:
    def __init__(self):
        self.min_data_points = 20  # Минимум точек для анализа
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Расчет RSI (Relative Strength Index)"""
        if len(prices) < period + 1:
            return 50  # Нейтральное значение
        
        df = pd.DataFrame({'price': prices})
        delta = df['price'].diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50
    
    def calculate_volatility(self, prices: List[float]) -> float:
        """Расчет волатильности (стандартное отклонение)"""
        if len(prices) < 2:
            return 0
        
        returns = np.diff(np.log(prices))
        return float(np.std(returns) * 100)  # В процентах
    
    def analyze_price_trend(self, prices: List[float], volumes: List[float] = None) -> Dict:
        """Анализ тренда цены"""
        if len(prices) < self.min_data_points:
            return {
                'trend': 'SIDEWAYS',
                'strength': 0,
                'confidence': 0
            }
        
        # Простой анализ тренда по скользящим средним
        short_ma = np.mean(prices[-5:])  # Короткая MA (5 периодов)
        long_ma = np.mean(prices[-20:])   # Длинная MA (20 периодов)
        
        trend_strength = (short_ma - long_ma) / long_ma * 100
        
        if trend_strength > 2:
            trend = 'UP'
        elif trend_strength < -2:
            trend = 'DOWN'
        else:
            trend = 'SIDEWAYS'
        
        confidence = min(abs(trend_strength) * 10, 100)  # Уверенность 0-100%
        
        return {
            'trend': trend,
            'strength': abs(trend_strength),
            'confidence': confidence
        }
    
    def get_recommendation_score(self, coin_data: Dict) -> Dict:
        """Получить рекомендацию на основе анализа данных"""
        if not coin_data or 'prices' not in coin_data:
            return self._neutral_recommendation()
        
        prices = [point[1] for point in coin_data['prices']]
        volumes = [point[1] for point in coin_data.get('total_volumes', [])]
        
        if len(prices) < self.min_data_points:
            return self._neutral_recommendation()
        
        # Технические индикаторы
        rsi = self.calculate_rsi(prices)
        volatility = self.calculate_volatility(prices)
        trend_analysis = self.analyze_price_trend(prices, volumes)
        
        # 24h изменение цены
        price_change_24h = ((prices[-1] - prices[-24]) / prices[-24] * 100) if len(prices) >= 24 else 0
        
        # Логика рекомендаций
        long_score = 0
        short_score = 0
        
        # RSI анализ
        if rsi < 30:  # Перепроданность
            long_score += 30
        elif rsi > 70:  # Перекупленность
            short_score += 30
        elif 40 < rsi < 60:  # Нейтральная зона
            long_score += 10
            short_score += 10
        
        # Трендовый анализ
        if trend_analysis['trend'] == 'UP':
            long_score += trend_analysis['confidence'] * 0.5
        elif trend_analysis['trend'] == 'DOWN':
            short_score += trend_analysis['confidence'] * 0.5
        
        # Волатильность (высокая волатильность = больше возможностей)
        volatility_bonus = min(volatility * 2, 20)
        long_score += volatility_bonus
        short_score += volatility_bonus
        
        # 24h momentum
        if price_change_24h > 5:
            short_score += 15  # Возможна коррекция
        elif price_change_24h < -5:
            long_score += 15   # Возможен отскок
        
        # Определяем направление и плечо
        if long_score > short_score:
            direction = 'LONG'
            confidence = min(long_score, 100)
        else:
            direction = 'SHORT' 
            confidence = min(short_score, 100)
        
        # Подбор плеча на основе волатильности и уверенности
        leverage = self._calculate_optimal_leverage(volatility, confidence)
        
        return {
            'direction': direction,
            'leverage': leverage,
            'confidence': confidence,
            'rsi': rsi,
            'volatility': volatility,
            'trend': trend_analysis['trend'],
            'price_change_24h': price_change_24h,
            'reasoning': self._generate_reasoning(rsi, volatility, trend_analysis, price_change_24h, direction)
        }
    
    def _calculate_optimal_leverage(self, volatility: float, confidence: float) -> int:
        """Расчет оптимального плеча"""
        # Базовое плечо на основе уверенности
        if confidence > 80:
            base_leverage = 20
        elif confidence > 60:
            base_leverage = 10
        elif confidence > 40:
            base_leverage = 5
        else:
            base_leverage = 3
        
        # Корректировка на волатильность
        if volatility > 8:  # Высокая волатильность - меньше плечо
            base_leverage = max(base_leverage // 2, 2)
        elif volatility < 3:  # Низкая волатильность - можно больше
            base_leverage = min(base_leverage * 1.5, 50)
        
        # Находим ближайшее доступное плечо
        return min(LEVERAGES, key=lambda x: abs(x - base_leverage))
    
    def _generate_reasoning(self, rsi: float, volatility: float, trend_analysis: Dict, 
                          price_change_24h: float, direction: str) -> str:
        """Генерация обоснования рекомендации"""
        reasons = []
        
        # RSI обоснование
        if rsi < 30:
            reasons.append(f"RSI ({rsi:.1f}) показывает перепроданность")
        elif rsi > 70:
            reasons.append(f"RSI ({rsi:.1f}) показывает перекупленность")
        else:
            reasons.append(f"RSI ({rsi:.1f}) в нейтральной зоне")
        
        # Тренд
        if trend_analysis['trend'] == 'UP':
            reasons.append("восходящий тренд")
        elif trend_analysis['trend'] == 'DOWN':
            reasons.append("нисходящий тренд")
        else:
            reasons.append("боковое движение")
        
        # 24h изменение
        if abs(price_change_24h) > 5:
            reasons.append(f"значительное изменение за 24ч ({price_change_24h:+.1f}%)")
        
        # Волатильность
        if volatility > 8:
            reasons.append(f"высокая волатильность ({volatility:.1f}%)")
        elif volatility < 3:
            reasons.append(f"низкая волатильность ({volatility:.1f}%)")
        
        return f"{', '.join(reasons)}"
    
    def _neutral_recommendation(self) -> Dict:
        """Нейтральная рекомендация при недостатке данных"""
        return {
            'direction': 'LONG',
            'leverage': 3,
            'confidence': 20,
            'rsi': 50,
            'volatility': 0,
            'trend': 'UNKNOWN',
            'price_change_24h': 0,
            'reasoning': 'Недостаточно данных для анализа, консервативная рекомендация'
        }

# Глобальный экземпляр анализатора
technical_analyzer = TechnicalAnalyzer()
