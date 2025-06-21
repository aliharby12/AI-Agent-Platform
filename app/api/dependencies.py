from app.utils.database import get_db
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Dependency to get a database session
get_db_session = get_db

# Dependency to get an OpenAI client
async def get_openai_client():
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    try:
        yield client
    finally:
        await client.close()