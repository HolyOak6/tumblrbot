import random
import sys
import pytumblr
import time
from dotenv import load_dotenv
import os
from requests_oauthlib import OAuth1Session
import contentbot as cbot
from pprint import pprint

load_dotenv()

# OAuth URLs given on the application page
request_token_url= "https://www.tumblr.com/oauth/request_token"
authorization_base_url= "https://www.tumblr.com/oauth/authorize"
access_token_url= "https://www.tumblr.com/oauth/access_token"

# # Credentials from the application page
# consumer_key = os.getenv("TUMBLR_CONSUMER_KEY")
# consumer_secret = os.getenv("TUMBLR_CONSUMER_SECRET")
#
# # Step 1: Fetch a request token
# oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)
# fetch_response = oauth.fetch_request_token(request_token_url)
#
# resource_owner_key = fetch_response.get("oauth_token")
# resource_owner_secret = fetch_response.get("oauth_token_secret")
#
# # Step 2: Link user to authorization page
# authorization_url = oauth.authorization_url(authorization_base_url)
# print('Please go here and authorize:', authorization_url)
#
# # Step 3: Get the verifier code from the URL (paste full redirect URL)
# redirect_response = input('Paste the full redirect URL here: ')
#
# # Step 4: Parse the redirect response to get the verifier
# oauth_response = oauth.parse_authorization_response(redirect_response)
# verifier = oauth_response.get("oauth_verifier")
#
# print("Resource Owner Key:", resource_owner_key)
# print("Resource Owner Secret:", resource_owner_secret)
# print("Verifier:", verifier)
#
# # Step 5: Fetch the access token using all above
# oauth = OAuth1Session(
#     consumer_key,
#     client_secret=consumer_secret,
#     resource_owner_key=resource_owner_key,
#     resource_owner_secret=resource_owner_secret,
#     verifier=verifier
# )
#
# access_token_data = oauth.fetch_access_token(access_token_url)
# print("Access Token Data:", access_token_data)
#
# # Step 6: Use the access tokens to make authenticated requests
# oauth = OAuth1Session(
#     consumer_key,
#     client_secret=consumer_secret,
#     resource_owner_key=access_token_data.get("oauth_token"),
#     resource_owner_secret=access_token_data.get("oauth_token_secret")
# )
#
# response = oauth.get('https://api.tumblr.com/v2/user/dashboard')
# print("Response Status:", response.status_code)

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++Get env variables
def get_env_or_exit(var_name):
    value = os.getenv(var_name)
    if not value:
        print(f"No {var_name} found!")
        sys.exit(1)
    return value

consumer_key = get_env_or_exit("TUMBLR_CONSUMER_KEY")
consumer_secret = get_env_or_exit("TUMBLR_CONSUMER_SECRET")
oauth_token = get_env_or_exit("oauth_token")
oauth_token_secret = get_env_or_exit("oauth_token_secret")
my_blog_name = get_env_or_exit("MY_BLOG_NAME")

#__________________________________create client using pytumblr
try:
    client = pytumblr.TumblrRestClient(
        consumer_key,
        consumer_secret,
        oauth_token,
        oauth_token_secret
    )
except Exception as e:
    print(f"Failed to create Tumblr client: {e}")
    sys.exit(1)
try:
    client_info = client.info()  # Example test call
except Exception as e:
    print(f"API call failed: {e}")
    sys.exit(1)



tags_list = [
    "dark_fantasy", "gothic", "dark_love", "dark_passion", "skull_aesthetic", "dark_mind", "gothic_love",
    "dark_beauty", "goth_alternative",

    # Synonyms / aesthetic adjacents
    "romantic_goth", "dark_romanticism",  "ethereal_dark",


    # Fantasy & nerd-culture
    "fantasy_art", "surreal",

    #Artists
    "jonas kunickas", "matt bailey", "sara punt", "viktoria lapteva",
]
#____________________________________________________________Basic tools
def create_text_post(client, blog_name, title, body, tags):
    try:
        response = client.create_text(blog_name, title=title, body=body, tags=tags)

        # Check if we got a successful response
        if isinstance(response, dict) and "id" in response:
            print(f"✅ Post successfully created: ID {response['id']}")
        else:
            print(f"⚠️ Post creation returned unexpected response: {response}")

        return response

    except Exception as e:
        print(f"❌ Failed to create text post on blog '{blog_name}' with title '{title}': {e}")
        return None

def create_photo_post(client, blog_name, photo_url, caption, tags):
    try:
        response = client.create_photo(
            blogname=blog_name,
            state="queue",
            tags=tags,        # use the tags argument
            caption=caption,  # use the caption argument
            source=photo_url  # use the photo_url argument
        )

        print(f"✅ Photo post created: {response}")
        return response
    except Exception as e:
        print(f"❌ Failed to create photo post: {e}")
        return None

