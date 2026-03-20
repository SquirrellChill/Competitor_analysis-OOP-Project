import pandas as pd
import os

USERS_PATH   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
DATASET_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../dataset/all_industries_organized.csv")

#_______________Sreka's Part_______________________
class Method:
    def __init__(self):
        self._df = pd.DataFrame()

    # ── Helpers ───────────────────────────────────────────────────────────────────

    def _load_dataset(self):
        """Loads the organized dataset. Returns None if not found."""
        if(not os.path.exists(DATASET_PATH)):
            print("  Dataset not found. Please run Organize Data from the admin panel first.")
            return None
        return pd.read_csv(DATASET_PATH)

    def _get_col(self, df, *candidates):
        """Returns the first column name from candidates that exists in df."""
        for col in candidates:
            if(col in df.columns):
                return col
        return None

    # ── Step 1: Select Industry ───────────────────────────────────────────────────

    def _pick_industry(self, df):
        """Shows unique industries and returns the one the user picks."""
        industry_col = self._get_col(df, 'industry', 'source')
        if(not industry_col):
            print("  No industry column found in dataset.")
            return None

        industries = (
            df[industry_col]
            .dropna()
            .astype(str)
            .str.strip()
            .unique().tolist()
        )
        industries.sort()

        print("\n  Select Industry")
        print("  " + "-" * 36)
        for i, ind in enumerate(industries, 1):
            print(f"  [{i}] {ind}")

        choice = input("\n  Choose industry number: ").strip()

        try:
            idx = int(choice) - 1
            if(0 <= idx < len(industries)):
                return industries[idx], industry_col
            else:
                print("  Invalid selection.")
                return None, None
        except ValueError:
            print("  Please enter a valid number.")
            return None, None

    # ── Step 2: Select Brand ──────────────────────────────────────────────────────

    def _pick_brand(self, df):
        """Shows unique brands in the filtered df and returns the one the user picks."""
        brand_col = self._get_col(df, 'brand_name', 'brand')
        if(not brand_col):
            print("  No brand column found.")
            return None, None

        brands = (
            df[brand_col]
            .dropna()
            .astype(str)
            .str.strip()
            .unique().tolist()
        )
        brands.sort()

        print("\n  Select Brand to Compare Against")
        print("  " + "-" * 36)
        for i, b in enumerate(brands, 1):
            print(f"  [{i}] {b}")

        choice = input("\n  Choose brand number: ").strip()

        try:
            idx = int(choice) - 1
            if(0 <= idx < len(brands)):
                return brands[idx], brand_col
            else:
                print("  Invalid selection.")
                return None, None
        except ValueError:
            print("  Please enter a valid number.")
            return None, None

    # ── Step 3: Get user's own product ───────────────────────────────────────────

    def _get_my_product(self):
        """Asks user to enter their own product details."""
        print("\n  Enter Your Product Details")
        print("  " + "-" * 36)

        try:
            my_name    = input("  Product name : ").strip()
            my_price   = float(input("  Price (USD)  : "))
            my_rating  = float(input("  Rating (0-5) : "))
            my_reviews = int(input("  Reviews count: "))
            return {
                "product_name": my_name,
                "price":        my_price,
                "rating":       my_rating,
                "reviews":      my_reviews,
            }
        except ValueError:
            print("  Error: Price, Rating, and Reviews must be numeric.")
            return None

    # ── Step 4: Compare & Recommend ───────────────────────────────────────────────

    def _show_comparison(self, my_product, market_df):
        """Compares user's product against the market and gives recommendations."""
        price_col   = self._get_col(market_df, 'price_usd', 'price')
        rating_col  = self._get_col(market_df, 'rating', 'user_rating')
        reviews_col = self._get_col(market_df, 'reviews', 'user_reviews')

        market_avg_price   = market_df[price_col].mean()
        market_avg_rating  = market_df[rating_col].mean()
        market_top_rating  = market_df[rating_col].max()
        market_avg_reviews = market_df[reviews_col].mean() if reviews_col else 0

        my_price   = my_product["price"]
        my_rating  = my_product["rating"]
        my_reviews = my_product["reviews"]

        # ── Summary Table ───────────────────────────────
        print("\n  ═══════════════════════════════════════")
        print("         Market Comparison Report")
        print("  ═══════════════════════════════════════")
        print(f"  {'Metric':<20} {'Yours':>10} {'Market Avg':>12}")
        print("  " + "-" * 44)
        print(f"  {'Price (USD)':<20} {'${:.2f}'.format(my_price):>10} {'${:.2f}'.format(market_avg_price):>12}")
        print(f"  {'Rating':<20} {'{:.2f}'.format(my_rating):>10} {'{:.2f}'.format(market_avg_rating):>12}")
        if(reviews_col):
            print(f"  {'Reviews':<20} {str(my_reviews):>10} {'{:.0f}'.format(market_avg_reviews):>12}")
        print("  " + "-" * 44)

        # ── Rating Position ─────────────────────────────
        if(my_rating >= market_top_rating):
            print("\n  ★ Your rating is TOP in this market!")
        elif(my_rating >= market_avg_rating):
            gap = market_top_rating - my_rating
            print(f"\n  ✓ Your rating is ABOVE market average.")
            print(f"  ↑ {gap:.2f} points away from the top rated product.")
        else:
            gap = market_avg_rating - my_rating
            print(f"\n  ✗ Your rating is BELOW market average by {gap:.2f} points.")

        # ── Price Position ──────────────────────────────
        if(my_price < market_avg_price * 0.8):
            print("  $ Your price is significantly LOWER than market average.")
        elif(my_price > market_avg_price * 1.2):
            print("  $ Your price is significantly HIGHER than market average.")
        else:
            print("  $ Your price is within the market range.")

        # ── Top 5 competitors in this segment ───────────
        top5 = market_df.sort_values(by=rating_col, ascending=False).head(5)
        print("\n  Top 5 in this segment:")
        print("  " + "-" * 44)
        for _, row in top5.iterrows():
            print(f"  {str(row['product_name']):<28} rating: {row[rating_col]}  ${row[price_col]}")

        # ── Recommendations ─────────────────────────────
        self._give_recommendations(my_product, market_avg_rating, market_avg_price, market_df, rating_col, price_col)

    def _give_recommendations(self, my_product, market_avg_rating, market_avg_price, market_df, rating_col, price_col):
        """Gives startup recommendations based on product position in the market."""
        my_rating = my_product["rating"]
        my_price  = my_product["price"]

        print("\n  ═══════════════════════════════════════")
        print("           Startup Recommendations")
        print("  ═══════════════════════════════════════")

        has_recommendation = False

        # Low rating advice
        if(my_rating < market_avg_rating):
            has_recommendation = True
            print("\n  [Rating] Your rating is below the market average.")

            # find top rated products for inspiration
            top_rated = market_df.sort_values(by=rating_col, ascending=False).head(3)
            print("  → Study these top-rated products for quality benchmarks:")
            for _, row in top_rated.iterrows():
                print(f"    • {row['product_name']} — rating: {row[rating_col]}")

            if(my_rating < 3.0):
                print("  → Consider focusing on product quality improvements before scaling.")
                print("  → Gather customer feedback to identify the biggest pain points.")
            elif(my_rating < market_avg_rating):
                print("  → Small quality improvements could bring you to market average.")
                print("  → Offer promotions or bundles to gather more reviews and boost visibility.")

        # Price advice
        if(my_price > market_avg_price * 1.2):
            has_recommendation = True
            print("\n  [Pricing] Your price is above market average.")
            print("  → Make sure your product has a clear premium value proposition.")
            print("  → Highlight unique features that justify the higher price.")
            print("  → Consider a lower entry-tier product to capture price-sensitive buyers.")

        elif(my_price < market_avg_price * 0.8):
            has_recommendation = True
            print("\n  [Pricing] Your price is below market average.")
            print("  → Low price can attract early customers — use this as a growth strategy.")
            print("  → Once you build reviews and trust, gradually increase pricing.")

        # Low reviews advice
        if(my_product["reviews"] < 10):
            has_recommendation = True
            print("\n  [Reviews] You have very few reviews.")
            print("  → Offer your product to early users in exchange for honest reviews.")
            print("  → Make the review process as easy as possible for customers.")
            print("  → Reviews build trust — prioritise this in your first 3 months.")

        # All good
        if(not has_recommendation):
            print("\n  ✓ Your product is performing well against the market!")
            print("  → Keep maintaining quality and continue collecting reviews.")
            print("  → Consider expanding to adjacent product categories.")

        print("\n  " + "─" * 38)

    # ── Main entry: Compare Products ─────────────────────────────────────────────

    def _compare_products(self):
        """Full startup comparison flow: industry → brand → my product → report."""
        df = self._load_dataset()
        if(df is None):
            return

        # Step 1: Pick industry
        industry, industry_col = self._pick_industry(df)
        if(not industry):
            return

        industry_df = df[df[industry_col].str.lower().str.strip() == industry.lower().strip()]

        # Step 2: Pick brand to compare against
        brand, brand_col = self._pick_brand(industry_df)
        if(not brand):
            return

        market_df = industry_df[industry_df[brand_col].str.lower().str.strip() == brand.lower().strip()].copy()

        if(market_df.empty):
            print(f"  No products found for brand '{brand}' in '{industry}'.")
            return

        print(f"\n  Comparing against: {brand} ({len(market_df)} products in {industry})")

        # Step 3: Enter own product
        my_product = self._get_my_product()
        if(not my_product):
            return

        # Step 4: Show comparison + recommendations
        self._show_comparison(my_product, market_df)

        input("\n  Press Enter to return.........")

    # ── Analytics ────────────────────────────────────────────────────────────────

    def analytics(self):
        while True:
            print("\n  Analytics Menu")
            print("  ─" * 18)
            print("  1. Compare with dataset")
            print("  2. Top rated competitors")
            print("  3. Price breakdown by industry")
            print("  4. Recommendation")
            print("  5. Back")
            choice = input("  Choose option: ").strip()

            if(choice == "1"):
                self._compare_with_dataset()
            elif(choice == "2"):
                self._top_rated()
            elif(choice == "3"):
                self._price_breakdown()
            elif(choice == "4"):
                self.recommend_products()
            elif(choice == "5"):
                break
            else:
                print("  Invalid option.")

    def _compare_with_dataset(self):
        if(self._df.empty):
            print("  No competitor data.")
            return

        dataset = self._load_dataset()
        if(dataset is None):
            return

        # Step 1: pick an industry to compare against
        industry, industry_col = self._pick_industry(dataset)
        if(not industry):
            return

        # Step 2: filter market to that industry only
        # also exclude competitors_combined rows so we don't compare against ourselves
        market_df = dataset[
            dataset[industry_col].str.lower().str.strip() == industry.lower().strip()
        ].copy()

        if(market_df.empty):
            print(f"  No market data found for '{industry}'.")
            return

        # Step 3: filter competitor data to same industry if possible
        comp_industry_col = self._get_col(self._df, 'industry')
        if(comp_industry_col):
            comp_df = self._df[
                self._df[comp_industry_col].str.lower().str.strip() == industry.lower().strip()
            ]
        else:
            comp_df = self._df

        if(comp_df.empty):
            print(f"  No competitor data found for industry '{industry}'.")
            return

        price_col  = self._get_col(market_df, 'price_usd', 'price')
        rating_col = self._get_col(market_df, 'rating', 'user_rating')

        comp_price_col  = self._get_col(comp_df, 'price_usd', 'price')
        comp_rating_col = self._get_col(comp_df, 'rating', 'user_rating')

        avg_comp_price    = comp_df[comp_price_col].mean()
        avg_comp_rating   = comp_df[comp_rating_col].mean()
        avg_market_price  = market_df[price_col].mean()
        avg_market_rating = market_df[rating_col].mean()

        print(f"\n  Market Comparison — {industry}")
        print("  " + "─" * 44)
        print(f"  {'Metric':<22} {'Competitors':>12} {'Market Avg':>12}")
        print("  " + "-" * 44)
        print(f"  {'Avg Price (USD)':<22} {'${:.2f}'.format(avg_comp_price):>12} {'${:.2f}'.format(avg_market_price):>12}")
        print(f"  {'Avg Rating':<22} {'{:.2f}'.format(avg_comp_rating):>12} {'{:.2f}'.format(avg_market_rating):>12}")
        print(f"  {'Products tracked':<22} {str(len(comp_df)):>12} {str(len(market_df)):>12}")
        print("  " + "-" * 44)

        if(avg_comp_rating > avg_market_rating):
            diff = avg_comp_rating - avg_market_rating
            print(f"\n  ✓ Competitors perform ABOVE market average by {diff:.2f} points.")
        else:
            diff = avg_market_rating - avg_comp_rating
            print(f"\n  ✗ Competitors perform BELOW market average by {diff:.2f} points.")

        if(avg_comp_price > avg_market_price * 1.1):
            print("  $ Competitor prices are HIGHER than the market average.")
        elif(avg_comp_price < avg_market_price * 0.9):
            print("  $ Competitor prices are LOWER than the market average.")
        else:
            print("  $ Competitor prices are in line with the market average.")

    def _top_rated(self):
        if(self._df.empty):
            print("  No competitor data.")
            return

        top = self._df.sort_values(by="rating", ascending=False).head(10)

        print("\n  Top Rated Competitors")
        print("  ────────────────────────")
        for _, row in top.iterrows():
            print(f"  {row['product_name']} | {row['rating']} | ${row['price_usd']}")

    def _price_breakdown(self):
        if(self._df.empty):
            print("  No competitor data.")
            return

        breakdown = self._df.groupby("industry")["price_usd"].mean()

        print("\n  Average Price by Industry")
        print("  ────────────────────────")
        for industry, price in breakdown.items():
            print(f"  {industry}: ${price:.2f}")

    def recommend_products(self):
        dataset = self._load_dataset()
        if(dataset is None):
            return

        industry, industry_col = self._pick_industry(dataset)
        if(not industry):
            return

        filtered    = dataset[dataset[industry_col].str.lower().str.strip() == industry.lower()].copy()
        price_col   = self._get_col(filtered, 'price_usd', 'price')
        rating_col  = self._get_col(filtered, 'rating', 'user_rating')
        reviews_col = self._get_col(filtered, 'reviews', 'user_reviews')
        brand_col   = self._get_col(filtered, 'brand_name', 'brand')

        if(filtered.empty):
            print("  No products found.")
            return

        filtered['score'] = (
            filtered[rating_col] * 0.6 +
            (filtered[reviews_col] / filtered[reviews_col].max()) * 0.3 +
            (1 / filtered[price_col]) * 0.1
        )

        top = filtered.sort_values(by="score", ascending=False).head(5)

        print(f"\n  Top Recommended Products in {industry}")
        print("  ────────────────────")
        for _, row in top.iterrows():
            print(
                f"  {row['product_name']} | {row[brand_col]} | "
                f"${row[price_col]} | {row[rating_col]}"
            )