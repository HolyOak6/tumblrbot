import random
import sys
import pytumblr
import time
from dotenv import load_dotenv
import os
from requests_oauthlib import OAuth1Session


load_dotenv()

# OAuth URLs given on the application page
request_token_url= "https://www.tumblr.com/oauth/request_token"
authorization_base_url= "https://www.tumblr.com/oauth/authorize"
access_token_url= "https://www.tumblr.com/oauth/access_token"

"""Initial OATH setup"""

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

#___________________________Default Variables________________________________________________
tags_list = [
    "dark_fantasy", "gothic", "dark_love", "dark_passion", "skull_aesthetic", "dark_mind", "gothic_love",
    "dark_beauty", "goth_alternative",

    # Synonyms / aesthetic adjacents
    "romantic_goth", "dark_romanticism",  "ethereal_dark",

    # Fantasy & nerd-culture
    "fantasy_art", "surreal",

    #Artists
    "jonas kunickas", "matt bailey", "sara punt", "viktoria lapteva", "Glyn Smyth", "edgar allen poe"
]
blacklisted_words = [
        "spoilers", "ai art", "ai_art", "ai-generated", "generated", "ai", "machine learning",
        "shitpost", "shitposter", "meme dump", "nsfw", "explicit", "porn", "sex", "price", "buy", "sale", "discount", "restored", "collectible", "product",
        "etsy", "amazon", "shop", "promo", "link in bio", "store", "order now", "preorder",
        "subscribe", "donate", "patreon", "paypal", "fundraiser", "crowdfunding",
        "gross", "spam", "clickbait", "viral", "giveaway", "contest", "free", "offer", "limited time",
        "trans", "lesbian", "gay", "queer", "transgender", "genderfluid", "nonbinary", "nb",
        "http", "https", "www", ".com", ".net", ".org", "sissy"
    ]