def shuffle_queue(client, blog_identifier):
    session = OAuth1Session(
        os.getenv("TUMBLR_CONSUMER_KEY"),
        client_secret=os.getenv("TUMBLR_CONSUMER_SECRET"),
        resource_owner_key=os.getenv("oauth_token"),
        resource_owner_secret=os.getenv("oauth_token_secret")
    )

    url = f"https://api.tumblr.com/v2/blog/{blog_identifier}/posts/queue/shuffle"

    response = session.post(url)

    if response.status_code == 200:
        print("Queue successfully shuffled.")
    else:
        print(f"Failed to shuffle queue. Status code: {response.status_code}")
        print(response.json())

def like_post(client, post_id, reblog_key):
    return client.like(post_id, reblog_key)

def is_reblog_worthy(post):
    caption = post.get('caption', '').lower()
    summary = post.get('summary', '').lower()

    tags = [tag.lower() for tag in post.get('tags', [])]
    blacklisted_words = ["spoilers", "ai art", "ai_art", "price", "ai", "generated", "shitpost", "product", "etsy", "http", "gross", "shitposter", "spoil", "buy", "restored", "collectible", "sale", "discount", "shop", "promo", "link in bio", "store", "trans", "lesbian", "gay", "transgender", "genderfluid", "order now"]

    for word in blacklisted_words:
        if word in caption or word in summary:
            print(f"Rejected because: blacklisted word '{word}'")
            return False

    if len(caption) > 70 or len(summary) > 70:
        print(f"Rejected because: post was too long")
        return False
    print("post accepted")
    return True

def generate_comment():
    comments = [
        "woah", "nice", "🔥",
        "this.", "queued", "kyood",
        "vibe", "save-worthy", "damn", "art", "queued",  "cool", "good stuff",
        "liked", "queueing this", "worth the reblog", "👌", "👍", "🙌", "fire"
    ]
    return random.choice(comments)

def reblog_to_queue(client, blog_name, post_id, reblog_key, comment=None, tags=None):
    if comment is None:
        number = random.randint(0, 6)
        if number == 2:
            comment = generate_comment()
            print(f"added comment: {comment}")
        else:
            comment = ""  # Or just an empty string instead of None

    kwargs = {
        'id': post_id,
        'reblog_key': reblog_key,
        'state': 'queue',
        'tags': tags if tags else "",
        'comment': comment
    }
    return client.reblog(blog_name, **kwargs)


#_________________________________________________Acquiring posts from Tumblr
def grab_liked_posts():
    offset = random.randint(40, 54)
    try:
        response = client.likes(limit=20, offset=offset)
        if not isinstance(response, dict) or 'liked_posts' not in response:
            print("Unexpected response format or no liked_posts key found.")
            return None
        return response['liked_posts']

    except Exception as e:
        print(f"Failed to fetch liked posts: {e}")
        return None

def get_posts_using_single_tag(tag, num):

    session = OAuth1Session(
        os.getenv("TUMBLR_CONSUMER_KEY"),
        client_secret=os.getenv("TUMBLR_CONSUMER_SECRET"),
        resource_owner_key=os.getenv("oauth_token"),
        resource_owner_secret=os.getenv("oauth_token_secret")
    )
    some_timestamp = int(time.time()) - random.randint(0, 60 * 60 * 24 * 30)
    response = session.get(
        "https://api.tumblr.com/v2/tagged",
        params={
            "tag": tag,
            "limit": num,  # Set your desired number here (max is 20)
            "before": some_timestamp
        }
    )
    print(tag)

    return response

def list_joined_communities():
    session = OAuth1Session(
        os.getenv("TUMBLR_CONSUMER_KEY"),
        client_secret=os.getenv("TUMBLR_CONSUMER_SECRET"),
        resource_owner_key=os.getenv("oauth_token"),
        resource_owner_secret=os.getenv("oauth_token_secret")
    )
    response = session.get("https://api.tumblr.com/v2/communities")
    return response.json()


def get_community_posts(community_handle):
    session = OAuth1Session(
        os.getenv("TUMBLR_CONSUMER_KEY"),
        client_secret=os.getenv("TUMBLR_CONSUMER_SECRET"),
        resource_owner_key=os.getenv("oauth_token"),
        resource_owner_secret=os.getenv("oauth_token_secret")
    )

    response = session.get(
        f"https://api.tumblr.com/v2/communities/{community_handle}/timeline",
    )
    return response.json()

def get_posts_using_random_tag_from_list(tags, num):
    tags= tags
    tag = random.choice(tags)

    session = OAuth1Session(
        os.getenv("TUMBLR_CONSUMER_KEY"),
        client_secret=os.getenv("TUMBLR_CONSUMER_SECRET"),
        resource_owner_key=os.getenv("oauth_token"),
        resource_owner_secret=os.getenv("oauth_token_secret")
    )
    # some_timestamp = int(time.time()) - random.randint(0, 60 * 60 * 24 * 30)
    response = session.get(
        "https://api.tumblr.com/v2/tagged",
        params={
            "tag": tag,
            "limit": num,  # Set your desired number here (max is 20)
            # "before": some_timestamp
        }
    )
    print(tag)
    return response


