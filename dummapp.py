from fastapi import FastAPI,File,UploadFile,Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os, base64, subprocess
from tempfile import NamedTemporaryFile
from openai import OpenAI
import json
from bhashini import translation, text_to_speech, transcribe
from image_detect import capture_add, capture_inc, capture_delete
from inventory import check_existing_user, get_data, add_to_supabase, increment_to_supabase, decrement_to_supabase, delete_supabase, supabase, url
from alerts import alert_message
import google.generativeai as genai
from fastapi.templating import Jinja2Templates
from chat_final import outputfn
import uvicorn


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

languages = {
    "Hindi": "hi", #hindi
    "Gom": "gom", #Gom
    "Kannade": "kn", #Kannada
    "Dogri": "doi", #Dogri    
    "Bodo": "brx", #Bodo 
    "Urdu": "ur",  #Urdu
    "Tamil": "ta",  #Tamil
    "Kashmiri": "ks",  #Kashmiri
    "Assamese": "as",  #Assamese
    "Bengali": "bn", #Bengali
    "Marathi": "mr", #Marathi
    "Sindhi": "sd", #Sindhi
    "Maihtili": "mai",#Maithili
    "Punjabi": "pa", #Punjabi
    "Malayalam": "ml", #Malayalam
    "Manipuri": "mni",#Manipuri
    "Telugu": "te", #Telugu
    "Sanskrit": "sa", #Sanskrit
    "Nepali": "ne", #Nepali
    "Santali": "sat",#Santali
    "Gujarati": "gu", #Gujarati
    "Oriya": "or", #Oriya
    "English": "en",#English
}

"""
@app.post("/voice")
async def upload_audio(file: UploadFile = File(...)):
    try:
        command = ["ffmpeg", "-i", "-", "-acodec", "libmp3lame", "-f", "mp3", "-"]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        file_content = await file.read()
        output, error = process.communicate(input=file_content)
        if process.returncode != 0:
            return JSONResponse(status_code=500, content={"message":f"FFmpeg error: {error.decode()}"})
        base64_encoded_data = base64.b64encode(output).decode('utf-8')
        source_text = await transcribe("Hindi",base64_encoded_data)
        text = source_text["transcribed_content"]
        return JSONResponse(content={"message":text}, status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message":str(e)}, status_code=400)
"""
#username:str=Form(...),password:str=Form(...),email:str=Form(...),contact:str=Form(...),language:str=Form(...)

templates = Jinja2Templates(directory="templates")

@app.get("/confirmation")
async def read_root():
    return templates.TemplateResponse("index.html")


@app.post("/verifyemail")
async def verifyemail(request:Request):
    try:
        
        data = await request.json()
        password = data["password"]
        email = data["email"]
         # Using get to provide a default if not supplied
        # Check if the username, email, or contact already exists in your database
        if await check_existing_user("email", email):
            return JSONResponse(content={"message": "User already exists", "success": False}, status_code=403)
        user_data = supabase.auth.sign_up({"email":email, "password":password})
        user_id = user_data.user.id
        print(user_id)
        """
        result = supabase.table("users").insert({
                    "username": username,
                    "email": email,
                    "language": language,
                    "contact": contact,
                    "user_id": user_id
                }).execute()
        if result.error:
            return JSONResponse(content={"message": "Failed to register the user", "success": False}, status_code=403)4
            """
        return JSONResponse(content={"message":"User registered successfully, please verify your email", "success":True}, status_code=200)
        
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": f"Error: {str(e)}" , "success": False}, status_code=500)

