from Menu import Menu
from method_crud import MethodCrud
from method import Method


class Admin:

    def __init__(self):
        self.admin              = Menu()
        self.competitor_manager = MethodCrud()
        self.analytics_manager  = Method()        
        self.analytics_manager._df = self.competitor_manager._df  # share the same df

    def _admin_session(self):
        while True:
            self.admin._admin_menu()
            choice = input("  Choose option: ").strip()

            if(choice == "1"):
                self.competitor_manager.add_competitor()
                self.analytics_manager._df = self.competitor_manager._df  # keep in sync
            elif(choice == "2"):
                self.competitor_manager.update_competitor()
                self.analytics_manager._df = self.competitor_manager._df
            elif(choice == "3"):
                self.competitor_manager.delete_competitor()
                self.analytics_manager._df = self.competitor_manager._df            
            elif(choice == "4"):
                self.competitor_manager._browse_products() 
            elif(choice == "5"):
                self.analytics_manager.analytics()  
            elif(choice == "6"):
                print("\n  Admin logged out.")
                break
            else:
                print("  Invalid option.")

    def _organize_data(self):
        """Runs the organize_data script to build all_industries_organized.csv."""
        import os, sys
        organize_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../handlingDataset/organize_data.py")
        if(os.path.exists(organize_path)):
            os.system(f"{sys.executable} {organize_path}")
        else:
            print("  Error: organize_data.py not found.")