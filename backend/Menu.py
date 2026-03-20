class Menu:
    def _display_menu(self):
        print("\n" + "═"*35)
        print("       COMPETITOR TRACKER")
        print("═"*35)
        print("  1. Register")
        print("  2. Login")
        print("  3. Forgot Password")
        print("  4. Exit")
        print("─"*35)

    def _user_menu(self, username):
        print(f"\n  Welcome, {username}!")
        print("─"*35)
        print("  1. Select Industry")
        print("  2. Compare Products")
        print("  3. Logout")
        print("─"*35)

    def _admin_menu(self):
        print("\n" + "═"*35)
        print("         ADMIN PANEL")
        print("═"*35)
        print("  1. Add Competitor")
        print("  2. Update Competitor")
        print("  3. Delete Competitor")
        print("  4. Organize Data")
        print("  5. Select Industry")
        print("  6. View Competitors")
        print("  7. Analytics")
        print("  8. Logout")
        print("─"*35)        