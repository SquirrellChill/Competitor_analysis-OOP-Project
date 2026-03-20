import os
import sys
import pandas as pd
from io import StringIO

# Tell Python where to find organize_data.py
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../handlingDataset"))

# Now import normally
from organize_data import scan_columns, select_columns, convert_inr_to_usd, handle_currency_conversion
USERS_PATH      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
DATASET_PATH    = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../dataset/all_industries_organized.csv")
COMPETITOR_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../dataset/all_industries_organized.csv")

COMPETITOR_COLUMNS = ["product_name", "industry", "brand_name", "price_usd", "rating", "reviews", "category"]


class MethodCrud:
    def __init__(self):
        self._df = self._load_competitors()  # FIX: was empty, caused crashes everywhere

    # ── Load / Save ───────────────────────────────────────────────────────────────

    def _load_competitors(self):
        """Loads existing competitor CSV or returns empty DataFrame."""
        if(os.path.exists(COMPETITOR_PATH)):
            return pd.read_csv(COMPETITOR_PATH)
        return pd.DataFrame(columns=COMPETITOR_COLUMNS)

    def _save_competitors(self):
        """Saves the current competitor DataFrame to CSV."""
        self._df.to_csv(COMPETITOR_PATH, index=False)

    # ── Industry / Product view ───────────────────────────────────────────────────

    def _select_industry(self):
        """Industry → Brand → Category → Products sorted by rating (50 at a time)."""
        if(not os.path.exists(DATASET_PATH)):
            print("  Error: Organized dataset not found. Please run Organize Data first.")
            return

        df = pd.read_csv(DATASET_PATH)

        if('industry' not in df.columns):
            print(f"  Error: Column 'industry' not found. Available columns: {df.columns.tolist()}")
            return

        # ── Step 1: Pick Industry ─────────────────────────────────────────────────
        industries = (
            df['industry']
            .dropna().astype(str).str.strip()
            .unique().tolist()
        )
        industries.sort()

        print("\n" + "═"*38)
        print("         SELECT INDUSTRY")
        print("═"*38)
        for i, ind in enumerate(industries, 1):
            count = len(df[df['industry'] == ind])
            print(f"  [{i}] {ind:<20}  ({count} products)")
        print(f"  [0] Back")
        print("─"*38)

        try:
            choice = int(input("\n  Choose number: ").strip())
            if(choice == 0):
                return
            if(not (1 <= choice <= len(industries))):
                print("  Invalid selection.")
                return
            industry_name = industries[choice - 1]
        except ValueError:
            print("  Please enter a valid number.")
            return

        industry_df = df[df['industry'].str.strip() == industry_name]

        # ── Step 2: Pick Brand ────────────────────────────────────────────────────
        brand_col = 'brand_name' if 'brand_name' in industry_df.columns else 'brand'
        if(brand_col not in industry_df.columns):
            print("  No brand column found.")
            return

        brands = (
            industry_df[brand_col]
            .dropna().astype(str).str.strip()
            .unique().tolist()
        )
        brands.sort()

        print(f"\n" + "═"*38)
        print(f"  {industry_name.upper()} — SELECT BRAND")
        print("═"*38)
        for i, b in enumerate(brands, 1):
            count = len(industry_df[industry_df[brand_col].str.strip() == b])
            print(f"  [{i}] {b:<20}  ({count} products)")
        print(f"  [0] Back")
        print("─"*38)

        try:
            choice = int(input("\n  Choose number: ").strip())
            if(choice == 0):
                return
            if(not (1 <= choice <= len(brands))):
                print("  Invalid selection.")
                return
            brand_name = brands[choice - 1]
        except ValueError:
            print("  Please enter a valid number.")
            return

        brand_df = industry_df[industry_df[brand_col].str.strip() == brand_name]

        # ── Step 3: Pick Category ─────────────────────────────────────────────────
        cat_col = 'category' if 'category' in brand_df.columns else None

        if(cat_col):
            categories = (
                brand_df[cat_col]
                .dropna().astype(str).str.strip()
                .unique().tolist()
            )
            categories.sort()

            print(f"\n" + "═"*38)
            print(f"  {brand_name.upper()} — SELECT CATEGORY")
            print("═"*38)
            for i, cat in enumerate(categories, 1):
                count = len(brand_df[brand_df[cat_col].str.strip() == cat])
                print(f"  [{i}] {cat:<20}  ({count} products)")
            print(f"  [{len(categories)+1}] All Categories")
            print(f"  [0] Back")
            print("─"*38)

            try:
                choice = int(input("\n  Choose number: ").strip())
                if(choice == 0):
                    return
                elif(choice == len(categories) + 1):
                    final_df = brand_df.copy()
                    category_label = "All Categories"
                elif(1 <= choice <= len(categories)):
                    cat_name = categories[choice - 1]
                    final_df = brand_df[brand_df[cat_col].str.strip() == cat_name].copy()
                    category_label = cat_name
                else:
                    print("  Invalid selection.")
                    return
            except ValueError:
                print("  Please enter a valid number.")
                return
        else:
            final_df = brand_df.copy()
            category_label = "All"

        # ── Step 4: Display sorted by rating with pagination ──────────────────────
        self._view_products_paged(final_df, industry_name, brand_name, category_label)

    def _view_products_paged(self, df, industry_name, brand_name, category_label):
        """Displays products sorted by rating, 50 per page, with show-all option."""
        price_col  = 'price_usd' if 'price_usd' in df.columns else 'price'
        rating_col = 'rating'    if 'rating'    in df.columns else 'user_rating'

        sorted_df = df.copy()
        if(rating_col in sorted_df.columns):
            sorted_df = sorted_df.sort_values(by=rating_col, ascending=False).reset_index(drop=True)

        cols_to_show = [c for c in ['product_name', 'brand_name', price_col, rating_col, 'category'] if c in sorted_df.columns]
        total     = len(sorted_df)
        PAGE_SIZE = 50
        page      = 0

        while True:
            start = page * PAGE_SIZE
            end   = min(start + PAGE_SIZE, total)

            print("\n" + "═"*60)
            print(f"  {industry_name.upper()} › {brand_name} › {category_label}")
            print(f"  Showing {start+1}–{end} of {total} products  (sorted by rating ↓)")
            print("═"*60)
            print(sorted_df[cols_to_show].iloc[start:end].to_string(index=False))
            print("─"*60)

            options = []
            if(end < total):
                options.append("[N] Next 50")
            if(page > 0):
                options.append("[P] Previous 50")
            if(total > PAGE_SIZE):
                options.append("[A] Show All")
            options.append("[B] Back")

            print("  " + "   ".join(options))
            nav = input("\n  Choice: ").strip().upper()

            if(nav == "N" and end < total):
                page += 1
            elif(nav == "P" and page > 0):
                page -= 1
            elif(nav == "A" and total > PAGE_SIZE):
                print("\n" + "═"*60)
                print(f"  ALL {total} products — {industry_name} › {brand_name} › {category_label}  (sorted by rating ↓)")
                print("═"*60)
                print(sorted_df[cols_to_show].to_string(index=False))
                print("─"*60)
                input("\n  Press Enter to return.........")
                break
            elif(nav == "B"):
                break
            else:
                print("  Invalid option.")

    # ── CSV Helper Functions ──────────────────────────────────────────────────────
    # scan_columns, select_columns, convert_inr_to_usd, handle_currency_conversion
    # are imported from handlingDataset/organize_data.py

    def _suggest_column(self, std_col, available_cols):
        """Returns the best matching column name based on keyword similarity."""
        keywords = {
            "product_name": ["name", "product", "title", "item"],
            "industry":     ["industry", "sector", "category", "type"],
            "brand_name":   ["brand", "company", "manufacturer", "maker"],
            "price_usd":    ["price", "cost", "usd", "amount", "value"],
            "rating":       ["rating", "rate", "score", "stars", "review_score"],
            "reviews":      ["reviews", "review", "count", "feedback", "num_reviews"],
            "category":     ["category", "cat", "segment", "type", "class"],
        }

        hints = keywords.get(std_col, [std_col])
        for col in available_cols:
            col_lower = col.lower()
            if(any(hint in col_lower for hint in hints)):
                return col
        return None

    def _map_columns(self, df):
        """Maps existing column names to standard competitor column names using integer selection."""
        print("\n  ==== Column Mapping ====")
        print("  (press Enter to skip any field)")
        print("  " + "-" * 38)

        mapping = {}
        for std_col in COMPETITOR_COLUMNS:
            if(std_col in df.columns):
                continue

            # get remaining unmapped columns
            used       = list(mapping.keys())
            available  = [c for c in df.columns if c not in used]

            if(not available):
                break

            # find suggestion
            suggestion     = self._suggest_column(std_col, available)
            suggestion_idx = (available.index(suggestion) + 1) if suggestion else None

            # display numbered list
            print(f"\n  Map to '{std_col}':")
            for i, col in enumerate(available, 1):
                tag = "  ← suggested" if col == suggestion else ""
                print(f"    [{i}] {col}{tag}")

            if(suggestion_idx):
                prompt = f"  Enter number (suggested [{suggestion_idx}], Enter to skip): "
            else:
                prompt = f"  Enter number (Enter to skip): "

            user_input = input(prompt).strip()

            # accept Enter to use suggestion, or pick by number
            if(not user_input and suggestion):
                mapping[suggestion] = std_col
                print(f"  ✓ '{suggestion}' → '{std_col}'")
            elif(user_input.isdigit()):
                idx = int(user_input) - 1
                if(0 <= idx < len(available)):
                    mapping[available[idx]] = std_col
                    print(f"  ✓ '{available[idx]}' → '{std_col}'")
                else:
                    print("  Invalid number. Skipped.")
            else:
                print(f"  Skipped '{std_col}'.")

        if(mapping):
            df.rename(columns=mapping, inplace=True)

        return df

    def _convert_inr_to_usd(self, value, exchange_rate=0.012):
        """Converts INR string like ₹1,099 to a USD float."""
        try:
            cleaned = str(value).replace("₹", "").replace(",", "").strip()
            return round(float(cleaned) * exchange_rate, 2)
        except:
            return value

    def _handle_currency_conversion(self, df):
        """Optionally converts an INR price column to USD."""
        print("\n  Currency Conversion (press Enter to skip)")
        print("  " + "-" * 38)

        col_input = input("  Which column has INR prices (₹)? Name or number, or Enter to skip: ").strip()
        if(not col_input):
            return df

        try:
            col_name = df.columns[int(col_input) - 1]
        except (ValueError, IndexError):
            col_name = col_input

        if(col_name not in df.columns):
            print(f"  Column '{col_name}' not found. Skipping.")
            return df

        rate_input = input("  Exchange rate (default 1 INR = 0.012 USD, press Enter to confirm): ").strip()
        exchange_rate = float(rate_input) if rate_input else 0.012

        df[col_name] = df[col_name].apply(lambda x: self._convert_inr_to_usd(x, exchange_rate))
        df.rename(columns={col_name: col_name + "_usd"}, inplace=True)
        print(f"  Converted '{col_name}' → '{col_name}_usd' at rate {exchange_rate}")
        return df

    # ── Add competitor ────────────────────────────────────────────────────────────

    def add_competitor(self):
        """Entry point — prompts user to choose between manual input or CSV import."""
        print("\n==== Add New Competitor ====")
        print("  1. Manual input")
        print("  2. Import from CSV file")
        choice = input("\n  Choose option: ").strip()

        if(choice == "1"):
            self._add_manual()
        elif(choice == "2"):
            self._add_from_csv()
        else:
            print("  Invalid option.")

    def _add_manual(self):
        """Collects competitor data field by field from the terminal."""
        print("\n==== Add New Competitor (Manual) ====")

        try:
            product_name = input("  Product Name: ").strip()
            industry     = input("  Industry: ").strip()
            brand_name   = input("  Brand Name: ").strip()
            category     = input("  Category: ").strip()
            price_usd    = float(input("  Price (USD): "))
            rating       = float(input("  Rating: "))
            reviews      = int(input("  Reviews: "))

            new_row = {
                "product_name": product_name,
                "industry":     industry,
                "brand_name":   brand_name,
                "price_usd":    price_usd,
                "rating":       rating,
                "reviews":      reviews,
                "category":     category,
            }

            self._df = pd.concat([self._df, pd.DataFrame([new_row])], ignore_index=True)
            self._save_competitors()
            print(f"\n  Product '{product_name}' added successfully!")

        except ValueError:
            print("  Error: Price, Rating, and Reviews must be numeric.")

    def _add_from_csv(self):
        """Loads a CSV, scans columns, lets user select, trim, map, and convert."""
        path = input("\n  Enter path to CSV file: ").strip().strip('"').strip("'")

        if(not os.path.exists(path)):
            print("  Error: File not found.")
            return

        try:
            new_data = pd.read_csv(path)
            print("\n  File loaded successfully!")

            # Step 1: Scan and show columns
            scan_columns(new_data)

            # Step 2: Select columns to keep
            selected_cols = select_columns(new_data)

            # Step 3: Trim rows
            row_input = input(f"\n  How many rows to keep? (file has {len(new_data)} rows): ").strip()
            row_limit = int(row_input)
            new_data = new_data[selected_cols].head(row_limit).copy()

            # Step 4: Optional metadata
            print("\n  Optional Info (press Enter to skip)")
            print("  " + "-" * 38)
            industry   = input("  Industry: ").strip()
            brand_name = input("  Brand name: ").strip()

            if(industry):   new_data["industry"]   = industry
            if(brand_name): new_data["brand_name"] = brand_name

            # Step 5: Currency conversion
            new_data = handle_currency_conversion(new_data)

            # Step 6: Map columns to standard names
            new_data = self._map_columns(new_data)

            # Step 7: Merge and save
            self._df = pd.concat([self._df, new_data], ignore_index=True)
            self._save_competitors()
            print(f"\n  Successfully imported {len(new_data)} records!")

        except Exception as e:
            print(f"  Error reading CSV: {e}")

    # ── Update competitor ─────────────────────────────────────────────────────────

    def update_competitor(self):
        """Updates price and rating for an existing competitor product."""
        print("\n==== Update Competitor ====")
        name = input("  Enter the Product Name to update: ").strip()

        if(name in self._df['product_name'].values):
            print(f"  Updating details for: {name}")
            new_price  = input("  New Price (leave blank to keep current): ").strip()
            new_rating = input("  New Rating (leave blank to keep current): ").strip()

            idx = self._df[self._df['product_name'] == name].index[0]

            if(new_price):
                self._df.at[idx, 'price_usd'] = float(new_price)

            if(new_rating):
                self._df.at[idx, 'rating'] = float(new_rating)

            self._save_competitors()
            print(f"  Product '{name}' updated successfully.")
        else:
            print("  Product not found.")

    # ── Delete competitor ─────────────────────────────────────────────────────────

    def delete_competitor(self):
        """Removes a competitor product by name."""
        print("\n==== Delete Competitor ====")
        name_to_delete = input("  Enter Product Name to remove: ").strip()

        if(name_to_delete in self._df['product_name'].values):
            self._df = self._df[self._df['product_name'] != name_to_delete]
            self._save_competitors()
            print(f"  Product '{name_to_delete}' has been removed successfully.")
        else:
            print(f"  Product '{name_to_delete}' not found in the list.")

    # ── View competitors ──────────────────────────────────────────────────────────

    def view_competitors(self):
        """Displays current competitor list in the terminal."""
        print("\n── Current Competitor List ──")

        if(self._df.empty):
            print("  The list is currently empty.")
        else:
            cols_to_show = [c for c in ['product_name', 'industry', 'brand_name', 'price_usd', 'rating'] if c in self._df.columns]
            print(self._df[cols_to_show].head(15).to_string(index=False))

            total_count = len(self._df)
            if(total_count > 15):
                print(f"\n  ...... and {total_count - 15} more products.")

        input("\n  Press Enter to return.........")