@app.post("/signup")
async def signup(request:Request):
    try:
        data = await request.json()
        username = data["username"]
        password = data["password"]
        email = data["email"]
        language = data["language"]
        contact = data["contact"] 
        city = data["city"]
         # Using get to provide a default if not supplied
        # Check if the username, email, or contact already exists in your database
        if await (check_existing_user("email", email) or
                check_existing_user("contact", contact) or
                check_existing_user("username", username)):
            return JSONResponse(content={"message": "User already exists"}, status_code=403)
        user_data = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print(user_data)
        user_id = user_data.user.id
        result = supabase.table("users").insert({
                    "username": username,
                    "email": email,
                    "language": language,
                    "contact": contact,
                    "user_id": user_id,
                    "city": city
                }).execute()
        return JSONResponse(content={"message":"Mauj kar bhava", "success":True, "user_id":user_id}, status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": f"Error: {str(e)}" , "success": False}, status_code=500)


#email: str = Form(...), password: str=Form(...)

@app.post('/signin')
async def loginn(request:Request):
    try:
        
        data = await request.json()
        print(data)
        email = data["email"]
        
        password = data["password"]
        
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print(response)
        user_id = response.user.id
        language = await get_data("language", "XXX", "XXX", user_id)
        print("This is language",language[0]["language"])
        return JSONResponse(content={"message":"User logged in Successfully", "success":True, "user_id":user_id, "language":language[0]["language"]}, status_code=200)
    except Exception as e:
        resp = str(e)
        return JSONResponse(content={"message":resp, "success":False}, status_code = 500)
    
"""
@app.post("/getimage_add")
async def getimage_add(Image: UploadFile = File(...), language: str = Form(...)):
    try:
        data = await capture_add(Image)
        translated_json = data.copy()
        final_translated = data.copy()
        for key in translated_json:
            if translated_json[key]:
                if type(translated_json[key]) == str:
                    translated_json[key] = await translation("English", language, translated_json[key])
                    final_translated[key] = translated_json[key]["translated_content"]
        return JSONResponse(content={"data": final_translated}, status_code=200)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "text": "Error processing text", "success": False}, status_code=500)

@app.post("/getimage_count")
async def getimage_count(Image: UploadFile = File(...)):
    try:
        data = await capture_count(Image)
        return JSONResponse(content={"data":data}, status_code=200)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "text": "Error processing text", "success": False}, status_code=500)
"""

@app.post("/get_imagedets")
async def getimage_add(file: UploadFile = File(...), language: str = Form(...), operation: str=Form(...)):
    try:
        if operation == "add":
            data = await capture_add(file)
        elif operation == "delete":
            data = await capture_delete(file)
        else:
            data = await capture_inc(file)
        translated_json = data.copy()
        final_translated = data.copy()
        for key in translated_json:
            if translated_json[key]:
                if type(translated_json[key]) == str:
                    translated_json[key] = await translation("English", language, translated_json[key])
                    final_translated[key] = translated_json[key]["translated_content"]
        return JSONResponse(content={"data": final_translated, "success":True}, status_code=200)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "text": "Error processing text", "success": False}, status_code=500)


"""
@app.post("/staticvoice1")
async def voiceassistant1(language: str = Form(...)):
    try:
        static_response = "Hello what operation do you want to perform?"
        translate_response = await translation("English",language,static_response)
        translate_text = translate_response["translated_content"]
        speech = await text_to_speech(language,translate_text)
        if speech["status_code"] == 200:
            tts_b64 = speech["tts_base64"]
            audio_bytes = base64.b64decode(tts_b64)
            with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            return FileResponse(path=tmp_path, filename="output.mp3", media_type="audio/mpeg")
        else:
            return JSONResponse(content={"message": "Error generating speech for static voice1", "success": False}, status_code=speech["status_code"])
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "message": "Error processing text for static voice1", "success": False}, status_code=500)    
    

@app.post("/staticvoice2")
async def voiceassistant2(language: str = Form(...), operation: str = Form(...)):
    try:
        speech = None
        if(operation=="add"):
            static_response = "Enter details for addition"
            translate_response = await translation("English",language,static_response)
            translate_text = translate_response["translated_content"]
            speech = await text_to_speech(language,translate_text)
        elif(operation=="increment"):
            static_response = "Enter details for increment"
            translate_response = await translation("English",language,static_response)
            translate_text = translate_response["translated_content"]
            speech = await text_to_speech(language,translate_text)
        elif(operation=="decrement"):
            static_response = "Enter details for decrement"
            translate_response = await translation("English",language,static_response)
            translate_text = translate_response["translated_content"]
            speech = await text_to_speech(language,translate_text)
        else:
            static_response = "delete"
            translate_response = await translation("English",language,static_response)
            translate_text = translate_response["translated_content"]
            speech = await text_to_speech(language,translate_text)
        if speech["status_code"] == 200:
            tts_b64 = speech["tts_base64"]
            audio_bytes = base64.b64decode(tts_b64)
            with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            return FileResponse(path=tmp_path, filename="output.mp3", media_type="audio/mpeg")
        else:
            return JSONResponse(content={"message": "Error generating speech for staticvoice2", "success": False}, status_code=speech["status_code"])
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "message": "Error processing text for static voice2", "success": False}, status_code=500)
"""
        

