import json
import os
import requests
from google import genai
from google.genai import types


gemini_key = os.getenv("GEMINI_API_KEY")

class Geminibot:
    def __init__(self):
        self.api = gemini_key

    def get_tags(self, content, content_type="image"):
        client = genai.Client()
        if content_type == "image":
            # Convert URL to image bytes
            image_bytes = requests.get(content).content
            content_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
            prompt = "Return only a JSON array of tags for this image. Do not include explanations."
            contents = [prompt, content_part]
        else:  # text type
            prompt = f"Return only a JSON array of tags for this text: {content}"
            contents = [prompt]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )

        try:
            if response.text is not None:
                tags = json.loads(response.text)
            else:
                tags = []
        except json.JSONDecodeError:
            start = response.text.find("[")
            end = response.text.rfind("]") + 1
            try:
                tags = json.loads(response.text[start:end])
            except:
                tags = []

