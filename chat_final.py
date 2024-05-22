import google.generativeai as genai
from google.generativeai import GenerationConfig,GenerativeModel
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")


async def outputfn(question, data, language):
    try:
        main_data = pd.DataFrame(data)
        prompt = f"""
        Description:
        The Inventory Management System is designed to track various aspects of inventory data including product details, pricing, quantities, user assignments, and more. Below is the dataframe of a dummy data for the inventory table:

        Data: {main_data} where, \n 
        Name : Name of the product,
        Brand: Brand of the product,
        Quantity: Quantity as in number of items in the product,
        Threshold: Threshold of stock with respect to the product,
        Category: Category of the product,
        Net Weight: Net Weight of an individual product.
        Price: Price of individual product\n
        Answer to this query: {question} by going through the entire system in 1 sentence and don't generate anything else. Your response should be translated into this language: {language} without translating the values of the data.
        """
        generated_config = GenerationConfig(temperature=0.1)
        response = model.generate_content(prompt,generation_config=generated_config)
        generated_text = response.text
        print(generated_text)
        return generated_text
    except Exception as e:
        print(e)
        return str(e)
    
