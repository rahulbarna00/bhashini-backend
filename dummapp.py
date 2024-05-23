from fastapi import FastAPI,File,UploadFile,Form, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os, base64, subprocess
from tempfile import NamedTemporaryFile
import json
from bhashini import translation, text_to_speech, transcribe
from image_detect import capture_add, capture_inc, capture_delete
from inventory import get_user_data, check_existing_user, get_data, add_to_supabase, increment_to_supabase, decrement_to_supabase, delete_supabase, supabase, url
from alerts import alert_message
import google.generativeai as genai
from fastapi.templating import Jinja2Templates
from chat_final import outputfn
import uvicorn


load_dotenv()

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
        return JSONResponse(content={"message":"Please verify your email", "success":True}, status_code=200)
        
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
        if await check_existing_user("email", email):
            return JSONResponse(content={"message": "User with this Email already exists", "success":False}, status_code=403)
        elif await check_existing_user("contact", contact):
            return JSONResponse(content={"message": "User with this Contact already exists", "success":False}, status_code=403)
        elif await check_existing_user("username",username):
            return JSONResponse(content={"message":"User with this Username already exists", "success":False}, status_code=403)
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
        return JSONResponse(content={"message":"Signup Successful", "success":True, "user_id":user_id}, status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": f"Error: {str(e)}" , "success": False}, status_code=500)

@app.post("/trainmodel")
async def trainmodel(request:Request):
    try:
        data = await request.json()
        print("train model data: ", data)
        return JSONResponse(content={"success":True}, status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"success":False}, status_code=500)

#email: str = Form(...), password: str=Form(...)

@app.post('/signin')
async def loginn(request:Request):
    try:
        
        data = await request.json()
        #print(data)
        email = data["email"]
        
        password = data["password"]
        
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print(response)
        user_id = response.user.id
        language = await get_data("language", "XXX", "XXX", user_id)
        user_data = await get_user_data(user_id)
        username= user_data[0]["username"]
        city= user_data[0]["city"]
        contact = user_data[0]["contact"]
        print("This is language",language[0]["language"])
        print("User id is:", user_id)

        # message = await training(user_id)
        # print(message)
        return JSONResponse(content={"message":"User logged in Successfully", "success":True, "user_id":user_id, "language":language[0]["language"], "username":username, "email":email, "city":city,
                                     "contact":str(contact)}, status_code=200)
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
        if language == "English":
            final_translated = data
        else: 
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
        mess = await translation("English", language, "Error reading details from image")
        return JSONResponse(content={ "message": mess["translated_content"], "success": False}, status_code=500)


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
        details = None
        command = ["ffmpeg", "-i", "-", "-acodec", "libmp3lame", "-f", "mp3", "-"]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        file_content = await file.read()
        output, error = process.communicate(input=file_content)
        if process.returncode != 0:
            return JSONResponse(status_code=500, content={"message":f"FFmpeg error: {error.decode()}"})
        base64_encoded_data = base64.b64encode(output).decode('utf-8')
        source_text = await transcribe(language, base64_encoded_data)
        text = source_text["transcribed_content"]
        print(text)
        if language == "English":
            details = text
        else:
            translated_text = await translation(language, "English", text)
            details = translated_text["translated_content"]
        print(details)

        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = ""

        if operation == 'add':
            prompt = f"""
            You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.
            Example: (Name: Wheat Flour, Brand: Aashirvad, Category: Baking, Netweight: 10KG, Quantity: 25, Price: 70, Threshold: 5).
            Based on the text below, extract the Name of product, Brand of product, Category of product, Net Weight of product, Quantity of product, 
            Price of product, threshold of product. Make sure that price and quantity are written in number format. If any of the 7 entered parameters are not present 
            then keep the json value of that parameter empty. The string type parameters are Name, Brand, Netweight, Category. Keep 0 for number type parameter, 
            the parameters are Quantity, Price, Threshold.:\n{details}
            Strictly return all the 7 parameters.
            """
        elif operation == 'increment':
            prompt = f"""
            You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.
            Example: (Name: Wheat Flour, Brand: Aashirvad, Quantity: 25).
            Based on the text below, extract the Name of product, Brand of product and Quantity of product. Make sure that Quantity is written in number format. If any of the 3 entered parameters are not present 
            then keep the json value of that parameter empty for string type parameter and 0 for number type parameter. The string type parameters are Name and Brand. Number type parameter is Quantity. Provide all the three parameters:\n{details}.
            Strictly return all the 3 parameters
            """
        elif operation == 'decrement':
            prompt = f"""
            You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.
            Example: (Name: Wheat Flour, Brand: Aashirvad, Quantity: 25).
            Based on the text below, extract the Name of product, Brand of product and Quantity of product. Make sure that Quantity is written in number format. If any of the 3 entered parameters are not present 
            then keep the json value of that parameter empty for string type parameter and 0 for number type parameter. The string type parameters are Name and Brand. Number type parameter is Quantity. Provide all the three parameters:\n{details}.
            Strictly return all the 3 parameters
            """
        elif operation == 'delete':
            prompt = f"""
            You are provided with an example format and the question below. Follow the instructions and return a JSON type answer.
            Example: (Name: Wheat Flour, Brand: Aashirvad).
            Based on the text below, extract the Name of product and Brand of product. If any of the 2 entered parameters are not present 
            then keep the json value of that parameter empty:\n{details}
            """
        
        print("Generated prompt:", prompt)
        response = model.generate_content(prompt)
        print("Full response object:", response)

        # Clean the response text
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        print("Cleaned Response Text:", response_text)

        try:
            response_data = json.loads(response_text)
            print("Parsed JSON:", response_data)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return JSONResponse(status_code=500, content={"message": "Failed to decode JSON"})
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JSONResponse(status_code=500, content={"message": "Error processing response"})
        
        if language == "English":
            final_translated = response_data
            return JSONResponse(content={'message': final_translated}, status_code=200)
        else:
            translated_json = response_data.copy()
            final_translated = response_data.copy()
            for key in translated_json:
                if translated_json[key]:
                    if type(translated_json[key]) == str:
                        translated_json[key] = await translation("English", language, translated_json[key])
                        final_translated[key] = translated_json[key]["translated_content"]
            return JSONResponse(content={'message': final_translated}, status_code=200)

    except Exception as e:
        print(f"Error: {str(e)}")
        if language == "English":
            return JSONResponse(content={"message": f"Error occurred during processing of audio", "success": False}, status_code=500)
        else:
            mess = await translation("English", language, f"Error occurred during processing of audio")
            return JSONResponse(content={"message": mess["translated_content"], "success": False}, status_code=500)
      