class TumblrBot:
    """A bot for interacting with Tumblr's API."""
    """Initializes the TumblrBot with necessary credentials and sets up the Tumblr client.
    Loads configuration from environment variables and prepares the client for API interactions.
    """
    def __init__(self):
        self.consumer_key = self.get_env_or_exit("TUMBLR_CONSUMER_KEY")
        self.consumer_secret = self.get_env_or_exit("TUMBLR_CONSUMER_SECRET")
        self.oauth_token = self.get_env_or_exit("OAUTH_TOKEN")
        self.oauth_token_secret = self.get_env_or_exit("OAUTH_TOKEN_SECRET")
        self.my_blog_name = self.get_env_or_exit("MY_BLOG_NAME")
        self.secondary_blog = self.get_env_or_exit("SECOND_BLOG")
        self.taglist = tags_list
        self.blacklisted = blacklisted_words

        # Create client
        try:
            self.client = pytumblr.TumblrRestClient(
                self.consumer_key,
                self.consumer_secret,
                self.oauth_token,
                self.oauth_token_secret
            )
        except Exception as e:
            print(f"Failed to create Tumblr client: {e}")
            sys.exit(1)

        # Test call
        try:
            self.client.info()  # simple test to verify credentials
        except Exception as e:
            print(f"Tumblr API call failed: {e}")
            sys.exit(1)

    def get_env_or_exit(self, var_name):
        """Get environment variable or exit if not found."""

        value = os.getenv(var_name)
        if not value:
            print(f"No {var_name} found!")
            sys.exit(1)
        return value

    def queue_photo_post(self, blog_name, tags, filepath):
        """Queue a photo post on a specified Tumblr blog.
        Parameters:
            blog_name (str): The name of the blog where the post will be published.
            tags (list of str): A list of tags to attach to the post.
            filepath (str): The local file path to the photo to be uploaded.
        Returns:
            dict: The API response if the post was successfully created.
            """

        blog_name = blog_name or self.secondary_blog
        return self.client.create_photo(
            blogname=blog_name,
            state="queue",
            tags=tags,
            data=filepath
        )

    def create_text_post(self, title, body, tags, blog_name=None):
        """
        Create a text post on a Tumblr blog.

        Parameters:
            title (str): The title of the text post.
            body (str): The main content of the post.
            tags (list of str): A list of tags to attach to the post.
            blog_name (str, optional): The name of the blog where the post will be published.
                Defaults to self.my_blog_name.

        Returns:
            dict or None: The API response if the post was successfully created,
            None if an error occurred.
        """
        blog_name = blog_name or self.my_blog_name

        try:
            response = self.client.create_text(blog_name, title=title, body=body, tags=tags)

            if isinstance(response, dict) and "id" in response:
                print(f"✅ Post successfully created: ID {response['id']}")
            else:
                print(f"⚠️ Post creation returned unexpected response: {response}")

            return response

        except Exception as e:
            print(f"❌ Failed to create text post on blog '{blog_name}' with title '{title}': {e}")
            return None

    def create_photo_post(self, photo_url, caption, tags, blog_name=None):
        """
            Create a photo post on a specified Tumblr blog.

            Parameters:
                self.
                blog_name (str): The name of the blog where the post will be published.
                photo_url (str): url of the image.
                caption (str): caption.
                tags (list of str): A list of tags to attach to the post.

            Returns:
                dict or None: The API response if the post was successfully created,
                None if an error occurred.
            """
        blog_name = blog_name or self.my_blog_name
        try:
            response = self.client.create_photo(
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

    def shuffle_queue(self, blog_name=None):
        """
            Shuffle blog's queue.

            client: Tumblr API client instance used to make the request.
            blog_identifier (str): The name of the blog where the post will be published.
            return successful or not.
        """
        blog_name = blog_name or self.my_blog_name
        session = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret
        )

        url = f"https://api.tumblr.com/v2/blog/{blog_name}/posts/queue/shuffle"

        response = session.post(url)

        if response.status_code == 200:
            print("Queue successfully shuffled.")
        else:
            print(f"Failed to shuffle queue. Status code: {response.status_code}")
            print(response.json())

    def like_post(self, post_id, reblog_key):
        """
            likes post

            Parameters:
                post_id: id of the posted wanting to like.
                reblog_key: key used to reblog or like desired post.

            Returns:
                dict: The API response if the like was successful.
        """
        return self.client.like(post_id, reblog_key)

    def is_reblog_worthy(self, post):
        """
            Determine whether a Tumblr post is suitable for reblogging.

            Checks:
            - Post caption and summary for blacklisted words.
            - Post length (caption or summary should not exceed 70 characters).

            Args:
                post (dict): A dictionary representing a Tumblr post, expected to have
                             'caption', 'summary', and 'tags' keys.

            Returns:
                bool: True if the post passes all checks and is reblog-worthy, False otherwise.
            """
        caption = post.get('caption', '').lower()
        summary = post.get('summary', '').lower()

        tags = [tag.lower() for tag in post.get('tags', [])]

        for word in self.blacklisted:
            if word in caption or word in summary:
                print(f"Rejected because: blacklisted word '{word}'")
                return False

        if len(caption) > 70 or len(summary) > 70:
            print(f"Rejected because: post was too long")
            return False
        print("post accepted")
        return True



    def reblog_to_queue(self, post_id, reblog_key, tags=None, blog_name=None):
        """Reblogs a post to the queue of a specified blog.
        Parameters:
            post_id (int): The ID of the post to be reblogged.
            reblog_key (str): The reblog key of the post to be reblogged.
            tags (list of str, optional): A list of tags to attach to the reblogged post.
            blog_name (str, optional): The name of the blog where the post will be reblogged.
                Defaults to self.my_blog_name.
        Returns:
            dict: The API response if the reblog was successful.

            """

        blog_name = blog_name or self.my_blog_name

        kwargs = {
            'id': post_id,
            'reblog_key': reblog_key,
            'state': 'queue',
            'tags': tags if tags else "",
        }
        return self.client.reblog(blog_name, **kwargs)


    #_________________________________________________Acquiring posts from Tumblr
    def grab_liked_posts(self):

        """Grab liked posts.
         Grabs 20 posts, random offset between 2 and 54 to avoid always getting the same posts.
        Returns:
            list: A list of liked posts or NONE if an error occurs.


        """
        offset = random.randint(2, 54)
        try:
            response = self.client.likes(limit=20, offset=offset)
            if not isinstance(response, dict) or 'liked_posts' not in response:
                print("Unexpected response format or no liked_posts key found.")
                return None
            return response['liked_posts']

        except Exception as e:
            print(f"Failed to fetch liked posts: {e}")
            return None

    def get_posts_using_single_tag(self, tag, num):

        """Grab posts using a single tag.
        Parameters:
            tag (str): The tag to search for.
            num (int): The number of posts to retrieve (max 20).
        Returns:
            Response object: The API response containing the posts.
        """

        session = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret
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


    def get_posts_using_random_tag_from_list(self, tags, num):
        """Grab posts using a random tag from a provided list.
        Parameters:
            tags (list of str): A list of tags to choose from.
            num (int): The number of posts to retrieve (max 20).
        Returns:
            Response object: The API response containing the posts.
            """

        tags= tags
        tag = random.choice(tags)

        session = OAuth1Session(
            self.consumer_key,
            client_secret=self.consumer_secret,
            resource_owner_key=self.oauth_token,
            resource_owner_secret=self.oauth_token_secret
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


    def grab_own_posts(self, blog_name=None):
        """Grab own posts from specified blog.
        Parameters:
            blog_name (str, optional): The name of the blog to fetch posts from.
                Defaults to self.my_blog_name.
        Returns:
            list: A list of own posts or NONE if an error occurs.
        """
        blog_name = blog_name or self.my_blog_name
        offset = random.randint(40, 54)
        print(f"Grabbing posts from {blog_name} with offset: {offset}")

        try:
            response = self.client.posts(blog_name, limit=20, offset=offset)
            if not isinstance(response, dict) or 'posts' not in response:
                print("Unexpected response format or no 'posts' key found.")
                return None
            return response['posts']

        except Exception as e:
            print(f"Failed to fetch posts from {blog_name}: {e}")
            return None


    def mass_like(self, tags, num):
        """Grab posts using a random tag from a list and like them.
        Parameters:
            tags (list of str): A list of tags to choose from.
            num (int): The number of posts to retrieve (max 20).
            """

        response = self.get_posts_using_random_tag_from_list(tags=tags, num=num)
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
            if self.is_reblog_worthy(post):
                self.like_post(
                    post_info["id"],
                    post_info["reblog_key"]
                )
                print("liked")


    ###__________________________________________Community stuff
    # def list_joined_communities():
    #     """Community api is not efficient, and many community items do not function"""
    #
    #     session = OAuth1Session(
    #         os.getenv("TUMBLR_CONSUMER_KEY"),
    #         client_secret=os.getenv("TUMBLR_CONSUMER_SECRET"),
    #         resource_owner_key=os.getenv("oauth_token"),
    #         resource_owner_secret=os.getenv("oauth_token_secret")
    #     )
    #     response = session.get("https://api.tumblr.com/v2/communities")
    #     return response.json()
    #
    #
    # def get_community_posts(community_handle):
    #     session = OAuth1Session(
    #         os.getenv("TUMBLR_CONSUMER_KEY"),
    #         client_secret=os.getenv("TUMBLR_CONSUMER_SECRET"),
    #         resource_owner_key=os.getenv("oauth_token"),
    #         resource_owner_secret=os.getenv("oauth_token_secret")
    #     )
    #
    #     response = session.get(
    #         f"https://api.tumblr.com/v2/communities/{community_handle}/timeline",
    #     )
    #     return response.json()
    #
    # def react_to_community_post(community_handle, post_id):
    #     session = OAuth1Session(
    #         os.getenv("TUMBLR_CONSUMER_KEY"),
    #         client_secret=os.getenv("TUMBLR_CONSUMER_SECRET"),
    #         resource_owner_key=os.getenv("oauth_token"),
    #         resource_owner_secret=os.getenv("oauth_token_secret")
    #     )
    #
    #     body = {
    #         "slug": ":green_heart:"
    #     }
    #
    #     url = f"https://api.tumblr.com/v2/communities/{community_handle}/post/{post_id}/reactions"
    #
    #     try:
    #         response = session.put(url, json=body)
    #         data = response.json()
    #         if response.status_code in (200, 201):
    #             print(f"💚 Reacted to post {post_id} in {community_handle}")
    #             return True
    #         else:
    #             print(f"Failed with status {response.status_code}: {data}")
    #             return False
    #     except Exception as e:
    #         print(f"Request failed: {e}")
    #         return False

    #_____________________________________________get and reblog_to_queue

    def queue_using_tags(self, tags_list, blogtoqueueto):
        """Grab posts using a random tag from a list and reblog to queue.
        Parameters:
            tags_list (list of str): A list of tags to choose from.
            blogtoqueueto (str): The name of the blog where the post will be reblogged.
        """
        blog_name = blogtoqueueto or self.secondary_blog
        response = self.get_posts_using_random_tag_from_list(tags_list, 20)
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
            if self.is_reblog_worthy(post):
                self.reblog_to_queue(
                    blog_name=blog_name,
                    post_id=post_info['id'],
                    reblog_key=post_info['reblog_key'],
                    tags=post_info['tags']
                )
        # shuffle_queue(client, my_blog_name)

    def queue_using_single_tag(self, tag, num, blog_name=None):
        """Grab posts using a single tag and reblog to queue.
        Parameters:
            tag (str): The tag to search for.
            num (int): The number of posts to retrieve (max 20).
            blog_name (str, optional): The name of the blog where the post will be reblogged.
                Defaults to self.my_blog_name.
            """
        blog_name = blog_name or self.my_blog_name
        response = self.get_posts_using_single_tag(tag, num)
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
            if self.is_reblog_worthy(post):
                self.reblog_to_queue(
                    blog_name=blog_name,
                    post_id=post_info['id'],
                    reblog_key=post_info['reblog_key'],
                    tags=post_info['tags']
                )
        # shuffle_queue(client, my_blog_name)
                self.like_post( post_info['id'], reblog_key=post_info['id'])

    def post_to_queue_using_likes(self, blog_name=None):
        """Grab liked posts and reblog to queue.
        Parameters:
            blog_name (str): The name of the blog where the post will be reblogged.
            defaults to self.blogname if none provided.
        """
        posts = self.grab_liked_posts()
        blog_name = blog_name or self.secondary_blog
        for post in posts:
            post_info = {
                'id': post['id'],
                'reblog_key': post['reblog_key'],
                'tags': post.get('tags', []),
                'blog_name': post['blog_name'],
                'type': post['type']
            }
            print(post_info)
            if self.is_reblog_worthy(post):
                self.reblog_to_queue(
                    blog_name=blog_name,
                    post_id=post_info['id'],
                    reblog_key=post_info['reblog_key'],
                    tags=post_info['tags']
                )
        # shuffle_queue(client, my_blog_name)

    def post_to_queue_using_own_blog_posts(self, blog_name=None):
        """Grab own posts and reblog to queue.
        Parameters:
            blog_name (str): The name of the blog where the post will be reblogged.
            defaults to self.blogname if none provided.
            """
        blog_name = blog_name or self.my_blog_name
        posts = self.grab_own_posts(blog_name)

        for post in posts:
            post_info = {
                'id': post['id'],
                'reblog_key': post['reblog_key'],
                'tags': post.get('tags', []),
                'blog_name': post['blog_name'],
                'type': post['type']
            }
            print(post_info)
            if self.is_reblog_worthy(post):
                self.reblog_to_queue(
                    blog_name=blog_name,
                    post_id=post_info['id'],
                    reblog_key=post_info['reblog_key'],
                    tags=post_info['tags']
                )
        # shuffle_queue(client, my_blog_name)




    def megashuffle(self, blog_name=None):
        """Shuffle the queue multiple times to ensure randomness."""
        blog_name = blog_name or self.my_blog_name
        for num in range(0,15):
            self.shuffle_queue(blog_name)

