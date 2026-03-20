import pandas as pd
import organize_data
from io import StringIO
class CompetitorMapper:

    STANDARD_COLUMNS = ["competitor_name", "industry", "product_name", "brand_name", "price_usd", "rating", "reviews", "category"]
 
    def __init__(self):
        self.df = None
        self.competitor_name = None
 
    def add_competitor(self):
        print("\n" + "=" * 40)
        print("       Add New Competitor")
        print("=" * 40)
 
        self.competitor_name = input("\nCompetitor name: ").strip()
 
        print("\nHow would you like to add the data?")
        print("  [1] Upload a CSV file")
        print("  [2] Manual input")
        choice = input("\nEnter 1 or 2: ").strip()
 
        if choice == "1":
            self._load_from_csv()
        elif choice == "2":
            self._load_from_manual()
        else:
            print("Invalid choice.")
            return None
 
        self._apply_optional_metadata()
        self.df = organize_data.handle_currency_conversion(self.df)
        self.df = self._map_columns()
        self.df["competitor_name"] = self.competitor_name
 
        print(f"\nCompetitor '{self.competitor_name}' added with {len(self.df)} rows.")
        return self.df
 
    def _load_from_csv(self):
        file_path = input("\nEnter the path to your CSV file: ").strip().strip('"').strip("'")
        df = organize_data.load_csv(file_path)
        print("\nFile loaded successfully!")
 
        organize_data.scan_columns(df)
        selected_cols = organize_data.select_columns(df)
 
        row_input = input(f"\nHow many rows to keep? (file has {len(df)} rows): ").strip()
        row_limit = int(row_input)
 
        self.df = df[selected_cols].head(row_limit).copy()
 
    def _load_from_manual(self):
        print("\nEnter your data as CSV (paste headers first, then rows).")
        print("Type 'DONE' on a new line when finished.\n")
 
        lines = []
        while True:
            line = input()
            if line.strip().upper() == "DONE":
                break
            lines.append(line)
 
        raw = "\n".join(lines)
        self.df = pd.read_csv(StringIO(raw))
        print(f"\nData loaded: {len(self.df)} rows, {len(self.df.columns)} columns.")
 
    def _apply_optional_metadata(self):
        print("\n" + "-" * 40)
        print("Optional Info (press Enter to skip)")
        print("-" * 40)
 
        industry = input("Industry (e.g. Fashion, Tech): ").strip()
        brand_name = input("Brand name: ").strip()
 
        if industry:
            self.df["industry"] = industry
        if brand_name:
            self.df["brand_name"] = brand_name
 
    def _map_columns(self):
        print("\n" + "-" * 40)
        print("Column Mapping")
        print("Map your columns to standard names (press Enter to skip any)")
        print(f"Standard columns: {self.STANDARD_COLUMNS}")
        print("-" * 40)
 
        mapping = {}
        for std_col in self.STANDARD_COLUMNS:
            if std_col in self.df.columns:
                continue
            user_input = input(f"Which column maps to '{std_col}'? (current cols: {list(self.df.columns)}): ").strip()
            if user_input and user_input in self.df.columns:
                mapping[user_input] = std_col
 
        if mapping:
            self.df.rename(columns=mapping, inplace=True)
 
        return self.df
 