@app.post('/get_details')
async def get_details(language: str = Form(...), operation: str = Form(...), file: UploadFile = File(...)):
    try:
        print(language)
        command = ["ffmpeg", "-i", "-", "-acodec", "libmp3lame", "-f", "mp3", "-"]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        file_content = await file.read()
        output, error = process.communicate(input=file_content)
        if process.returncode != 0:
            return JSONResponse(status_code=500, content={"message":f"FFmpeg error: {error.decode()}"})
        base64_encoded_data = base64.b64encode(output).decode('utf-8')
        source_text = await transcribe(language,base64_encoded_data)
        text = source_text["transcribed_content"]
        print(text)
        translated_text = await translation(language, "English", text)
        details = translated_text["translated_content"]
        print(details)
        client=OpenAI(api_key = OPENAI_API_KEY)
        if operation == 'add':
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""
            You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.
            Example: (Name: Wheat Flour, Brand: Aashirvad, Category: Baking, Netweight: 10KG, Quantity: 25, Price: 70, Threshold: 5).
            Based on the text below, extract the Name of product, Brand of product, Category of product, Net Weight of product, Quantity of product, 
            Price of product, threshold of product. Make sure that price and quantity are written in number format. If any of the 7 entered parameters are not present 
            then keep the json value of that parameter empty. The string type parameters are Name, Brand, Netweight, Category. Keep 0 for number type parameter, 
            the parameters are Quantity, Price, Threshold.:\n{details}
            """
            response = model.generate_content(prompt)
            print("Full response object:", response)
            
            # Assuming that response.text directly contains the JSON data
            response_text = response.text
            print("Response Text:", response_text)

            try:
                # Parsing the JSON string directly from response.text
                response_data = json.loads(response_text)
                print("Parsed JSON:", response_data)
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
                return JSONResponse(status_code=500, content={"message": "Failed to decode JSON"})
            except Exception as e:
                print(f"Unexpected error: {e}")
                return JSONResponse(status_code=500, content={"message": "Error processing response"})
#prompt=f"You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.\nExample: (Name: Wheat Flour, Brand: Aashirvad, Margin: 6).\nBased on the text below, extract the Name of product, Brand of product, Margin by which to increase quantity of product. Make sure that Margin is written in numeric format. If any of the 3 entered parameters are not present then return the json value of that parameter as empty.:\n{details}"
    # Continue with your processing using 'response_data'
        elif operation == 'increment':
            model = genai.GenerativeModel('gemini-pro')
            prompt=f"You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.\nExample: (Name: Wheat Flour, Brand: Aashirvad, Quantity: 6).\nBased on the text below, extract the Name of product, Brand of product, Quantity by which to increase count of product. Make sure that Quantity is written in numeric format. If any of the 3 entered parameters are not present then return the json value of that parameter as empty.:\n{details}"
            response = model.generate_content(prompt)
            print("Full response object:", response)
            
            # Assuming that response.text directly contains the JSON data
            response_text = response.text
            print("Response Text:", response_text)

            try:
                # Parsing the JSON string directly from response.text
                response_data = json.loads(response_text)
                print("Parsed JSON:", response_data)
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
                return JSONResponse(status_code=500, content={"message": "Failed to decode JSON"})
            except Exception as e:
                print(f"Unexpected error: {e}")
                return JSONResponse(status_code=500, content={"message": "Error processing response"})
            
                  #f"You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.\nExample: (Name: Wheat Flour, Brand: Aashirvad, Margin: 6).\nBased on the text below, extract the Name of product, Brand of product, Margin by which to decrease quantity of product. Make sure that Margin is written in numeric format. If any of the 3 entered parameters are not present then return the json value of that parameter as empty.:\n{details}"
        elif operation=='decrement':
            model = genai.GenerativeModel('gemini-pro')
            prompt=f"You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.\nExample: (Name: Wheat Flour, Brand: Aashirvad, Quantity: 6).\nBased on the text below, extract the Name of product, Brand of product, Quantity by which to decrease count of product. Make sure that Quantity is written in numeric format. If any of the 3 entered parameters are not present then return the json value of that parameter as empty.:\n{details}"
            response = model.generate_content(prompt)
            print("Full response object:", response)
            
            # Assuming that response.text directly contains the JSON data
            response_text = response.text
            print("Response Text:", response_text)

            try:
                # Parsing the JSON string directly from response.text
                response_data = json.loads(response_text)
                print("Parsed JSON:", response_data)
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
                return JSONResponse(status_code=500, content={"message": "Failed to decode JSON"})
            except Exception as e:
                print(f"Unexpected error: {e}")
                return JSONResponse(status_code=500, content={"message": "Error processing response"})
        #f"You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.\nExample: (Name: Wheat Flour, Brand: Aashirvad).\nBased on the text below, extract the Name of product and Brand of product. If any of the 2 entered parameters are not present then return the json value of that parameter as empty.:\n{details}"
        elif operation=='delete':
            model = genai.GenerativeModel('gemini-pro')
            prompt=f"You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.\nExample: (Name: Wheat Flour, Brand: Aashirvad).\nBased on the text below, extract the Name of product and Brand of product. If any of the 2 entered parameters are not present then return the json value of that parameter as empty.:\n{details}"
            response = model.generate_content(prompt)
            print("Full response object:", response)
            
            # Assuming that response.text directly contains the JSON data
            response_text = response.text
            print("Response Text:", response_text)

            try:
                # Parsing the JSON string directly from response.text
                response_data = json.loads(response_text)
                print("Parsed JSON:", response_data)
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON: {e}")
                return JSONResponse(status_code=500, content={"message": "Failed to decode JSON"})
            except Exception as e:
                print(f"Unexpected error: {e}")
                return JSONResponse(status_code=500, content={"message": "Error processing response"})
        translated_json = response_data.copy()
        final_translated = response_data.copy()
        for key in translated_json:
            if translated_json[key]:
                if type(translated_json[key]) == str:
                    translated_json[key] = await translation("English", language, translated_json[key])
                    final_translated[key] = translated_json[key]["translated_content"]
        print(f"final_translated json: {final_translated}")
        print(type(final_translated))
        return JSONResponse(content={'message': final_translated, 'english_json': response_data}, status_code=200)

    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "message": "Error processing get_details", "success": False}, status_code=500)
    
#operation: str=Form(...), language: str=Form(...), Name: str =Form(...), Brand: str=Form(...),Category: str=Form(...), Quantity: str=Form(...), Threshold: str=Form(...), Price: str=Form(...), Netweight: str=Form(...), user_id: str=Form(...), Margin: str=Form(...)

@app.post('/get_detailsfin')
async def get_detailsfin(request: Request):
    try:
        details = await request.json()
        print(details)
        operation = details["operation"]
        language = 'Hindi'
        alert = False
        Namex = None
        Brandx = None
        message_alert = None
        
        if operation=="add":

            data = {
                "product_name": details['Name'],
                "brand": details['Brand'],
                "category": details['Category'],
                "quantity": details['Quantity'],
                "threshold": details['Threshold'],
                "price": details['Price'],
                "netweight": details['Netweight'],
                "user_id": details['userId'], 
                "Language": details['language']
            }
            """
            data = {
                "Name": Name,
                "Brand": Brand,
                "Category": Category,
                "Quantity": Quantity,
                "Threshold": Threshold,
                "Price": Price,
                "Netweight": Netweight,
                "user_id": user_id, 
                "Language": language                
            }
            """
            db = await add_to_supabase(data)
            print(db)
            fin_response = await translation('English', language, f"Successfully added the item")
            return JSONResponse(content={'message': fin_response, "alert": alert, "alert_message": message_alert, "success":True}, status_code=200)
        elif operation=="increment":
            
            data = {
                "Name": details['Name'],
                "Brand": details['Brand'],
                "Margin": int(details['Quantity']),
                "userId": details["userId"]
            }
            """
            data = {
                "Name": Name,
                "Brand": Brand,
                "Margin": int(Margin),
                "userId": user_id             
            } 
            """           
            db = await increment_to_supabase(data)
            print(db)
            fin_response = await translation('English', language, f"Successfully incremented the item")
            return JSONResponse(content={'message': fin_response, "alert": alert, "alert_message": message_alert, "success":True}, status_code=200)
        elif operation=='decrement':
            
            data = {
                "Name": details['Name'],
                "Brand": details['Brand'],
                "Margin": int(details['Quantity']),
                "userId": details['userId']
            }
            """
            data = {
                "Name": Name,
                "Brand": Brand,
                "Margin": int(Margin),
                "userId": user_id             
            } 
            """  
            db = await decrement_to_supabase(data)
            print("this is db",db)
            Namex = data["Name"]
            Brandx = data["Brand"]
            result = await get_data("decrement", Namex, Brandx, details["userId"])
            Quantity = result[0]["Quantity"]
            Threshold = result[0]["Threshold"]
            if Quantity <= Threshold:
                message = await alert_message("decrement",Namex, Brandx, language)
                alert = True
                message_alert = message["alert_message"]
            fin_response = await translation('English', language,  f"Successfully decremented the item, remaining quantity: {Quantity}")
            return JSONResponse(content={'message': fin_response, "alert": alert, "alert_message": message_alert, "success": True}, status_code=200)
        elif operation=='delete':
            
            data = {
                "Name": details['Name'],
                "Brand": details['Brand'],
                "userId": details["userId"]
            }
            """
            data = {
                "Name": Name,
                "Brand": Brand,
                "userId": user_id              
            }   
            """
            db = await delete_supabase(data)
            Namex = data["Name"]
            Brandx = data["Brand"]
            message = await alert_message("delete",Namex, Brandx, language)
            alert = True
            message_alert = message["alert_message"]
            print(db)
            fin_response = await translation('English', language,  f"Successfullly deleted the item")
            return JSONResponse(content={'message': fin_response, "alert": alert, "alert_message": message_alert, "success":True}, status_code=200)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "message": "Error processing get_detailsfin", "success": False}, status_code=500)        
    

@app.post('/voice_alert')
async def voice_alert(request: Request):
    try:
        data = await request.json()
        language = data["language"]
        message = data["message"]
        speech = await text_to_speech(language,message)
        if speech["status_code"] == 200:
            tts_b64 = speech["tts_base64"]
            audio_bytes = base64.b64decode(tts_b64)
            with NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            return FileResponse(path=tmp_path, filename="output.mp3", media_type="audio/mpeg")
        else:
            return JSONResponse(content={"response": "Error generating speech", "success": False}, status_code=speech["status_code"])
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "response": "Error processing get details", "success": False}, status_code=500)


@app.post('/view_inventory')
async def db_table(request : Request):
    try:
        
        user_id = await request.json()        
        data = await get_data("all", "XYZ", "XYZ", user_id)
        print(data)
        count = 0
        lowstock = 0
        detailed_inventory=[]
        for i in data:
            count += 1
            print("This is for data elemt:",i["threshold"])
            print(" having value",i['quantity'])
            if (i["quantity"]<= i["threshold"]):
                lowstock += 1
        
            detailed_inventory.append({
                "Name": i["product_name"],
                "Brand": i["brand"],
                "Quantity": i["quantity"],
                "Price": i["price"]
            })
        return JSONResponse(content={"details":detailed_inventory, "success":True, "no_products": str(count),"low_stock": str(lowstock)}, status_code = 200)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "details": "Error processing view_inventory", "success": False}, status_code=500)

#{"Name": "Atta", "Brand":"Aashirvaad", "Category":"Baking","Net Weight": "Ten Kilo","Quantity": 80,"Price":80, "Threshold":0}

"""
async def get_current_user(token: str):
    Extracts and returns the user ID from the token
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{url}/auth/v1/user", headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            return response.json()['user']['id']
        else:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
