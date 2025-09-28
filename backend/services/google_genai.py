from google import genai
from dotenv import load_dotenv
import os
from models.worker import Worker

load_dotenv()

client = genai.Client()
prompt = "Мне нужно убрать мусор на улице пушкина, 16 используя E010BM116"
response = client.models.generate_content(
  model="gemini-2.5-flash",
  contents=prompt,
  config={
      "response_schema": Worker
  }
)

