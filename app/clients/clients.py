import openai
import os

OPENAI_CLIENT = openai.OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
)