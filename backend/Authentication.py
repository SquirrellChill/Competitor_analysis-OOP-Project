import os
import json
from user import User
from Menu import Menu
from admin import Admin
USERS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
#__________________Kimheng's Part________________________
class AuthSystem:

    def __init__(self):
        self._users = self._load_users()
        self.menu=Menu()
        self.admin=Admin()
        self.user=User()

    # ── User persistence ─────────────────────────

    def _load_users(self):
        if os.path.exists(USERS_PATH):
            with open(USERS_PATH, 'r') as f:
                return json.load(f)
        return {}

    def _save_users(self):
        with open(USERS_PATH, 'w') as f:
            json.dump(self._users, f, indent=2)

    # ── Password validation ──────────────────────

    def _validate_password(self, password):
        special = "!@#$%&*()"
        if len(password) < 8:
            print("  ✗ Must be at least 8 characters.")
            return False
        if not any(c.isupper() for c in password):
            print("  ✗ Must contain uppercase letter.")
            return False
        if not any(c.islower() for c in password):
            print("  ✗ Must contain lowercase letter.")
            return False
        if not any(c.isdigit() for c in password):
            print("  ✗ Must contain a number.")
            return False
        if not any(c in special for c in password):
            print("  ✗ Must contain special character.")
            return False
        return True

    # ── Auth actions ─────────────────────────────
    #__Admin_____________________________________
    def _is_admin(self, username, password):
        return username == "Kimheng" and password == "Kimheng123!"

    def _register(self):
        print("\n── Register ──")

        while True:
            username = input("  Username: ").strip()
            if not username:
                print("  Username cannot be empty.")
            elif username in self._users:
                print("  Username already exists.")
            else:
                break

        while True:
            password = input("  Password: ").strip()
            if self._validate_password(password):
                break

        self._users[username] = password
        self._save_users()

        print(f"\n  ✓ Registered successfully!")

    def _login(self):
        print("\n── Login ──")

        username = input("  Username: ").strip()
        password = input("  Password: ").strip()

        if self._is_admin(username, password):
            print("\n  Admin login successful!")
            self.admin._admin_session()
            return

        if username in self._users and self._users[username] == password:
            print(f"\n  ✓ Login successful! Welcome, {username}")
            self.user._user_session(username)
        else:
            print("\n  ✗ Invalid username or password.")

    def _forgot_password(self):
        print("\n── Forgot Password ──")

        username = input("  Username: ").strip()

        if username in self._users:
            print(f"  Your password is: {self._users[username]}")
        else:
            print("  Username not found.")

    # ── Main loop ────────────────────────────────

    def run(self):
        while True:
            self.menu._display_menu()
            choice = input("  Choose option: ").strip()

            if choice == "1":
                self._register()
            elif choice == "2":
                self._login()
            elif choice == "3":
                self._forgot_password()
            elif choice == "4":
                print("\n  Goodbye!")
                break
            else:
                print("  Invalid option.")