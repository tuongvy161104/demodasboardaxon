# Axon Ads Dashboard

Dashboard phân tích hiệu suất campaign Axon AppLovin, xây dựng bằng Streamlit + Plotly.

## Features

- 📊 KPI Cards: Total Campaigns, Cost, Revenue, Profit, Orders
- 🟢🔴 ROAS Performance: campaigns above/below breakeven ROAS
- 📅 Time-series chart: sOrders & sROAS theo time period
- 🏆 Top/Bottom campaigns by sOrders và sProfit
- 📋 Raw data table có filter

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run dashboard.py
```

## Deploy

Deployed on [Streamlit Community Cloud](https://streamlit.io/cloud).
