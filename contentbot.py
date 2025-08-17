import requests
import os
from pprint import pprint
from dotenv import load_dotenv

load_dotenv()
unsp_access_key = os.getenv("UNSP_ACCESS_KEY")
unsp_key = os.getenv("UNSP_SECRET_KEY")
unsp_app_id = os.getenv("UNSP_APPLICATION_ID")

headers = {
    "Authorization": f"Client-ID {unsp_access_key}"
}


#______________________________________________________Get a photo using ID
def get_photo():
    photo_id = input("What is the ID of the photo you'd like?       ")
    # photo_id = "NuHrMrC5rlk"
    unsp_getphoto_url=f"https://api.unsplash.com/photos/{photo_id}"
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
    print(tags)
    photo_info = {
        "url": photo_url,
        "tags": tags,  # tag processing function
        "artist_first_name": first_name,
        "artist_last_name": last_name,
        "caption_text": " ".join(slug_parts[:-1])
    }
    return photo_info