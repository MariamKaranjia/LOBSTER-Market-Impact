# LOBSTER Market Impact Research

## Project Overview

This project investigates the relationship between order flow imbalance and short-term stock price movements using high-frequency limit order book data from LOBSTER.

The research focuses on reconstructing order book information, processing high-frequency trading activity into minute-level observations, and estimating the relationship between signed trading activity and next-minute returns.

**Research Supervisor:** Professor Tucker Balch  
**Institution:** Emory University, Goizueta Business School

## Dataset

- **Source:** LOBSTER high-frequency market data
- **Period:** June 30, 2025 – June 30, 2026
- **Coverage:** 252 trading days per stock
- **Frequency:** One-minute observations
- **Trading session:** 390 minutes per day
- **Processed observations:** 98,280 per stock
- **Stocks analyzed:** 12

### Stock Universe

| Ticker | Company |
|---|---|
| AXP | American Express |
| BA | Boeing |
| CAT | Caterpillar |
| CRM | Salesforce |
| CSCO | Cisco Systems |
| CVX | Chevron |
| GS | Goldman Sachs |
| HD | Home Depot |
| HON | Honeywell |
| IBM | IBM |
| MMM | 3M |
| VZ | Verizon |

## Methodology

### 1. Data Processing

The Python processing pipeline:

- Reads daily LOBSTER message files.
- Reconstructs the visible limit order book.
- Extracts best bid and best ask prices.
- Calculates executed trading volume and signed volume.
- Aggregates trading activity into one-minute intervals.
- Constructs normalized trade-flow imbalance and return variables.

### 2. Market Impact Regression

The primary regression examines the relationship between normalized trade-flow imbalance and next-minute returns:

**Next-Minute Return (bps) = α + β × Normalized Trade-Flow Imbalance + ε**

The coefficient β measures the estimated association between trading imbalance and subsequent short-term price movements.

### 3. Robustness Analysis

Robustness checks include:

- Newey–West heteroskedasticity and autocorrelation-consistent (HAC) standard errors.
- Outlier-trimmed regressions excluding the most extreme 1% of returns.
- Comparison of original and trimmed coefficients across all 12 stocks.

## Research Results

All 12 analyzed stocks exhibit positive estimated market-impact coefficients.

| Ticker | Coefficient (bps) |
|---|---:|
| CSCO | 3.5093 |
| CRM | 2.8613 |
| CVX | 2.4085 |
| BA | 2.3373 |
| IBM | 2.3057 |
| VZ | 2.2019 |
| CAT | 2.0013 |
| GS | 1.8619 |
| HD | 1.6677 |
| HON | 1.6257 |
| AXP | 1.5885 |
| MMM | 1.4590 |

### Key Findings

1. All 12 original regression coefficients are positive and statistically significant at the 5% level.
2. All 12 coefficients remain positive after outlier trimming.
3. Estimated coefficients decrease after trimming, suggesting that extreme returns contribute to measured impact magnitude.
4. The explanatory power of individual regressions is relatively modest, with R-squared values of approximately 1.5%–4.3%.

These results establish a consistent positive relationship between normalized trading imbalance and next-minute returns across the analyzed stocks. They do not, by themselves, establish causality.

## Repository Structure

```text
LOBSTER-Market-Impact/
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   └── 02_batch2_processing.ipynb
├── src/
│   └── lobster_pipeline.py
├── results/
│   ├── 12_stock_research_summary.csv
│   ├── 12_stock_robustness_comparison.png
│   ├── all_12_market_impact_results.csv
│   └── all_12_market_impact_comparison.png
└── README.md
```

Additional regression tables and robustness outputs are available in the `results/` directory.

## Data Availability

Raw LOBSTER data is proprietary and is not included in this public repository. Access to the original data requires appropriate authorization and licensing.

## Future Research

- Extend the analysis to additional Dow Jones constituents.
- Examine nonlinear relationships between order flow and returns.
- Compare market impact across stocks with different liquidity characteristics.
- Evaluate predictive performance and alternative model specifications.
