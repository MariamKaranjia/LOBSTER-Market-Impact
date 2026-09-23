# LOBSTER Market Impact Analysis

Market microstructure and market impact analysis using LOBSTER limit order book data.

This repository contains the preprocessing, order book reconstruction, and exploratory analysis developed for the LOBSTER Market Impact project.

## Current Analysis

The current implementation uses **The Coca-Cola Company (KO)** as the initial security.

- **Sample period:** June 30, 2025 – June 30, 2026
- **Trading days processed:** 252
- **Frequency:** Minute-level
- **Minute observations:** 95,694

The analysis currently includes:

- Reconstruction of the active limit order book from LOBSTER message data
- Best bid (highest active bid) and best ask (lowest active ask)
- Average transaction price
- Execution and trading-volume analysis
- Normalized trade-flow imbalance
- New order flow analysis
- Minute-level market impact analysis
- Price and order-flow visualizations

## Repository Structure

`notebooks/`  
Contains the preprocessing, order book reconstruction, analysis, and visualization code.

`results/`  
Contains generated figures and analysis outputs.

## Data

The analysis uses **LOBSTER (Limit Order Book System – The Efficient Reconstructor)** data.

Raw LOBSTER data are **not included in this repository** because the underlying dataset is licensed.

## Current Progress

The processing pipeline was first tested on a single KO trading day and subsequently extended to the full sample of 252 trading days.

The KO implementation serves as the initial pipeline for extending the analysis to additional securities.

## Author

**Mariam Karanjia**  
Master of Finance, Emory University – Goizueta Business School
