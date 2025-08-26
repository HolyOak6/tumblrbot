import requests
import os
from dotenv import load_dotenv
import random as rd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
"""Load environment variables from a .env file."""
unsp_access_key = os.getenv("UNSP_ACCESS_KEY")
unsp_key = os.getenv("UNSP_SECRET_KEY")
unsp_app_id = os.getenv("UNSP_APPLICATION_ID")
unsp_username = os.getenv("UNSP_USERNAME")
ninja_key = os.getenv("NINJA_KEY")
headers = {
    "Authorization": f"Client-ID {unsp_access_key}"
}
"""Common English stopwords to filter out from tags."""
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
    """A bot that fetches content from various APIs, including Unsplash for images,
    icanhazdadjoke for jokes, and api-ninjas for facts. It
    can also generate captions and process images.
    """
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
        """gets a photo from unsplash based on that photo's id (found at the end of the photo's url)
        returns a dictionary with keys:
            url - the url of the photo
            tags - a list of tags associated with the photo
            artist_first_name - first name of the artist
            artist_last_name - last name of the artist
            caption_text - a caption based on the photo's slug
        If no photo_id is provided, prompts the user to input one.

        """
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
        """Fetch a photo from the user's liked photos on Unsplash.
        If n is None, a random photo is selected.
        Returns a dictionary with keys
        url - the url of the photo
        tags - a list of tags associated with the photo
        artist_first_name - first name of the artist
        artist_last_name - last name of the artist
        caption_text - a caption based on the photo's slug
        """
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
        """
        Fetch an image from a URL and resize it to the target width while maintaining aspect ratio.
        Returns a PIL Image object.
        1. Fetch the image from the URL.
        2. Open the image using PIL.
        3. Calculate the new height to maintain aspect ratio.
        4. Resize the image using high-quality resampling.
        5. Return the resized image.
        6. Raise an exception if the image cannot be fetched.
        7. Use Image.LANCZOS for high-quality downsampling.
        8. Handle any request errors gracefully.
        """

        response = requests.get(url)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))

        # Resize to target width while keeping aspect ratio
        w_percent = target_width / float(img.width)
        h_size = int(float(img.height) * w_percent)
        img = img.resize((target_width, h_size), Image.LANCZOS)
        return img

    def get_background_image(self, query=None):
        """Fetch a random photo from Unsplash based on a query or a list of queries.
        If no query is provided, a default list of queries is used.
        Returns a dictionary with keys:
            url - the url of the photo
            tags - a list of tags associated with the photo
            artist_first_name - first name of the artist
            artist_last_name - last name of the artist
            caption_text - a caption based on the photo's slug
        1. If no query is provided, use a default list of queries.
        2. If a single string is provided, convert it to a list.
        3. Randomly select a query from the list.
        4. Make a request to the Unsplash random photo endpoint with the selected query.
        5. Extract relevant information from the response.
        6. Return the information as a dictionary.
        7. Handle any request errors gracefully.
        8. Filter out common stopwords from the tags.
        9. Print the caption text for debugging purposes.
        """
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
            returns joke as string
            """
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
        """Wrap text into multiple lines without breaking words.
        1. Split the text into words.
        2. Iterate through the words and build lines.
        3. If adding a word exceeds max_chars, start a new line.
        4. Join the lines with newline characters and return the result.
        5. Ensure no line exceeds max_chars.
        6. Handle edge cases like very long words gracefully.
        7. Maintain original spacing between words.
        8. Return the wrapped text as a single string."""
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
        """Fetch random quotes from the RealInspire API.
        1. Make a GET request to the RealInspire API with the specified limit.
        2. Parse the JSON response to extract quotes.
        3. Return the first quote's content if available.
        4. Handle any request errors gracefully.
        5. Use a timeout to avoid hanging requests.
        6. Validate the response status code.
        7. Return None if no quotes are found or an error occurs.
        8. Print error messages for debugging purposes.
        """
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
        """Retrieve a random fact from the api-ninjas facts API.
        Returns the fact as a string."""
        facturl = self.factapi
        factheaders = {"X-Api-Key": self.ninjakey}
        response = requests.get(url=facturl, headers=factheaders).json()
        fact = response[0]["fact"]
        return fact






    #________________________