#operation: str=Form(...), language: str=Form(...), Name: str =Form(...), Brand: str=Form(...),Category: str=Form(...), Quantity: str=Form(...), Threshold: str=Form(...), Price: str=Form(...), Netweight: str=Form(...), user_id: str=Form(...), Margin: str=Form(...)

@app.post('/get_detailsfin')
async def get_detailsfin(request: Request):
    try:
        details = await request.json()
        print(details)
        operation = details["operation"]
        language = details["language"]
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
            if db["success"]:
                response_message = f"Successfully added the product {details['Name']} of brand {details['Brand']}"
            else:
                response_message = db["resp_message"]
            if language == "English":
                translate_text = response_message
            else:
                fin_response = await translation('English', language, response_message)
                translate_text = fin_response["translated_content"]
            return JSONResponse(content={'message': translate_text, "alert": alert, "alert_message": message_alert, "success":True}, status_code=200)
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
            if db["success"]:
                response_message = f"The quantity of product {details['Name']} of brand {details['Brand']} is increased by {details['Quantity']}"
            else:
                response_message = db["resp_message"]
            if language == "English":
                translate_text = response_message
            else:
                fin_response = await translation('English', language, response_message)
                translate_text = fin_response["translated_content"]
            return JSONResponse(content={'message': translate_text, "alert": alert, "alert_message": message_alert, "success":True}, status_code=200)
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
            if db["success"]:
                Namex = data["Name"]
                Brandx = data["Brand"]
                result = await get_data("decrement", Namex, Brandx, details["userId"])
                print(result)
                Quantity = result[0]["quantity"]
                Threshold = result[0]["threshold"]
                if Quantity <= Threshold:
                    message = await alert_message("decrement",Namex, Brandx, language)
                    alert = True
                    message_alert = message["alert_message"]
                response_message = f"The quantity of product {details['Name']} of brand {details['Brand']} is decreased by {details['Quantity']}"
            else:
                response_message = db["resp_message"]
            if language == "English":
                translate_text = response_message
            else:
                fin_response = await translation('English', language, response_message)
                translate_text = fin_response["translated_content"]
            return JSONResponse(content={'message': translate_text, "alert": alert, "alert_message": message_alert, "success":True}, status_code=200)
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
            if db["success"]:
                Namex = data["Name"]
                Brandx = data["Brand"]
                message = await alert_message("delete",Namex, Brandx, language)
                alert = True
                message_alert = message["alert_message"]
                response_message = f"Successfullly deleted the product {details['Name']} of brand {details['Brand']}"
            else:
                response_message = db["resp_message"]
            if language == "English":
                translate_text = response_message
            else:
                fin_response = await translation('English', language, response_message)
                translate_text = fin_response["translated_content"]
            return JSONResponse(content={'message': translate_text, "alert": alert, "alert_message": message_alert, "success":True}, status_code=200)
    except Exception as e:
        print(f"Error: {str(e)}")
        if language == "English":
            return JSONResponse(content={"message": f"Error occurred, please try again", "success": False}, status_code=500)
        else:
            mess = await translation("English", language, f"Error occured, please try again")
            return JSONResponse(content={ "message": mess["translated_content"], "success": False}, status_code=500)    
    

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
        mess = await translation("English", language, f"Error occured, while generating audio alert")
        return JSONResponse(content={ "message": mess["translated_content"], "success": False}, status_code=500)


@app.post('/genrateaudio')
async def generateaudio(language: str=Form(...), message: str=Form(...)):
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


