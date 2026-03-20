from Menu import Menu
from method_crud import MethodCrud
from method import Method


class User:
    def __init__(self):
        self.user    = Menu()
        self.crud    = MethodCrud() 
        self.methods = Method()      
        self.methods._df = self.crud._df

    def _user_session(self, username):
        while True:
            self.user._user_menu(username)
            choice = input("  Choose option: ").strip()

            if(choice == "1"):
                self.crud._select_industry()         
            elif(choice == "2"):
                self.methods._compare_products()      
            elif(choice == "3"):
                print(f"\n  Goodbye, {username}!")
                break
            else:
                print("  Invalid option.")