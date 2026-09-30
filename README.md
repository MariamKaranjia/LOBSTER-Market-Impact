
## Author

**Mariam Karanjia**  
Master of Finance, Emory University – Goizueta Business School
# LOBSTER Market Impact Analysis

Market microstructure and market impact analysis using LOBSTER limit order book data.

This repository contains a reusable Python pipeline for reconstructing the limit order book, processing high-frequency LOBSTER message data, measuring trade-flow imbalance, and analyzing short-horizon market impact across multiple securities.

## Current Analysis

The current implementation processes eight securities:

- American Express (AXP)
- Boeing (BA)
- Caterpillar (CAT)
- Cisco Systems (CSCO)
- Chevron (CVX)
- Goldman Sachs (GS)
- 3M (MMM)
- Verizon (VZ)

### Sample

- **Sample period:** June 30, 2025 – June 30, 2026
- **Trading days:** 252 per security
- **Frequency:** Minute-level
- **Regular trading session:** 9:30 AM – 4:00 PM
- **Minute observations:** 98,280 per security

The pipeline processes each security independently and produces a standardized minute-level dataset for subsequent market-impact analysis.

## Methodology

### 1. LOBSTER Message Processing

Raw LOBSTER message files are loaded and processed chronologically.

The pipeline handles the primary LOBSTER event types required for reconstructing the visible limit order book, including:

- New limit orders
- Partial cancellations
- Order deletions
- Visible executions
- Hidden executions

Active orders are tracked by order ID throughout each trading day.

### 2. Order Book Reconstruction

The active limit order book is reconstructed from the LOBSTER message stream.

For each minute, the pipeline records:

- **Best bid:** highest active bid price
- **Best ask:** lowest active ask price
- **Average transaction price**
- **Executed volume**

This produces a consistent minute-level representation of market conditions.

### 3. Trade Direction

LOBSTER's `direction` field identifies the side of the resting limit order.

For execution events, the aggressor direction is therefore the opposite side of the resting order.

The pipeline uses:

`aggressor_sign = -direction`

Signed execution volume is then calculated as:

`signed_volume = aggressor_sign × executed_quantity`

Positive signed volume represents buyer-initiated trading, while negative signed volume represents seller-initiated trading.

### 4. Trade-Flow Imbalance

Minute-level normalized trade-flow imbalance is calculated as:

`trade_flow_imbalance = signed_volume / executed_volume`

The measure is bounded between **-1 and +1**:

- Values near **+1** indicate predominantly buyer-initiated execution volume.
- Values near **-1** indicate predominantly seller-initiated execution volume.
- Values near **0** indicate relatively balanced executed flow.

This is an **execution-based trade-flow imbalance measure**, rather than a full depth-based order-book imbalance measure.

### 5. Market Impact

Minute-level transaction prices are used to calculate price changes.

The analysis examines whether trade-flow imbalance in one minute is associated with the subsequent minute's price movement.

This provides a framework for estimating short-horizon market impact across securities.

## Data Validation

The final processed datasets were checked for consistency across all eight securities.

Each security contains:

- **98,280 minute observations**
- Complete signed-volume calculations
- Trade-flow imbalance bounded between **-1 and +1**
- 252 successfully processed trading days

The corrected mean trade-flow imbalance is negative across all eight securities in the current sample, indicating that seller-initiated executed volume exceeds buyer-initiated executed volume on average under this execution-based measure.

## Repository Structure

### `src/`

Contains the reusable processing pipeline.

`lobster_pipeline.py` reconstructs the active order book and converts daily LOBSTER message files into standardized minute-level datasets.

### `notebooks/`

Contains exploratory analysis, validation, market-impact analysis, and visualization code.

### `results/`

Contains generated figures and processed analysis outputs organized by security.

### `data/`

Contains the local raw LOBSTER files used by the pipeline.

Raw LOBSTER data are excluded from GitHub because the underlying dataset is licensed.

## Data

The analysis uses **LOBSTER (Limit Order Book System – The Efficient Reconstructor)** message data.

The raw LOBSTER files are not distributed with this repository.

The processing pipeline is designed to operate on locally stored LOBSTER message files while keeping the licensed source data outside version control.

## Current Progress

The project began with a single-day implementation for Coca-Cola (KO) to validate the order-book reconstruction and market-impact methodology.

The workflow was subsequently converted into a reusable Python pipeline and extended to a one-year sample of eight securities.

The current pipeline:

1. Reads daily LOBSTER message files.
2. Reconstructs the active visible limit order book.
3. Extracts minute-level best bid and best ask.
4. Aggregates execution volume and transaction prices.
5. Determines aggressor-side signed volume.
6. Calculates normalized trade-flow imbalance.
7. Produces standardized security-level datasets.
8. Supports next-minute market-impact analysis.

The resulting framework can be extended to additional securities and used for cross-sectional analysis of liquidity, order flow, and market impact.