@app.post('/view_inventory')
async def db_table(request : Request):
    try:
        
        frontend_data = await request.json() 
        user_id = frontend_data["userID"]
        language = frontend_data["language"]       
        data = await get_data("all", "XYZ", "XYZ", user_id)
        count = 0
        lowstock = 0
        detailed_inventory=[]
        for i in data:
            count += 1
            if (i["quantity"]<= i["threshold"]):
                lowstock += 1
        
            detailed_inventory.append({
                "Name": i["product_name"],
                "Brand": i["brand"],
                "Quantity": i["quantity"],
                "Price": i["price"],
                "Threshold": i["threshold"],
                "Netweight": i["netweight"],
                "Category": i["category"]
            })
        return JSONResponse(content={"message":"Done","details":detailed_inventory, "success":True, "no_products": str(count),"low_stock": str(lowstock)}, status_code = 200)
    except Exception as e:
        print(f"Error: {str(e)}")
        if language == "English":
            return JSONResponse(content={"message": f"Error Fetching inventory details", "success": False}, status_code=500)
        else:
            mess = await translation("English", language, f"Error Fetching Inventory details")
            return JSONResponse(content={ "message": mess["translated_content"], "success": False}, status_code=500)

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
async def chattext(request:Request):
    try:
        # text = await request.json()
        translate_text = None
        reponse = await request.json()
        text = reponse["message"]
        user_id = reponse["user_id"]
        language = reponse["language"]
        if language == "English":
            translate_text = text
        else:
            translate_response = await translation(language,"English",text)
            translate_text = translate_response["translated_content"]
        data = await get_data("all","XYZ","XYZ",user_id)
        print(data)
        print("\n\n")
        print(translate_text)
        result = await outputfn(translate_text, data, language)
        return JSONResponse(content={"message":result, "success":True}, status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message":"Failure ho gaya", "success":False}, status_code=500)


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
    

@app.post('/transcribeaudio')
async def transcribeaud(audio:  UploadFile = File(...), language: str=Form(...)):
    try:
        command = ["ffmpeg", "-i", "-", "-acodec", "libmp3lame", "-f", "mp3", "-"]
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        file_content = await audio.read()
        output, error = process.communicate(input=file_content)
        if process.returncode != 0:
            return JSONResponse(status_code=500, content={"message":f"FFmpeg error: {error.decode()}"})
        base64_encoded_data = base64.b64encode(output).decode('utf-8')
        source_text = await transcribe(language,base64_encoded_data)
        text = source_text["transcribed_content"]
        return JSONResponse(content={"messsage":text, "success":True}, status_code=200)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"messsage":"Error occured while transcribing", "success":False}, status_code=500)

@app.post('/chat_audio')
async def chataudio(language: str = Form(...), file: UploadFile = Form(...)):
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
        return JSONResponse(content={"message": text, "success": True}, status_code=200)
    except Exception as e:
        print(e)
        return JSONResponse(content={"message": "Try failure", "success": False}, status_code=500)   


@app.post("/lowstockitems")
async def lowstockitems(request:Request):
    try:
        frontend_data = await request.json()
        user_id = frontend_data["userId"]
        language = frontend_data["language"]
        data = await get_data("lowstock", "XYZ", "XYZ", user_id)
        lowstock_inventory=[]
        for i in data:
            if (i["quantity"]<= i["threshold"]):
                lowstock_inventory.append({
                    "Name": i["product_name"],
                    "Brand": i["brand"],
                    "Quantity": i["quantity"],
                    "Threshold": i["threshold"]
                })
        return JSONResponse(content={"message":"Done","details":lowstock_inventory, "success":True}, status_code = 200)
    except Exception as e:
        print(f"Error: {str(e)}")
        if language == "English":
            return JSONResponse(content={"message": f"Error Fetching low stock details", "success": False}, status_code=500)
        else:
            mess = await translation("English", language, f"Error Fetching low stock details")
            return JSONResponse(content={ "message": mess["translated_content"], "success": False}, status_code=500)


@app.post('/notes')
async def notes(text:str=Form(...), language:str=Form(...)):
    try:
        translate_text = None
        if language == "English":
            translate_text = text
        else:
            translate_response = await translation(language,"English",text)
            translate_text = translate_response["translated_content"]
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        prompt = f"""
You are provided with an example format and the question below. Follow the instructions and return a JSON type answer. 
Extract the Title and description from the message which will be provided by the user at the end. Example for you reference: \n
text_message = The title of notes is Machine learning and the description is Machine learning (ML) is a field of study in artificial intelligence concerned with the development and study of statistical algorithms.\n
Result = \n (Title: Machine learning, Description: Machine learning (ML) is a field of study in artificial intelligence concerned with the development and study of statistical algorithms.).\n Based on the above example and instruction , generate JSON answer for:
text_message = {translate_text}
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
            return JSONResponse(content={"message":response_data}, status_code=200)
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
            return JSONResponse(status_code=500, content={"message": "Failed to decode JSON"})
        except Exception as e:
            print(f"Unexpected error: {e}")
            return JSONResponse(status_code=500, content={"message": "Error processing response"})
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"message": "Error occured during notes"}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)    
    
    

