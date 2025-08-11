#!/usr/bin/env python3
from simple_main import SimpleTradingRecommendationSystem

if __name__ == "__main__":
    system = SimpleTradingRecommendationSystem()
    rec = system.get_market_based_recommendation()
    print(system.format_recommendation(rec))
