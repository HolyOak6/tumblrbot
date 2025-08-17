import requests
import os
from pprint import pprint
from dotenv import load_dotenv
import random as rd
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
unsp_access_key = os.getenv("UNSP_ACCESS_KEY")
unsp_key = os.getenv("UNSP_SECRET_KEY")
unsp_app_id = os.getenv("UNSP_APPLICATION_ID")
unsp_username = os.getenv("UNSP_USERNAME")
zenkey = os.getenv("ZENKEY")
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
dadjokes_url= "https://icanhazdadjoke.com/"

#______________________________________________________Get a photo using ID
def get_photo():
    photo_id = input("What is the ID of the photo you'd like?       ")
    # photo_id = "NuHrMrC5rlk"
    unsp_getphoto_url=f"https://api.unsplash.com/photos/{photo_id}"

    try:
        response = requests.get(url=unsp_getphoto_url, headers=headers)
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
    tags = [word for word in slug_parts[:-1] if word not in stopwords]

    photo_info = {
        "url": photo_url,
        "tags": tags,  # tag processing function
        "artist_first_name": first_name,
        "artist_last_name": last_name,
        "caption_text": " ".join(slug_parts[:-1])
    }
    return photo_info

def get_from_likes(n=None):
    endpoint = f"/users/{unsp_username}/likes"
    params = {
        "username" : unsp_username,
    }
    try:
        response = requests.get(url=f"https://api.unsplash.com/{endpoint}", headers=headers, params=params)
        response.raise_for_status()  # Raises an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching photo: {e}")
        return None  # stop here if request fails
    else:
        photo_data = response.json()
        if n is None:
            n = rd.randint(0, len(photo_data) - 1)


        first_name = photo_data[n]["user"]["first_name"]
        last_name = photo_data[n]["user"]["last_name"]
        photo_url = photo_data[n]["urls"]["full"]
        slug_parts = photo_data[n]["slug"].split("-")
        tags = [word for word in slug_parts[:-1] if word not in stopwords]

        photo_info = {
            "url": photo_url,
            "tags": tags,  # tag processing function
            "artist_first_name": first_name,
            "artist_last_name": last_name,
            "caption_text": " ".join(slug_parts[:-1])
        }
        print(photo_info["caption_text"])
        return photo_info





def fetch_and_resize_image(url, target_width):
    response = requests.get(url)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))

    # Resize to target width while keeping aspect ratio
    w_percent = target_width / float(img.width)
    h_size = int(float(img.height) * w_percent)
    img = img.resize((target_width, h_size), Image.LANCZOS)
    return img

def get_random_background_image():
    random_endpoint = "/photos/random"
    query = "sunset, clouds, mountains, night sky, aurora, coffee cup, blossoms"
    params = {
        "query" : query,
        "orientation" : "landscape"
    }
    try:
        response = requests.get(url=f"https://api.unsplash.com/{random_endpoint}", headers=headers, params=params)
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
    tags = [word for word in slug_parts[:-1] if word not in stopwords]

    photo_info = {
        "url": photo_url,
        "tags": tags,
        "artist_first_name": first_name,
        "artist_last_name": last_name,
        "caption_text": " ".join(slug_parts[:-1])
    }
    print(photo_info["caption_text"])
    return photo_info

def get_dadjoke():
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(dadjokes_url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quote: {e}")
        return None  # stop here if request fails
    else:
        return response.json()["joke"]



def combine_quote_and_image():
    bg_url = get_random_background_image()["url"]
    joke = get_dadjoke()

    # Fetch and resize the image to a consistent width
    image = fetch_and_resize_image(bg_url, target_width=1080)

    draw = ImageDraw.Draw(image)

    # Start with a large font size
    font_size = 250
    font = ImageFont.truetype("arial.ttf", size=font_size)

    # Define maximum allowed width (90% of image width)
    max_width = image.width * 0.9

    # Loop to shrink font until text fits
    while True:
        text_bbox = draw.textbbox((0, 0), joke, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        if text_width <= max_width or font_size <= 10:  # stop at 10px minimum
            break
        font_size -= 5
        font = ImageFont.truetype("arial.ttf", size=font_size)

    # Center text
    text_height = text_bbox[3] - text_bbox[1]
    x = (image.width - text_width) / 2
    y = (image.height - text_height) / 2

    draw.text((x, y), joke, font=font, fill="white")
    image.show()
    return image





