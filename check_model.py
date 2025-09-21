# to check the model of gemini 
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load API key from .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env")
    exit()

genai.configure(api_key=api_key)

print("✅ Available models for your API key:")
for m in genai.list_models():
    print("-", m.name)
