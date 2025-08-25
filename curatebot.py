import os
import tempfile

import tumblrbot as tbot
import contentbot as cbot
import geminibotter as gbot
from PIL import ImageDraw, ImageFont


class CurateBot:
    def __init__(self, tumblr_client, gemini_client, content_client):
        self.tbot = tumblr_client
        self.cbot = content_client
        self.gbot = gemini_client
        self.blog_name = os.getenv("MY_BLOG_NAME")
        self.secondaryblog = os.getenv("SECOND_BLOG")


    def queue_from_unsplash(self, blog_name=None):

        ""    """
        Retrieves a photo from the bot's liked Unsplash images and posts it to Tumblr.
    
        The function fetches a random liked photo from Unsplash using the content bot,
        builds a caption including the artist's name, and then creates a photo post
        on the configured Tumblr blog with relevant tags.
    
        Returns:
            None
        """
        # # Ask the user for the photo ID
        # photo_id = input("What is the ID of the photo you'd like to share to Tumblr? ")
        blog_name = blog_name or self.blog_name
        # Get photo info from your content bot
        photo_info = self.cbot.get_from_likes()

        if not photo_info:
            print("❌ Could not retrieve photo info. Aborting post.")
            return

        # Build the caption with artist credit
        caption_text = (
            f"{photo_info['caption_text']} \n— "
            f"{photo_info['artist_first_name']} {photo_info['artist_last_name']}"
        )
    # Post the photo
        self.tbot.create_photo_post(
            blog_name=blog_name,
            photo_url=photo_info['url'],
            caption=caption_text,
            tags=photo_info['tags']
        )

    def queue_multiple_unsplash(self, blog_name=None):
        """Queues multiple photos from liked Unsplash images to Tumblr."""
        blog_name = blog_name or self.blog_name
        for num in range(5, 10):
            photo_info = self.cbot.get_from_likes(num)

            if not photo_info:
                print("❌ Could not retrieve photo info. Aborting post.")
                return

            # Build the caption with artist credit
            caption_text = (
                f"{photo_info['caption_text']} \n— "
                f"{photo_info['artist_first_name']} {photo_info['artist_last_name']}"
            )
            # Post the photo
            self.tbot.create_photo_post(

                blog_name=blog_name,
                photo_url=photo_info['url'],
                caption=caption_text,
                tags=photo_info['tags']
            )

    def queue_dad_joke(self, blog_name=None):
        """
        Generates a dad joke image and queues it as a photo post on Tumblr.
        """
        blog_name = blog_name or self.blog_name

        # Generate image from content bot
        image = self.combine_quote_and_image_Unsplash()  # <-- assume this is in your content bot

        postit = "y"  # for now, hardcoded
        if postit == "y":
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_filename = tmp.name
                image.save(temp_filename, format="PNG")

            try:
                # Delegate posting to TumblrBot
                response = self.tbot.queue_photo_post(
                    blog_name=blog_name,
                    tags=["dadjoke", "funny", "lol"],
                    filepath=temp_filename
                )
                print(f"✅ Photo post created: {response}")
            except Exception as e:
                print(f"❌ Failed to create photo post: {e}")
            finally:
                try:
                    os.remove(temp_filename)
                except Exception as e:
                    print(f"⚠️ Failed to delete temp file: {e}")

    def queue_famous_quote(self, blog_name=None):
        blog_name = blog_name or self.blog_name

        # Let the content bot do the content generation
        image = self.combine_quote_and_image_quote()  # returns a PIL.Image

        postit = "y"  # or ask user
        if postit == "y":
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_filename = tmp.name
                image.save(temp_filename, format="PNG")

            try:
                # Tumblr bot handles posting
                response = self.tbot.queue_photo_post(
                    blog_name=blog_name,
                    tags=["quote", "inspiration", "motivation"],
                    filepath=temp_filename
                )
                print(f"✅ Photo post created: {response}")
            except Exception as e:
                print(f"❌ Failed to create photo post: {e}")
            finally:
                try:
                    os.remove(temp_filename)
                except Exception as e:
                    print(f"⚠️ Failed to delete temp file: {e}")


    def queue_fact(self, blog_name=None):
        """
           Generates a fact image and queues it as a photo post on Tumblr.

           The function uses the content bot to combine a dad joke with a background image,
           prompts the user to confirm posting, saves the image temporarily, and then creates
           a queued photo post on the configured Tumblr blog with predefined tags. The temporary
           file is deleted afterward.

           Returns:
               None
           """
        blog_name = blog_name or self.blog_name
        image = self.fact_over_image()  # PIL.Image
        # postit = input("Whould you like to post it? y or n?  ").lower()
        postit = "y"
        if postit == "y":
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_filename = tmp.name
                image.save(temp_filename, format="PNG")

            try:
                response = self.tbot.client.create_photo(
                    blogname=self.secondaryblog,
                    state="queue",
                    tags=["fact", "trivia", "crazy", "woah"],
                    data=temp_filename
                )
                print(f"✅ Photo post created: {response}")
            except Exception as e:
                print(f"❌ Failed to create photo post: {e}")
            finally:
                try:
                    os.remove(temp_filename)
                except Exception as e:
                    print(f"⚠️ Failed to delete temp file: {e}")


    def ai_captioned_like_from_unsplash(self, blog_name=None):
        """Pulls random image from liked photos from Unsplash profile
        Feeds that image to Gemini asking for tags that fit the imagery
        uses those tags to post image to Tumblr Queue"""
        blog_name = blog_name or self.blog_name
        response = self.cbot.get_from_likes()
        url=response["url"]
        caption=response["caption_text"] + "--" + response["artist_first_name"] + " " + response["artist_last_name"]
        # print(url)
        tags = self.gbot.get_tags(url)

        print(tags)
        # print(tags)
        self.tbot.create_photo_post(blog_name, url, caption, tags)

    def combine_quote_and_image_Unsplash(self, blog_name=None):
        """Uses Pillow to combine random image from Unsplash and dad joke into a single meme.
        Returns image as a PIL.Image object."""

        # Try your main query first, fallback to default if None
        bg_data = self.cbot.get_background_image(query=["laughing, laugh, sky, clouds, party, fun, sunset, stars"])
        if bg_data is None:
            bg_data = self.cbot.get_background_image(query=["sunsets"])
        if bg_data is None:
            raise ValueError("No background image available.")

        bg_url = bg_data["url"]
        joke = self.cbot.get_dadjoke()
        wrapped_joke = self.cbot.wrap_text(joke, max_chars=45)  # wrap into multiple lines

        # Fetch and resize the image
        image = self.cbot.fetch_and_resize_image(bg_url, target_width=1080)
        draw = ImageDraw.Draw(image)

        # Start with a large font size
        font_size = 250
        font = ImageFont.truetype("arial.ttf", size=font_size)

        # Maximum allowed dimensions
        max_width = image.width * 0.9
        max_height = image.height * 0.9

        # Shrink font until wrapped text fits in both width and height
        while True:
            text_bbox = draw.multiline_textbbox((0, 0), wrapped_joke, font=font, spacing=10)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            if (text_width <= max_width and text_height <= max_height) or font_size <= 10:
                break
            font_size -= 5
            font = ImageFont.truetype("arial.ttf", size=font_size)

        # Center text
        x = (image.width - text_width) / 2
        y = (image.height - text_height) / 2

        # Draw text with stroke, respecting line breaks
        draw.multiline_text(
            (x, y),
            wrapped_joke,
            font=font,
            fill="white",
            stroke_width=3,
            stroke_fill="black",
            spacing=10,
            align="center"
        )

        return image

    def combine_quote_and_image_quote(self, blog_name=None):
        """Uses Pillow to combine a random image from Unsplash and a quote into a single meme.
        Returns image as a PIL.Image object."""
        blog_name = blog_name or self.blog_name
        bg_url = self.cbot.get_background_image()["url"]
        quote = self.cbot.get_random_quotes(1)

        # Wrap the quote so it doesn’t run off screen
        wrapped_quote = self.cbot.wrap_text(quote, max_chars=45)

        # Fetch and resize the image
        image = self.cbot.fetch_and_resize_image(bg_url, target_width=1080)
        draw = ImageDraw.Draw(image)

        # Start with a large font size
        font_size = 250
        font = ImageFont.truetype("arial.ttf", size=font_size)

        # Set max box for both width and height
        max_width = image.width * 0.9
        max_height = image.height * 0.9

        # Shrink font until wrapped text fits inside image bounds
        while True:
            text_bbox = draw.multiline_textbbox((0, 0), wrapped_quote, font=font, spacing=10)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            if (text_width <= max_width and text_height <= max_height) or font_size <= 10:
                break

            font_size -= 5
            font = ImageFont.truetype("arial.ttf", size=font_size)

        # Center the wrapped text
        x = (image.width - text_width) / 2
        y = (image.height - text_height) / 2

        # Draw with stroke for readability
        draw.multiline_text(
            (x, y),
            wrapped_quote,
            font=font,
            fill="white",
            stroke_width=3,
            stroke_fill="black",
            spacing=10,
            align="center"
        )

        return image

    def fact_over_image(self, blog_name=None):
        """Uses Pillow to combine random image from Unsplash and fact into a single meme.
        Returns image as a PIL.Image object."""
        blog_name=blog_name or self.blog_name
        fact=self.cbot.get_fact()

        bg_url = self.cbot.get_background_image()["url"]

        # Wrap the quote so it doesn’t run off screen
        wrapped_fact = self.cbot.wrap_text(fact, max_chars=45)

        # Fetch and resize the image
        image = self.cbot.fetch_and_resize_image(bg_url, target_width=1080)
        draw = ImageDraw.Draw(image)

        # Start with a large font size
        font_size = 250
        font = ImageFont.truetype("arial.ttf", size=font_size)

        # Set max box for both width and height
        max_width = image.width * 0.9
        max_height = image.height * 0.9

        # Shrink font until wrapped text fits inside image bounds
        while True:
            text_bbox = draw.multiline_textbbox((0, 0), wrapped_fact, font=font, spacing=10)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            if (text_width <= max_width and text_height <= max_height) or font_size <= 10:
                break

            font_size -= 5
            font = ImageFont.truetype("arial.ttf", size=font_size)

        # Center the wrapped text
        x = (image.width - text_width) / 2
        y = (image.height - text_height) / 2

        # Draw with stroke for readability
        draw.multiline_text(
            (x, y),
            wrapped_fact,
            font=font,
            fill="white",
            stroke_width=3,
            stroke_fill="black",
            spacing=10,
            align="center"
        )

        return image
    def curate_dad_joke_ai(self):
        """
        Uses Gemini to generate tags for a dad joke, then uses those tags to find a relevant
        background image from Unsplash. Combines the joke and image into a meme-style image
        using Pillow, and returns the image and tags.
        """


        # Generate image from content bot
        joke = self.cbot.get_dadjoke()
        tags = self.gbot.get_tags(joke, content_type="text")
        bg_url = self.cbot.get_background_image(query=tags)["url"]
        wrapped_joke = self.cbot.wrap_text(joke, max_chars=45)# wrap into multiple lines

        # Resize image
        image = self.cbot.fetch_and_resize_image(bg_url, target_width=1080)
        draw = ImageDraw.Draw(image)

        # Start with a large font size
        font_size = 250
        font = ImageFont.truetype("arial.ttf", size=font_size)

        # Set max box for both width and height
        max_width = image.width * 0.9
        max_height = image.height * 0.9

        # Shrink font until wrapped text fits inside image bounds
        while True:
            text_bbox = draw.multiline_textbbox((0, 0), wrapped_joke, font=font, spacing=10)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            if (text_width <= max_width and text_height <= max_height) or font_size <= 10:
                break

            font_size -= 5
            font = ImageFont.truetype("arial.ttf", size=font_size)

        # Center the wrapped text
        x = (image.width - text_width) / 2
        y = (image.height - text_height) / 2

        # Draw with stroke for readability
        draw.multiline_text(
            (x, y),
            wrapped_joke,
            font=font,
            fill="white",
            stroke_width=3,
            stroke_fill="black",
            spacing=10,
            align="center"
        )
        print(image, tags)
        return image, tags

    def curate_fact_ai(self):
        """ Uses Gemini to generate tags for a fact, then uses those tags to find a relevant
        background image from Unsplash. Combines the fact and image into a meme-style image
        using Pillow, and returns the image and tags."""

        fact = self.cbot.get_fact()
        tags = self.gbot.get_tags(fact, content_type="text")
        bg_url = self.cbot.get_background_image(query=tags)["url"]
        wrappedfact = self.cbot.wrap_text(fact)
        print(tags)
        print(fact)
        print(wrappedfact)

        #Resize image
        image = self.cbot.fetch_and_resize_image(bg_url, target_width=1080)
        draw = ImageDraw.Draw(image)

        # Start with a large font size
        font_size = 250
        font = ImageFont.truetype("arial.ttf", size=font_size)

        # Set max box for both width and height
        max_width = image.width * 0.9
        max_height = image.height * 0.9

        # Shrink font until wrapped text fits inside image bounds
        while True:
            text_bbox = draw.multiline_textbbox((0, 0), wrappedfact, font=font, spacing=10)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            if (text_width <= max_width and text_height <= max_height) or font_size <= 10:
                break

            font_size -= 5
            font = ImageFont.truetype("arial.ttf", size=font_size)

        # Center the wrapped text
        x = (image.width - text_width) / 2
        y = (image.height - text_height) / 2

        # Draw with stroke for readability
        draw.multiline_text(
            (x, y),
            wrappedfact,
            font=font,
            fill="white",
            stroke_width=3,
            stroke_fill="black",
            spacing=10,
            align="center"
        )
        print(image, tags)
        return image, tags

    def queue_curated_ai(self, blog_name=None, image=None, tags=None):
        """ Uses self attributes to post curated AI content to Tumblr queue.
        Takes optional image and tags parameters, if not provided,
        it will generate them using curate_fact_ai method.
        """
        blog_name = blog_name or self.blog_name
        if not image and not tags:
            image, tags = self.curate_fact_ai()  # PIL.Image

        # postit = input("Whould you like to post it? y or n?  ").lower()
        postit = "y"
        if postit == "y":
            # Create a temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                temp_filename = tmp.name
                image.save(temp_filename, format="PNG")

            try:
                response = self.tbot.client.create_photo(
                    blogname=self.secondaryblog,
                    state="queue",
                    tags=tags,
                    data=temp_filename
                )
                print(f"✅ Photo post created: {response}")
            except Exception as e:
                print(f"❌ Failed to create photo post: {e}")
            finally:
                try:
                    os.remove(temp_filename)
                except Exception as e:
                    print(f"⚠️ Failed to delete temp file: {e}")


    #_____________________________Testing

cbotclient = cbot.ContentBot()
tbotclient = tbot.TumblrBot()
gbotclient = gbot.Geminibot()
bot=CurateBot(tbotclient, gbotclient, cbotclient)



for i in range (6):

    img, tgs = bot.curate_fact_ai()
    bot.queue_curated_ai(image=img, tags=tgs)
    images, tags = bot.curate_dad_joke_ai()
    bot.queue_curated_ai(image=images, tags=tags)
    bot.queue_from_unsplash(blog_name=os.getenv("MY_BLOG_NAME"))
    tbotclient.megashuffle(blog_name=os.getenv("MY_BLOG_NAME"))
    tbotclient.megashuffle(blog_name=os.getenv("SECOND_BLOG"))

# images, tags = bot.curate_dad_joke_ai()
# bot.queue_curated_ai(image=images, tags=tags)