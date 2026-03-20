import pandas as pd
import os

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../dataset")


def load_csv(file_path):
    return pd.read_csv(file_path)


def scan_columns(df):
    print("\nColumns found in your file:")
    print("-" * 40)
    for i, col in enumerate(df.columns, 1):
        sample = str(df[col].iloc[0])[:40] if len(df) > 0 else "N/A"
        print(f"  [{i}] {col}")
        print(f"       Sample: {sample}")
    print("-" * 40)
    print(f"Total: {len(df.columns)} columns, {len(df)} rows\n")


def select_columns(df):
    print("Which columns do you want to keep?")
    print("Enter column numbers separated by commas (e.g. 1, 3, 5)")
    print("Or enter column names separated by commas (e.g. name, price)\n")

    user_input = input("Your selection: ").strip()
    parts = [p.strip() for p in user_input.split(",")]

    try:
        indices = [int(p) - 1 for p in parts]
        selected = [df.columns[i] for i in indices]
    except ValueError:
        selected = parts

    invalid = [c for c in selected if c not in df.columns]
    if invalid:
        print(f"\nColumn(s) not found: {invalid}")
        return select_columns(df)

    return selected


def get_optional_metadata():
    print("\n" + "-" * 40)
    print("Optional Info (press Enter to skip)")
    print("-" * 40)

    industry   = input("Industry (e.g. Fashion, Tech, Food): ").strip()
    brand_name = input("Brand name (e.g. Nike, Apple): ").strip()

    return industry or None, brand_name or None


def convert_inr_to_usd(value, exchange_rate=0.012):
    """Converts INR string like ₹1,099 to USD float."""
    try:
        cleaned = str(value).replace("₹", "").replace(",", "").strip()
        return round(float(cleaned) * exchange_rate, 2)
    except:
        return value


def handle_currency_conversion(df):   
    print("\n" + "-" * 40)
    print("Currency Conversion (press Enter to skip)")
    print("-" * 40)

    col_input = input("Which column contains INR prices (₹)? Enter name or number, or press Enter to skip: ").strip()

    if not col_input:
        return df

    try:
        col_name = df.columns[int(col_input) - 1]
    except (ValueError, IndexError):
        col_name = col_input

    if col_name not in df.columns:
        print(f"Column '{col_name}' not found, skipping.")
        return df

    rate_input = input("Exchange rate (default 1 INR = 0.012 USD, press Enter to confirm): ").strip()
    exchange_rate = float(rate_input) if rate_input else 0.012

    df[col_name] = df[col_name].apply(lambda x: convert_inr_to_usd(x, exchange_rate))
    df.rename(columns={col_name: col_name + "_usd"}, inplace=True)
    print(f"Converted '{col_name}' → '{col_name}_usd' at rate {exchange_rate}")
    return df


def import_and_organize():
    """Reads all CSVs in the dataset folder and merges them into all_industries_organized.csv."""
    all_dfs = []

    for filename in os.listdir(DATASET_DIR):
        if(not filename.endswith(".csv") or filename == "all_industries_organized.csv" or filename == "competitors_combined.csv"):
            continue

        path = os.path.join(DATASET_DIR, filename)
        try:
            df = pd.read_csv(path)
            source_name = filename.replace(".csv", "")
            df["source"] = source_name

            # normalise column names to lowercase + strip spaces
            df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

            all_dfs.append(df)
            print(f"  Loaded: {filename} ({len(df)} rows)")
        except Exception as e:
            print(f"  Skipped {filename}: {e}")

    if(not all_dfs):
        print("  No CSV files found to organize.")
        return

    combined = pd.concat(all_dfs, ignore_index=True)
    out_path = os.path.join(DATASET_DIR, "all_industries_organized.csv")
    combined.to_csv(out_path, index=False)
    print(f"\n  Organized dataset saved → {out_path}")
    print(f"  Total rows: {len(combined)}")


def main():
    print("=" * 40)
    print("    CSV Column Selector & Row Trimmer")
    print("=" * 40)

    file_path = input("\nEnter the path to your CSV file: ").strip().strip('"').strip("'")
    df = load_csv(file_path)
    print("\nFile loaded successfully!")

    scan_columns(df)
    selected_cols = select_columns(df)
    print(f"\nSelected: {selected_cols}")

    row_input = input(f"\nHow many rows do you want to keep? (file has {len(df)} rows): ").strip()
    row_limit = int(row_input)

    industry, brand_name = get_optional_metadata()

    result = df[selected_cols].head(row_limit).copy()
    result = handle_currency_conversion(result)   # FIX: removed extra arg

    if brand_name:
        result.insert(0, "brand_name", brand_name)
    if industry:
        result.insert(0, "industry", industry)

    output_path = input("\nEnter output file name (e.g. output.csv): ").strip()
    if not output_path.endswith(".csv"):
        output_path += ".csv"

    result.to_csv(output_path, index=False)
    print(f"\nDone! Saved to: {output_path}")
    print(f"Rows: {result.shape[0]} | Columns: {result.shape[1]}")
    print("=" * 40)


if __name__ == "__main__":
    main()