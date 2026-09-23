
from pathlib import Path
from collections import defaultdict
import re

import numpy as np
import pandas as pd


COLUMNS = [
    "time",
    "event_type",
    "order_id",
    "size",
    "price",
    "direction",
    "extra",
]

REGULAR_OPEN = 9 * 3600 + 30 * 60
REGULAR_CLOSE = 16 * 3600


def process_day(file_path):
    """
    Reconstruct the active order book from one LOBSTER
    message file and calculate regular-session minute metrics.

    Returns a DataFrame with best bid, best ask, and
    volume-weighted average visible/hidden execution price.
    """

    file_path = Path(file_path)

    match = re.search(r"_(\d{4}-\d{2}-\d{2})_", file_path.name)

    if match is None:
        raise ValueError(f"Cannot identify date: {file_path.name}")

    trading_date = pd.Timestamp(match.group(1))
    ticker = file_path.name.split("_")[0].upper()

    df = pd.read_csv(
        file_path,
        header=None,
        names=COLUMNS,
    )

    # Active orders: order_id -> (direction, price, remaining_size)
    orders = {}

    # Aggregate active shares at each price level.
    bid_levels = defaultdict(int)
    ask_levels = defaultdict(int)

    # Execution totals for each minute.
    execution_notional = defaultdict(float)
    execution_volume = defaultdict(int)

    snapshots = []

    def change_level(direction, price, change):
        levels = bid_levels if direction == 1 else ask_levels

        levels[price] += change

        if levels[price] <= 0:
            levels.pop(price, None)

    def remove_order(order_id):
        order = orders.pop(order_id, None)

        if order is not None:
            direction, price, remaining = order
            change_level(direction, price, -remaining)

    def reduce_order(order_id, quantity):
        order = orders.get(order_id)

        if order is None:
            return

        direction, price, remaining = order
        removed = min(quantity, remaining)
        new_remaining = remaining - removed

        change_level(direction, price, -removed)

        if new_remaining > 0:
            orders[order_id] = (
                direction,
                price,
                new_remaining,
            )
        else:
            orders.pop(order_id, None)

    def save_snapshot(minute_index):
        best_bid = max(bid_levels) if bid_levels else np.nan
        best_ask = min(ask_levels) if ask_levels else np.nan

        volume = execution_volume.get(minute_index, 0)

        avg_transaction_price = (
            execution_notional[minute_index] / volume
            if volume > 0
            else np.nan
        )

        snapshots.append(
            {
                "ticker": ticker,
                "datetime": (
                    trading_date
                    + pd.to_timedelta(minute_index, unit="m")
                ),
                "highest_bid": best_bid / 10000
                if pd.notna(best_bid)
                else np.nan,
                "lowest_ask": best_ask / 10000
                if pd.notna(best_ask)
                else np.nan,
                "avg_transaction_price": avg_transaction_price,
                "executed_volume": volume,
            }
        )

    # Process all messages in chronological order, including
    # pre-open events, to build the opening book state.
    current_minute = None

    for row in df.itertuples(index=False):
        time_seconds = float(row.time)
        event_type = int(row.event_type)
        order_id = int(row.order_id)
        quantity = int(row.size)
        price = int(row.price)
        direction = int(row.direction)

        minute_index = int(time_seconds // 60)

        # Save completed regular-session minutes before
        # processing messages belonging to the next minute.
        if current_minute is not None and minute_index > current_minute:
            while current_minute < min(
                minute_index,
                REGULAR_CLOSE // 60,
            ):
                if current_minute >= REGULAR_OPEN // 60:
                    save_snapshot(current_minute)

                current_minute += 1

        current_minute = minute_index

        if event_type == 1:
            # New visible limit order.
            if order_id in orders:
                remove_order(order_id)

            if quantity > 0 and direction in (1, -1):
                orders[order_id] = (
                    direction,
                    price,
                    quantity,
                )
                change_level(direction, price, quantity)

        elif event_type == 2:
            # Partial cancellation.
            reduce_order(order_id, quantity)

        elif event_type == 3:
            # Complete deletion.
            remove_order(order_id)

        elif event_type == 4:
            # Execution of a visible resting order.
            reduce_order(order_id, quantity)

        elif event_type == 5:
            # Hidden execution: no visible order-book change.
            pass

        # Types 6 and 7 do not modify the reconstructed
        # active visible order book in this implementation.

        if (
            event_type in (4, 5)
            and REGULAR_OPEN <= time_seconds < REGULAR_CLOSE
            and quantity > 0
        ):
            execution_volume[minute_index] += quantity

            # LOBSTER prices are stored in units of 1/10000 USD.
            execution_notional[minute_index] += (
                quantity * price / 10000
            )

    # Save the remaining regular-session minutes.
    if current_minute is not None:
        start_minute = max(
            current_minute,
            REGULAR_OPEN // 60,
        )

        for minute_index in range(
            start_minute,
            REGULAR_CLOSE // 60,
        ):
            save_snapshot(minute_index)

    result = pd.DataFrame(snapshots)

    return result


def process_stock(ticker, data_dir="../data", output_dir="../results"):
    """
    Process all daily message files for one stock and save
    its minute-level output separately.
    """

    ticker = ticker.upper()

    data_dir = Path(data_dir)
    output_dir = Path(output_dir)

    stock_folders = sorted(
        folder
        for folder in data_dir.iterdir()
        if folder.is_dir()
        and folder.name.upper().startswith(ticker + "_")
    )

    if not stock_folders:
        raise FileNotFoundError(
            f"No data folder found for {ticker} in {data_dir}"
        )

    files = sorted(
        file
        for folder in stock_folders
        for file in folder.rglob(f"{ticker}_*_message_0.csv")
    )

    if not files:
        raise FileNotFoundError(
            f"No message files found for {ticker}"
        )

    print(f"{ticker}: Found {len(files)} daily files")

    daily_results = []
    failures = []

    for index, file in enumerate(files, start=1):
        try:
            daily_results.append(process_day(file))

        except Exception as exc:
            failures.append((file.name, str(exc)))
            print(f"FAILED: {file.name} — {exc}")

        if index % 25 == 0 or index == len(files):
            print(f"{ticker}: Processed {index}/{len(files)} files")

    if not daily_results:
        raise RuntimeError(f"No files processed successfully for {ticker}")

    result = pd.concat(daily_results, ignore_index=True)
    result = result.sort_values("datetime").reset_index(drop=True)

    stock_output = output_dir / ticker
    stock_output.mkdir(parents=True, exist_ok=True)

    output_file = stock_output / f"{ticker}_minute_data.csv"

    result.to_csv(output_file, index=False)

    print(f"\nSaved: {output_file}")
    print(f"Successful files: {len(daily_results)}")
    print(f"Failed files: {len(failures)}")
    print(f"Minute observations: {len(result):,}")

    return result, failures