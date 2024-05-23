import google.generativeai as genai
import google.ai.generativelanguage as glm
from PIL import Image
from dotenv import load_dotenv
from io import BytesIO
import os, re, json
import pandas as pd

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

"""
async def capture_count(image_file):
    file_bytes = await image_file.read()
    with BytesIO(file_bytes) as img_data:
        with Image.open(img_data) as img:
            ext = os.path.splitext(image_file.filename)[1].lower()
            if ext == '.jpg' or ext == '.jpeg':
                img_format = 'JPEG'
            elif ext == '.png':
                img_format = 'PNG'
            else:
                raise ValueError("Unsupported image format")

            with BytesIO() as buffer:            
                img.save(buffer, format=img_format)
                image_bytes = buffer.getvalue()
                model = genai.GenerativeModel("gemini-pro-vision")
                response = model.generate_content(glm.Content(parts=[glm.Part(text='You have to work like a Object and Object’s count  Detection assistant. You will be provided with an Image clicked from Mobile phone, Detect the main Object in the photo ignoring the environment. Gather as much as details about that object as you can. You have to give the output in a form of JSON with keys named as Name, Brand, Quantity. You have to strictly follow the given name convention. Try to detect the Name and Brand written on the object (Brand is usually a named entity and Product Name is a name given to an object), for Quantity detect how many Objects are present In the given image, you can’t detect Threshold from image so written its value as 0, Based on the Name and Brand of the Object derive it’s Category, for Price try to search Number present with some currency value if not then consider the number you detected by scanning the image(Also you can try to get the Price according to Indian market based on Name and Brand), and for consider values which might describe the weight of the object (NOTE: sometimes the product is a bundle containing the same product of multiple quantities so don’t get confused there). Example (Name: “Mac Book Pro”, Brand: “Apple”, Quantity: 2). NOTE: Quantity should be numbers,  should have some unit associated with it like kg, gram, Oz, Litre, etc., Name and Brand should not be the same and Category should be sensible. After generating the JSON verify it whether the Quantity is not contradicting each other, Brand and Name are not conflicting with each other.'),
                                                            glm.Part(inline_data=glm.Blob(mime_type='image/jpeg',
                                                                                        data=image_bytes))]))
                result = int(response.text)
    return result
"""

async def capture_add(image_file):
    file_bytes = await image_file.read()
    with BytesIO(file_bytes) as img_data:
        with Image.open(img_data) as img:
            ext = os.path.splitext(image_file.filename)[1].lower()
            if ext == '.jpg' or ext == '.jpeg':
                img_format = 'JPEG'
            elif ext == '.png':
                img_format = 'PNG'
            else:
                raise ValueError("Unsupported image format")

            with BytesIO() as buffer:            
                img.save(buffer, format=img_format)
                image_bytes = buffer.getvalue()
                model = genai.GenerativeModel("gemini-pro-vision")
                response = model.generate_content(glm.Content(parts=[glm.Part(text='You have to work like a Object and Object’s count  Detection assistant. You will be provided with an Image clicked from Mobile phone, Detect the main Object in the photo ignoring the environment. Gather as much as details about that object as you can. You have to give the output in a form of JSON with keys named as Name, Brand, Category, Netweight, Quantity, Price, Threshold. You have to strictly follow the given name convention. Try to detect the Name and Brand written on the object (Brand is usually a named entity and Product Name is a name given to an object), for Quantity detect how many Objects are present In the given image, you can’t detect Threshold from image so written its value as 1, Based on the Name and Brand of the Object derive it’s Category, for Price try to search Number present with some currency value if not then consider the number you detected by scanning the image(Also you can try to get the Price according to Indian market based on Name and Brand), and for Netweight consider values which might describe the weight of the object (NOTE: sometimes the product is a bundle containing the same product of multiple quantities so don’t get confused there). Example (Name: “Mac Book Pro”, Brand: “Apple”, Category:”Electronic”, Quantity: 4, Threshold: 0, Price: 200000, Netweight: “1.5 kgs”). NOTE: Threshold, Price and Quantity should be numbers, Netweight should have some unit associated with it like kg, gram, Oz, Litre, etc., Name and Brand should not be the same and Category should be sensible. After generating the JSON verify it whether the Quantity and Netweight are not contradicting each other, Brand and Name are not conflicting with each other, Price is not confused with Quantity or Netweight.'),
                                                            glm.Part(inline_data=glm.Blob(mime_type='image/jpeg',
                                                                                        data=image_bytes))]))
                result = response.text
                print(result)
                json_objects = re.findall(r'{.*?}', result, re.DOTALL)
                if json_objects:
                    json_data = json.loads(json_objects[0])
                else:
                    raise ValueError("No valid JSON object found in the response")
                print(type(json_data))
    return json_data

