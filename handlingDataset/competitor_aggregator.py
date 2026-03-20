import pandas as pd
from io import StringIO

# ─────────────────────────────────────────────────────────────
#  CLASS 2: CompetitorAggregator
#  Collects all competitor DataFrames and merges into one file
# ─────────────────────────────────────────────────────────────
 
class CompetitorAggregator:
 
    def __init__(self):
        self.competitors = []
 
    def add(self, df):
        if df is not None and not df.empty:
            self.competitors.append(df)
 
    def merge(self):
        if not self.competitors:
            print("No competitor data to merge.")
            return None
 
        merged = pd.concat(self.competitors, ignore_index=True)
 
        # Reorder: put competitor_name first
        cols = merged.columns.tolist()
        if "competitor_name" in cols:
            cols.insert(0, cols.pop(cols.index("competitor_name")))
            merged = merged[cols]
 
        return merged
 
    def save(self, output_path="competitors_combined.csv"):
        merged = self.merge()
        if merged is None:
            return
 
        if not output_path.endswith(".csv"):
            output_path += ".csv"
 
        merged.to_csv(output_path, index=False)
        print(f"\nSaved combined file to: {output_path}")
        print(f"Total rows: {len(merged)} | Columns: {len(merged.columns)}")
        print(f"Competitors: {merged['competitor_name'].unique().tolist()}")
 