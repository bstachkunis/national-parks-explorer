import requests
from park_class import NationalParksAPI
import time

class NationalParks(NationalParksAPI):
    def __init__(self):
        super().__init__()
        self.filter_dict = {"states": [], "activities": []}
    
    
    def main(self):
        print ("Welcome to the National Parks Recommendation Application!\n")
        print("This application will educate you about National Parks in the United States and or help you determine which park you should visit based on preferences you have.\n")

        while True:
            print("Would you like to continue? 1. Yes 2. No\n")
            choice = str(input()).lower()

            if choice == "1" or choice == "yes":
                self.main_menu()
            elif choice == "2" or choice == "no":
                print("Thanks for using the National Parks Recommendation Application! Good Bye.")
                break
            else:
                print("invalid input, please try again")

    def main_menu(self):
        print("National Parks Application Help Menu (please select from the following):\n")

        user_options = ["1. Generate Random Park", "2. Park List", "3. Filter Parks", "4. View My Saved Parks", "5. Quit", "6. Help"]

        for option in user_options:
            print(option)
        
        user_choice = str(input()).lower()

        if user_choice == "1" or user_choice == "generate random park":
            self.get_random_park()
        elif user_choice == "2" or user_choice == "park list":
            all_parks = self.get_all_parks(self.current_page, self.per_page)
            self.print_and_format_parks(all_parks)
        elif user_choice == "3" or user_choice == "filter parks":
            self.filter_parks_menu()
        elif user_choice == "4" or user_choice == "view my saved parks":
            self.save_park_list()
        elif user_choice == "5" or user_choice == "quit":
            print("Thank you for using the National Parks App! Good Bye!")
            exit()
        elif user_choice == "6" or user_choice == "help":
            self.user_help_guide()
            

    def get_park_data(self, park_name):
       params = {
           "api_key": self.api_key,
           "q": park_name
       }
       response = requests.get(self.np_url, params=params)

       if response.status_code == 200:
            data = response.json()
            park_data = data["data"]
            if park_data:
                description = park_data[0].get("description", "Description not available.")
                activities = park_data[0].get("activities", [])
                state = park_data[0].get("states", "State information not available")
                print(f'\nDescription for {park_name} located in {state}:\n')
                print(f'{description}\n')
                print("Activities:")
                for activity in activities:
                    activity_name = activity.get("name", "Unknown Activity")
                    print(f"{activity_name}")
                print("Would you like to save this park to your list?")
                print("1. Yes or 2. No?")
                user_choice = str(input()).lower()
                if user_choice == "1" or user_choice == "yes":
                    self.save_park_list(park_name)
                elif user_choice == "2" or user_choice =="no":
                    self.main_menu()
            else:
                print(f"Park '{park_name}' not found.")

    def get_all_parks(self, page, per_page=20):
        params = {
            "api_key": self.api_key,
            "start": (page - 1) * per_page,
            "limit": per_page,
        }
        response = requests.get(self.np_url, params=params)

        if response.status_code == 200:
            data = response.json()
            all_parks = data["data"]
            filter_list_lower = [filter_field.lower() for filter_field in self.filter_dict["activities"]]
            filtered_parks = []

            for park in all_parks:
                designation = park.get("designation", "")
                if designation == "National Park":
                    park_activities_lower = [activity["name"].lower() for activity in park.get("activities", [])]
                    activities_match = any(filter_field in park_activities_lower for filter_field in filter_list_lower)
                    states_match = any(state_code in park.get("states", []) for state_code in self.filter_dict["states"])

                    if self.filter_dict.get("activities") and self.filter_dict.get("states") and states_match and activities_match:
                        filtered_parks.append(park["fullName"])
                    elif self.filter_dict.get("activities") and not self.filter_dict.get("states") and activities_match:
                        filtered_parks.append(park["fullName"])
                    elif not self.filter_dict.get("activities") and self.filter_dict.get("states") and states_match:
                        filtered_parks.append(park["fullName"])
                    elif not self.filter_dict.get("activities") and not self.filter_dict.get("states"):
                        filtered_parks.append(park["fullName"])
            return filtered_parks
        else:
            print("Failed to get park names")

    def print_and_format_parks(self, all_parks):
        if all_parks:
                print("National Parks:\n")
                for index, park in enumerate(all_parks, start=1):
                    print(f'{index}. {park}')
                print("Navigation: 1. Search Park 2. Main Menu\n")
                user_nav = str(input()).lower()
                if user_nav == "1" or user_nav == "search park":
                    print("Please enter the park you would like you look up (name): ")
                    park_name = input()
                    self.get_park_data(park_name)
                else:
                    self.main_menu()

    def get_random_park(self):
        try:
            microservice_response = requests.get("http://127.0.0.1:5000/generate_random_park")
            microservice_response.raise_for_status()
        except requests.exceptions.RequestException:
            print("Error! Microservice Not Running. Please assure it is running and try again.")
            return
        print("Now generating random park . . . .")
        time.sleep(3)
        print(microservice_response.text)
        more_random = input("Generate another? (Yes/No) ").lower()
        if more_random == "yes":
            self.get_random_park()
        else:
            self.main_menu()

    def filter_parks_menu(self):
        print("Add any of the following to your search to find a park?\n 1. By State\n 2. By Activity\n 3. Show Filters\n 4. Stop Filtering\n 5. Clear Filters\n")
        user_selection = input()
        if user_selection == "1":
            state_selection = input("Please enter a 2 letter code for a state: ").upper()
            self.filter_dict["states"].append(state_selection)
            print(f'{state_selection} added to filter list!')
            self.filter_parks_menu()
        elif user_selection == "2":
            activity_selection = input("Please enter an activity: ")
            self.filter_dict["activities"].append(activity_selection)
            print(f'{activity_selection} added to filter list!')
            self.filter_parks_menu()
        elif user_selection == "3":
            print(f'Here are/is your current filter(s): {self.filter_dict}')
            self.filter_parks_menu()
        elif user_selection == "4":
            self.main_menu()
        elif user_selection == "5":
            self.filter_dict = {"states": [], "activities": []}
            print("Filter list cleared!")
            self.filter_parks_menu()

        

    def user_help_guide(self):
        print("\nWelcome to the user help guide! What would you like help with today? (please select a number) \n")
        options = ["1. What is this application?", "2. All parks data feature", "3. Random park generation", "4. Filter parks", "5. Saved Parks", "6. Main Menu"]

        for option in options:
            print(option)
        
        user_choice = input()

        if user_choice == "1":
            print("This is the national parks recommendation application. This application utilizes the national parks API to fetch data about the main national\
                   parks in the United States to help recommend parks and educate users about them.")
        elif user_choice == "2":
            print("When selecting the all parks feature, the user will be given a list of all the national parks recognized parks in the United States according to the API. From here, the user can select a single park to get information on.")
        elif user_choice == "3":
            print("The generate random parks option is a feature that has been implementend by a partner. This will use a local host endpoint to randomly generate a park for the user.")
        elif user_choice == "4":
            print("The filter parks feature allows the user to filter parks based on preferences. The benefit of using this feature is that parks can be more narrowed down to what the user wants rather than looking up and getting information from individual parks.")
        elif user_choice == "5":
            print("The saved parks feature allows the users to save parks they liked and come back to them later. This allows the user to decide between a few parks in order to make a decision on which park they would like to visit.")
        elif user_choice == "6":
            self.main_menu()
        else:
            print("Uh oh! Input not recognized. Please try again.")
            self.user_help_guide()
        self.user_help_guide()


    def save_park_list(self, park_name=None):
        if park_name != None:
            self.park_list.append(park_name)
            print(f"You saved {park_name} to your list.\n")
        user_choice = input("\nWould you like to 1. Add more parks/Go Back, 2. Edit my saved parks: ")
        if user_choice == "1":
            self.main_menu()
        elif user_choice == "2":
            print(f'\nHere is your current park list: {self.park_list}\n')
            user_response = input("\nWhich park would you like to edit? Please enter the park name or enter return to go back to the main menu: ")
            if user_response in self.park_list:
                user_entered = input(f"\nDeleting {user_response} from your list. Are you sure you want to delete?\nEnter 1 to continue or 2 to navigate back to park list menu: ")
                if user_entered == "1":
                    self.park_list.remove(user_response)
                    print(f"\nYou successfully removed {user_response} from your park list!")
                    user_pick = input("\nEnter 1 to undo or enter anything else to return to the main menu: ")
                    if user_pick != "1":
                        self.main_menu()
                else:
                    self.save_park_list(park_name)
        else:
            print("Invalid input! Please try again")
            self.save_park_list(park_name)
        

if __name__ == '__main__':
    national_parks_inst = NationalParks()
    national_parks_inst.main()