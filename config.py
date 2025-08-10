# Конфигурация для Trading Randomizer

# Тикеры из tickers.md
TICKERS = [
    'bitcoin', 'ethereum', 'ripple', 'binancecoin', 'solana',
    'usd-coin', 'staked-ether', 'tron', 'dogecoin', 'cardano',
    'hyperliquid', 'sui', 'stellar'
]

# Соответствие символов и ID для CoinGecko (проверенные ID)
TICKER_MAPPING = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum', 
    'XRP': 'ripple',
    'BNB': 'binancecoin',
    'SOL': 'solana',
    'USDC': 'usd-coin',
    'stETH': 'staked-ether',
    'TRX': 'tron',
    'DOGE': 'dogecoin',
    'ADA': 'cardano',
    'SUI': 'sui',
    'XLM': 'stellar'
}

# Доступные плечи из credits.md
LEVERAGES = [1, 2, 3, 5, 10, 20, 25, 50, 75, 100]

# Направления из ways.md
DIRECTIONS = ['LONG', 'SHORT']

# CoinGecko API настройки
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_API_KEY = "CG-EW8gYdr1dX36EnfhxZeCqTHf"
REQUEST_TIMEOUT = 10
