import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_ai_summary(result: dict) -> str:
    prompt = f"""
You are a quantitative trading analyst.

Analyze the following backtest results and explain them in simple English.

Rules:
- Do NOT give financial advice
- Do NOT say buy/sell/invest
- Focus on performance, risk, and improvements
- Keep it concise and easy to understand

Backtest Results:
- Total Trades: {result.get("total_trades")}
- Win Rate: {result.get("win_rate")}
- Total PnL: {result.get("total_net_pnl")}
- Profit Factor: {result.get("profit_factor")}
- Max Drawdown: {result.get("max_drawdown")}
- Avg Win: {result.get("avg_win")}
- Avg Loss: {result.get("avg_loss")}

Return in exactly these sections:
1. Performance Overview
2. Risk & Weaknesses
3. Suggestions
"""

    response = client.responses.create(
        model="gpt-4.1-mini",   # stable + cheaper
        input=prompt
    )

    return response.output_text