from dotenv import load_dotenv
import os

load_dotenv()
print("KEY:", os.getenv("GOOGLE_API_KEY"))