def grab_own_posts(blog_name):
    offset = random.randint(40, 54)
    print(f"Grabbing posts from {blog_name} with offset: {offset}")

    try:
        response = client.posts(blog_name, limit=20, offset=offset)
        if not isinstance(response, dict) or 'posts' not in response:
            print("Unexpected response format or no 'posts' key found.")
            return None
        return response['posts']

    except Exception as e:
        print(f"Failed to fetch posts from {blog_name}: {e}")
        return None


def mass_like(tags, num):
    response = get_posts_using_random_tag_from_list(tags=tags, num=num)
    jsonated_response = response.json()
    posts=jsonated_response['response']

    for post in posts:
        post_info = {
            'id': post['id'],
            'reblog_key': post['reblog_key'],
            'tags': post.get('tags', []),
            'blog_name': post['blog_name'],
            'type': post['type']
        }
        print(post_info['blog_name'])
        if is_reblog_worthy(post):
            like_post(
                client,
                post_info["id"],
                post_info["reblog_key"]
            )
            print("liked")


#_____________________________________________get and reblog_to_queue

def queue_using_tags(tags_list):
    response = get_posts_using_random_tag_from_list(tags_list, 20)
    jsonated_response = response.json()
    posts=jsonated_response['response']

    for post in posts:
        post_info = {
            'id': post['id'],
            'reblog_key': post['reblog_key'],
            'tags': post.get('tags', []),
            'blog_name': post['blog_name'],
            'type': post['type']
        }
        print(post_info)
        if is_reblog_worthy(post):
            reblog_to_queue(
                client,
                blog_name=my_blog_name,
                post_id=post_info['id'],
                reblog_key=post_info['reblog_key'],
                tags=post_info['tags']
            )
    # shuffle_queue(client, my_blog_name)

def queue_using_single_tag(tag, num):
    response = get_posts_using_single_tag(tag, num)
    jsonated_response = response.json()
    posts=jsonated_response['response']

    for post in posts:
        post_info = {
            'id': post['id'],
            'reblog_key': post['reblog_key'],
            'tags': post.get('tags', []),
            'blog_name': post['blog_name'],
            'type': post['type']
        }
        print(post_info)
        if is_reblog_worthy(post):
            reblog_to_queue(
                client,
                blog_name=my_blog_name,
                post_id=post_info['id'],
                reblog_key=post_info['reblog_key'],
                tags=post_info['tags']
            )
    # shuffle_queue(client, my_blog_name)
            like_post(client, post_info['id'], reblog_key=post_info['id'])

def post_to_queue_using_likes():
    posts = grab_liked_posts()

    for post in posts:
        post_info = {
            'id': post['id'],
            'reblog_key': post['reblog_key'],
            'tags': post.get('tags', []),
            'blog_name': post['blog_name'],
            'type': post['type']
        }
        print(post_info)
        if is_reblog_worthy(post):
            reblog_to_queue(
                client,
                blog_name=my_blog_name,
                post_id=post_info['id'],
                reblog_key=post_info['reblog_key'],
                tags=post_info['tags']
            )
    # shuffle_queue(client, my_blog_name)

def post_to_queue_using_own_blog_posts():
    posts = grab_own_posts(my_blog_name)

    for post in posts:
        post_info = {
            'id': post['id'],
            'reblog_key': post['reblog_key'],
            'tags': post.get('tags', []),
            'blog_name': post['blog_name'],
            'type': post['type']
        }
        print(post_info)
        if is_reblog_worthy(post):
            reblog_to_queue(
                client,
                blog_name=my_blog_name,
                post_id=post_info['id'],
                reblog_key=post_info['reblog_key'],
                tags=post_info['tags']
            )
    # shuffle_queue(client, my_blog_name)

def react_to_community_post(community_handle, post_id):
    session = OAuth1Session(
        os.getenv("TUMBLR_CONSUMER_KEY"),
        client_secret=os.getenv("TUMBLR_CONSUMER_SECRET"),
        resource_owner_key=os.getenv("oauth_token"),
        resource_owner_secret=os.getenv("oauth_token_secret")
    )

    body = {
        "slug": ":green_heart:"
    }

    url = f"https://api.tumblr.com/v2/communities/{community_handle}/post/{post_id}/reactions"

    try:
        response = session.put(url, json=body)
        data = response.json()
        if response.status_code in (200, 201):
            print(f"💚 Reacted to post {post_id} in {community_handle}")
            return True
        else:
            print(f"Failed with status {response.status_code}: {data}")
            return False
    except Exception as e:
        print(f"Request failed: {e}")
        return False


def post_from_Unsplash():
    # # Ask the user for the photo ID
    # photo_id = input("What is the ID of the photo you'd like to share to Tumblr? ")

    # Get photo info from your content bot
    photo_info = cbot.get_photo()

    if not photo_info:
        print("❌ Could not retrieve photo info. Aborting post.")
        return

    # Build the caption with artist credit
    caption_text = (
        f"{photo_info['caption_text']} — "
        f"{photo_info['artist_first_name']} {photo_info['artist_last_name']} via Unsplash"
    )
 # Post the photo
    create_photo_post(
        client=client,
        blog_name=my_blog_name,
        photo_url=photo_info['url'],
        caption=caption_text,
        tags=photo_info['tags']
    )
#______________________play
post_from_Unsplash()