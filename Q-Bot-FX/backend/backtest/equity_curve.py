from __future__ import annotations

import matplotlib.pyplot as plt


def generate_equity_curve(equity_history, output_path):
    plt.figure(figsize=(12, 5))
    plt.plot(equity_history, label="Equity")
    plt.title("Q-Bot Backtest Equity Curve")
    plt.xlabel("Trade #")
    plt.ylabel("Equity PnL")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
