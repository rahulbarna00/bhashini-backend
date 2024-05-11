import vanna as vn
from dotenv import load_dotenv
import os
from vanna.remote import VannaDefault
from IPython.display import Markdown
import google.generativeai as genai
from google.generativeai import GenerationConfig,GenerativeModel
import pandas as pd
from io import StringIO

api_key = "8369b9bcaa5b41db8ee8e3c3e7ac9723"
supa_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzaXFydHF3a2NkcmpzeGdnZ21uIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTM5ODE2MDksImV4cCI6MjAyOTU1NzYwOX0.HZGtXA5JHfcrvJ8puzfeStHD4utk7F37R8JJyElpt5o"
url = "https://asiqrtqwkcdrjsxgggmn.supabase.co"
host =  "aws-0-ap-south-1.pooler.supabase.com"
name = "postgres"
port = 5432
user = "postgres.asiqrtqwkcdrjsxgggmn"
password = "@ipragati1969"
gemini_api = 'AIzaSyBd8WwvM1WpcN6ibodXo1zgjJLRKhYgXG0'
genai.configure(api_key=gemini_api)
model = genai.GenerativeModel("gemini-pro")

vanna_model_name = "hisaaab"
vn = VannaDefault(model=vanna_model_name, api_key=api_key)

vn.connect_to_postgres(host=host,dbname=name,user=user,password=password,port=port)
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
print(df_information_schema)
df_inventory = df_information_schema[(df_information_schema['table_schema'] == 'public') & (df_information_schema['table_name'] == 'inventory')]
print(df_inventory)
plan = vn.get_training_plan_generic(df_inventory)
print("success")
vn.train(documentation= "The main aim of the system is to keep a track of the inventory systemically and generate visualizations according to the prompt in a hierarchial way.",
         sql="SELECT * FROM inventory ORDER BY quantity DESC LIMIT 5;"
         )

def get_model_response(sql,df):
    input_prompt = f"""Your query has returned the following result:
                      sql query= {sql},
                      dataframe = {df}.
                      As a Customer-Friendly Chatbot, it's important to convey this information in a short, clear and helpful manner to the customer. Please generate a response accordingly and if unknown language is found, generate the response but don't translate that word.
    """
    generated_config = GenerationConfig(temperature=0.3)
    response = model.generate_content(input_prompt,generation_config=generated_config)
    generated_text = response.text
    return generated_text

def general_questions():
    questions = vn.generate_questions()
    return questions

async def outputfn(question):
    sql = vn.generate_sql(question)
    print(sql)
    frame = vn.run_sql(sql)
    df = frame.to_string(index=False)
    final_answer = get_model_response(sql,df)
    # questions = vn.generate_followup_questions(question, sql, data)
    # fig = vn.get_plotly_figure(plotly_code="fig = px.bar(df, title='Inventory Visualization')",df=df)
    return final_answer