async def capture_delete(image_file):
    file_bytes = await image_file.read()
    with BytesIO(file_bytes) as img_data:
        with Image.open(img_data) as img:
            ext = os.path.splitext(image_file.filename)[1].lower()
            if ext == '.jpg' or ext == '.jpeg':
                img_format = 'JPEG'
            elif ext == '.png':
                img_format = 'PNG'
            else:
                raise ValueError("Unsupported image format")

            with BytesIO() as buffer:            
                img.save(buffer, format=img_format)
                image_bytes = buffer.getvalue()
                model = genai.GenerativeModel("gemini-pro-vision")
                response = model.generate_content(glm.Content(parts=[glm.Part(text='You have to work like a Object and Object’s count  Detection assistant. You will be provided with an Image clicked from Mobile phone, Detect the main Object in the photo ignoring the environment. Gather as much as details about that object as you can. You have to give the output in a form of JSON with keys named as Name and Brand. You have to strictly follow the given name convention. Try to detect the Name and Brand written on the object (Brand is usually a named entity and Product Name is a name given to an object).Example (Name: “Mac Book Pro”, Brand: “Apple”). Name and Brand should not be the in relation with each other. After generating the JSON verify it whether the Brand and Name are not conflicting with each other.'),
                                                            glm.Part(inline_data=glm.Blob(mime_type='image/jpeg',
                                                                                        data=image_bytes))]))
                result = response.text
                json_objects = re.findall(r'{.*?}', result, re.DOTALL)
                if json_objects:
                    json_data = json.loads(json_objects[0])
                else:
                    raise ValueError("No valid JSON object found in the response")
                print(type(json_data))
    return json_data


async def capture_inc(image_file):
    file_bytes = await image_file.read()
    with BytesIO(file_bytes) as img_data:
        with Image.open(img_data) as img:
            ext = os.path.splitext(image_file.filename)[1].lower()
            if ext == '.jpg' or ext == '.jpeg':
                img_format = 'JPEG'
            elif ext == '.png':
                img_format = 'PNG'
            else:
                raise ValueError("Unsupported image format")

            with BytesIO() as buffer:            
                img.save(buffer, format=img_format)
                image_bytes = buffer.getvalue()
                model = genai.GenerativeModel("gemini-pro-vision")
                response = model.generate_content(glm.Content(parts=[glm.Part(text='You have to work like a Object and Object’s count  Detection assistant. You will be provided with an Image clicked from Mobile phone, Detect the main Object in the photo ignoring the environment. Gather as much as details about that object as you can. You have to give the output in a form of JSON with keys named as Name, Brand, Quantity. You have to strictly follow the given name convention. Try to detect the Name and Brand written on the object (Brand is usually a named entity and Product Name is a name given to an object), for Quantity detect how many Objects are present In the given image, you can’t detect Threshold from image so written its value as 0, Based on the Name and Brand of the Object derive it’s Category, for Price try to search Number present with some currency value if not then consider the number you detected by scanning the image(Also you can try to get the Price according to Indian market based on Name and Brand), and for consider values which might describe the weight of the object (NOTE: sometimes the product is a bundle containing the same product of multiple quantities so don’t get confused there). Example (Name: “Mac Book Pro”, Brand: “Apple”, Quantity: 2). NOTE: Quantity should be numbers,  should have some unit associated with it like kg, gram, Oz, Litre, etc., Name and Brand should not be the same and Category should be sensible. After generating the JSON verify it whether the Quantity is not contradicting each other, Brand and Name are not conflicting with each other.'),
                                                            glm.Part(inline_data=glm.Blob(mime_type='image/jpeg',
                                                                                        data=image_bytes))]))
                result = response.text
                json_objects = re.findall(r'{.*?}', result, re.DOTALL)
                if json_objects:
                    json_data = json.loads(json_objects[0])
                else:
                    raise ValueError("No valid JSON object found in the response")
                print(type(json_data))
    return json_data