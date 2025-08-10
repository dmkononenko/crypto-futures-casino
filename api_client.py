import requests
import time
from typing import Dict, List, Optional
from config import COINGECKO_BASE_URL, COINGECKO_API_KEY, REQUEST_TIMEOUT, TICKERS

class CoinGeckoClient:
    def __init__(self):
        self.base_url = COINGECKO_BASE_URL
        self.api_key = COINGECKO_API_KEY
        self.session = requests.Session()
        self.last_request_time = 0
        
        # Добавляем API ключ в заголовки
        if self.api_key:
            self.session.headers.update({
                'x-cg-demo-api-key': self.api_key,
                'accept': 'application/json'
            })
        
    def _rate_limit(self):
        """Ограничение скорости запросов (с API ключом - до 500 запросов в минуту)"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # С API ключом можем делать запросы чаще
        min_interval = 0.2 if self.api_key else 1.5
        
        if time_since_last < min_interval:
            time.sleep(min_interval - time_since_last)
        self.last_request_time = time.time()
    
    def get_current_prices(self, coin_ids: List[str]) -> Dict:
        """Получить текущие цены монет"""
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/simple/price"
            params = {
                'ids': ','.join(coin_ids),
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true',
                'include_market_cap': 'true'
            }
            
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении цен: {e}")
            return {}
    
    def get_historical_data(self, coin_id: str, days: int = 7) -> Dict:
        """Получить исторические данные за указанное количество дней"""
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/coins/{coin_id}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'hourly' if days <= 30 else 'daily'
            }
            
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении исторических данных для {coin_id}: {e}")
            return {}
    
    def get_market_data(self, coin_ids: List[str]) -> Dict:
        """Получить подробные рыночные данные"""
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/coins/markets"
            params = {
                'vs_currency': 'usd',
                'ids': ','.join(coin_ids),
                'order': 'market_cap_desc',
                'per_page': len(coin_ids),
                'page': 1,
                'sparkline': 'false',
                'price_change_percentage': '1h,24h,7d'
            }
            
            response = self.session.get(url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении рыночных данных: {e}")
            return []

# Глобальный экземпляр клиента
coingecko_client = CoinGeckoClient()
