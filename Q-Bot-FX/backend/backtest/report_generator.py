from __future__ import annotations


def generate_backtest_report(metrics, symbol: str = "", timeframe: str = ""):
    print("====================================")
    print("Q-BOT BACKTEST REPORT")
    print("====================================")
    print(f"Symbol: {symbol}")
    print(f"Timeframe: {timeframe}")
    print(f"Total Trades: {metrics['total_trades']}")
    print(f"Winrate: {metrics['winrate'] * 100:.2f}%")
    print(f"Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"Expectancy: {metrics['expectancy']:.4f}")
    print(f"Net Profit: {metrics['net_profit']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}")
    print(f"Average RR: {metrics['average_rr']:.2f}")
    print(f"Win Streak: {metrics['longest_win_streak']}")
    print(f"Loss Streak: {metrics['longest_loss_streak']}")
    print("====================================")
