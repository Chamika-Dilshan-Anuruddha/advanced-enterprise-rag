from app.config import settings

print(settings.GROQ_API_KEY.get_secret_value())