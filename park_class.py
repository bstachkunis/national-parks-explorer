import requests

class NationalParksAPI:
    def __init__(self):
        self.current_page = 1
        self.per_page = 500
        self.api_key = ""
        self.np_url = "https://developer.nps.gov/api/v1/parks"
        self.park_list = []
    
    def get_all_parks(self, page, per_page=20):
        np_url = "https://developer.nps.gov/api/v1/parks"
        api_key = ""

        params = {
            "api_key": api_key,
            "start": (page - 1) * per_page,
            "limit": per_page,
        }
        response = requests.get(np_url, params=params)

        if response.status_code == 200:
            data = response.json()
            all_parks = data["data"]
            nat_parks_list = [park["fullName"] for park in all_parks if park["designation"] == "National Park"]
            return nat_parks_list
        else:
            print("Failed to get park names")