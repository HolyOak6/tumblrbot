import requests
import os
from dotenv import load_dotenv
import random as rd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


load_dotenv()
unsp_access_key = os.getenv("UNSP_ACCESS_KEY")
unsp_key = os.getenv("UNSP_SECRET_KEY")
unsp_app_id = os.getenv("UNSP_APPLICATION_ID")
unsp_username = os.getenv("UNSP_USERNAME")
ninja_key = os.getenv("NINJA_KEY")
headers = {
    "Authorization": f"Client-ID {unsp_access_key}"
}
stopwords = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
        "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
        "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
        "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
        "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
        "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
        "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on",
        "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
        "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some",
        "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then",
        "there", "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
        "those", "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we",
        "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's",
        "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "with",
        "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
        "yourself", "yourselves"
    }


class ContentBot:
    def __init__(self):
        self.jokeapi = "https://icanhazdadjoke.com/"
        self.factapi = "http://api.api-ninjas.com/v1/facts"
        self.stopwords = stopwords
        self.unspheader = headers
        self.ninjakey = ninja_key
        self.unspusername = unsp_username
        self.unspappid = unsp_app_id
        self.unspkey = unsp_key
        self.unspaccesskey = unsp_access_key





#______________________________________________________Get a photo using ID
    def get_photo(self, photo_id=None):
        """gets a photo from unsplash based on that photo's id (found at the end of the photo's url)"""
        if not photo_id:
            photo_id = input("What is the ID of the photo you'd like?       ")
        # photo_id = "NuHrMrC5rlk"
        unsp_getphoto_url=f"https://api.unsplash.com/photos/{photo_id}"
        if not self.unspheader:
            return None

        try:
            response = requests.get(url=unsp_getphoto_url, headers=self.unspheader)
            response.raise_for_status()  # Raises an exception for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error fetching photo: {e}")
            return None  # stop here if request fails
        else:
            photo_data = response.json()

        first_name = photo_data["user"]["first_name"]
        last_name = photo_data["user"]["last_name"]
        photo_url = photo_data["urls"]["full"]
        slug_parts = photo_data["slug"].split("-")
        tags = [word for word in slug_parts[:-1] if word not in self.stopwords]

        photo_info = {
            "url": photo_url,
            "tags": tags,  # tag processing function
            "artist_first_name": first_name,
            "artist_last_name": last_name,
            "caption_text": " ".join(slug_parts[:-1])
        }
        return photo_info

    def get_from_likes(self, n=None):

        endpoint = f"/users/{self.unspusername}/likes"
        all_photos = []
        page = 1
        per_page = 30  # max allowed by Unsplash

        while True:
            params = {
                "username": self.unspusername,
                "per_page": per_page,
                "page": page
            }
            try:
                response = requests.get(url=f"https://api.unsplash.com/{endpoint}", headers=self.unspheader, params=params)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching photo: {e}")
                return None
            else:
                photo_data = response.json()
                if not photo_data:
                    break  # no more photos
                all_photos.extend(photo_data)
                page += 1

        if not all_photos:
            print("No liked photos found.")
            return None

        if n is None:
            n = rd.randint(0, len(all_photos) - 1)

        first_name = all_photos[n]["user"]["first_name"]
        last_name = all_photos[n]["user"]["last_name"]
        photo_url = all_photos[n]["urls"]["full"]
        slug_parts = all_photos[n]["slug"].split("-")
        tags = [word for word in slug_parts[:-1] if word not in self.stopwords]

        photo_info = {
            "url": photo_url,
            "tags": tags,
            "artist_first_name": first_name,
            "artist_last_name": last_name,
            "caption_text": " ".join(slug_parts[:-1])
        }
        print(photo_info["caption_text"])
        return photo_info





    def fetch_and_resize_image(self, url, target_width):
        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))

        # Resize to target width while keeping aspect ratio
        w_percent = target_width / float(img.width)
        h_size = int(float(img.height) * w_percent)
        img = img.resize((target_width, h_size), Image.LANCZOS)
        return img

    def get_background_image(self, query=None):
        """from Unsplash"""
        random_endpoint = "/photos/random"

        # Default list of queries
        if query is None:
            query = ["sunset", "clouds", "mountains", "night sky", "aurora", "coffee cup", "blossoms"]

        # If a single string is passed, wrap it in a list
        if isinstance(query, str):
            query = [query]

        # Now you can loop through or randomly choose one
        chosen_query = rd.choice(query)
        params = {
            "query" : chosen_query,
            "orientation" : "landscape"
        }
        try:
            response = requests.get(url=f"https://api.unsplash.com/{random_endpoint}", headers=self.unspheader, params=params)
            response.raise_for_status()  # Raises an exception for HTTP errors
        except requests.exceptions.RequestException as e:
            print(f"Error fetching photo: {e}")
            return None  # stop here if request fails
        else:
            photo_data = response.json()

        first_name = photo_data["user"]["first_name"]
        last_name = photo_data["user"]["last_name"]
        photo_url = photo_data["urls"]["full"]
        slug_parts = photo_data["slug"].split("-")
        tags = [word for word in slug_parts[:-1] if word not in self.stopwords]

        photo_info = {
            "url": photo_url,
            "tags": tags,
            "artist_first_name": first_name,
            "artist_last_name": last_name,
            "caption_text": " ".join(slug_parts[:-1])
        }
        print(photo_info["caption_text"])
        return photo_info

    def get_dadjoke(self):
        """Retrieve dad joke from icanhazdadjoke api
            returns joke as string"""
        jokeheaders = {"Accept": "application/json"}
        try:
            response = requests.get(self.jokeapi, headers=jokeheaders)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching quote: {e}")
            return None  # stop here if request fails
        else:
            return response.json()["joke"]






    def wrap_text(self, text, max_chars=45):
        """Wrap text into multiple lines without breaking words."""
        words = text.split()
        lines, current_line = [], ""

        for word in words:
            # If adding the next word exceeds max_chars, start a new line
            if len(current_line) + len(word) + (1 if current_line else 0) > max_chars:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " "
                current_line += word

        if current_line:
            lines.append(current_line)

        return "\n".join(lines)

    def get_random_quotes(self, limit=1):
        quoteurl = f"https://api.realinspire.live/v1/quotes/random?limit={limit}"
        try:
            response = requests.get(quoteurl, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad status codes
            quotes = response.json()
            if quotes:
                return quotes[0]["content"]
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve quotes: {e}")
            return None

    def get_fact(self):
        facturl = self.factapi
        factheaders = {"X-Api-Key": self.ninjakey}
        response = requests.get(url=facturl, headers=factheaders).json()
        fact = response[0]["fact"]
        return fact






    #________________________