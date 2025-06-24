import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


class AiService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")

    def llm(self):
        model = ChatGoogleGenerativeAI(
            google_api_key=self.api_key,
            model="gemini-2.0-flash",
            temperature=0.5,
        )
        return model


if __name__ == "__main__":
    ai_service = AiService()
    llm = ai_service.llm()
    print(llm.invoke("Hello, how are you?"))
