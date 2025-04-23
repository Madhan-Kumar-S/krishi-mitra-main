from pydantic import BaseModel
import logging
from llm_setup.llm_setup import LLMService
import configs.config as config
import scraper
import processing.documents as document_processing
from stores.chroma import store_embeddings
import speech_to_text.gemini as gemini
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
import os

# Debugging: Print the GOOGLE_APPLICATION_CREDENTIALS environment variable
#print("GOOGLE_APPLICATION_CREDENTIALS:", os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Set environment variables
config.set_envs()

# Start web scraping if configured
# if config.START_WEB_SCRAPING_MYSCHEMES:
#     scraper.scrape_and_store_to_json_file()

# Load documents and store embeddings
json_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "myschemes_scraped.json")
documents = document_processing.load_json_to_langchain_document_schema(json_file_path)
chroma = store_embeddings(documents, config.EMBEDDINGS)
retriever = chroma.as_retriever()

# Define the Language data model
class Language(BaseModel):
    text: str
    language: str
    language_code: str

# Initialize the LLMService
llm_svc = LLMService(logger, "", retriever)
if llm_svc.error:
    logger.error(f"Error initializing LLM service: {llm_svc.error}")

llm = llm_svc.get_llm()

# Set up the JSON output parser and prompt template
parser = JsonOutputParser(pydantic_object=Language)
prompt_template = PromptTemplate(
    template="Answer the user query.\n{format_instructions}\n{query}\n",
    input_variables=["query"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

json_chain = prompt_template | llm | parser

# Terminal-based workflow
def main():
    try:
        print("Welcome to KrishiMitra!")
        print("Choose an option:")
        print("1. Enter text input")
        print("2. Upload an audio file")
        choice = input("Enter your choice (1 or 2): ")

        if choice == "1":
            text = input("Enter your query: ")
            llm_response = json_chain.invoke({
                "query": f"""
                User Input: {text}
                Provide a JSON response with the following keys:
                * language: The language of the input text.
                * text: A proper English translation understandable by a native English speaker.
                * language_code: The equivalent Google Cloud Platform language code for text-to-speech.
                """
            })
            response_dict = llm_response
        elif choice == "2":
            file_path = input("Enter the path to the audio file: ")
            gemini_resp = gemini.speech_to_text(file_path)
            response_dict = json_chain.invoke({"query": gemini_resp})
        else:
            print("Invalid choice. Exiting.")
            return

        user_language = response_dict['language']
        user_input = response_dict['text']
        user_language_code = response_dict["language_code"]

        docs = chroma.similarity_search(user_input)
        context = " ".join(doc.page_content for doc in docs[:4])

        if not context:
            print("I don't have an answer to this question.")
            return

        prompt = f"""
        You are a highly knowledgeable assistant specializing in Indian government schemes. 
        Your task is to provide clear, accurate, and actionable information to users about various government programs 
        related to areas like education, healthcare, agriculture, and insurance. 
        Your responses should be grounded in the provided context and include details about the scheme name, specific benefits, and eligibility criteria. 
        Ensure the information is delivered in a straightforward, conversational manner without using markdown formatting.
        Example Query: {user_input}
        Context: {context}
        Answer in {user_language}. Language code: {user_language_code}.
        """

        response = llm.invoke(prompt)
        
        print("\nResponse:")
        print(response.content)
        print("\nNote: Text-to-speech functionality is currently disabled.")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print("An internal error occurred.")

if __name__ == "__main__":
    main()