"""
            
@app.get('/signout')
async def sign_out():
    try:
        res = supabase.auth.sign_out()
        print(res)
        return JSONResponse(content={"message":res,"success":True}, status_code=200)
    except Exception as e:
        print(f"Error: {str(e)}")
        return JSONResponse(content={ "response": "Error processing get details", "success": False}, status_code=500)


@app.post('/chattext')
async def chattext(request : Request):
    try:
        text = await request.json()
        #translate_response = await translation(language,"English",text)
        #translate_text = translate_response["translated_content"]
        print("\n\n",)
        result = await outputfn(text)
        return JSONResponse(content={"messsage":result, "success":True}, status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"messsage":"Failure ho gaya", "success":False}, status_code=500)

@app.post('/translatingshitfoserver')
async def transerver(text: str=Form(...), lang:str=Form(...)):
    try:
        print(text,lang)
        translate_response = await translation("English",lang,text)
        translate_text = translate_response["translated_content"]
        print(translate_text)
        return JSONResponse(content={"messsage":translate_text, "success":True}, status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"messsage":"Failure ho gaya", "success":False}, status_code=500)


@app.post('/translatingshit')
async def trans(text: str=Form(...), lang:str=Form(...)):
    try:
        print(text,lang)
        translate_response = await translation("English",lang,text)
        translate_text = translate_response["translated_content"]
        print(translate_text)
        return JSONResponse(content={"messsage":translate_text, "success":True}, status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"messsage":"Failure ho gaya", "success":False}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
