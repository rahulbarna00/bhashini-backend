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
                response = model.generate_content(glm.Content(parts=[glm.Part(text='Focus only on the product in the image and return only the count of products(quantity). Note that the answer should only be a number'),
                                                            glm.Part(inline_data=glm.Blob(mime_type='image/jpeg',
                                                                                        data=image_bytes))]))
                result = int(response.text)
    return result


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
                response = model.generate_content(glm.Content(parts=[glm.Part(text='Focus only on the product in the image and generate a json file with Name of product, Brand of product, Category of product, Price of product, Netweight of the product, Quantity of product and Threshold of product. Here is an example of the format:\nExample: (Name: Wheat Flour, Brand: Aashirvad, Category: Baking, Netweight: 10KG, Quantity: 25, Price: 70, Threshold: 5).\nMake sure that Price, Quanitity and Threshold are written in number format. If any of the 7 entered parameters are not present in the image or you are not sure about the value of that parameter then keep the json value of that parameter as blank.'),
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
                response = model.generate_content(glm.Content(parts=[glm.Part(text='Focus only on the product in the image and generate a json file with Name of product, Brand of product. Here is an example of the format:\nExample: (Name: Wheat Flour, Brand: Aashirvad).\nIf any of the 2 entered parameters are not present then keep the json value of the parameter blank.'),
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
                response = model.generate_content(glm.Content(parts=[glm.Part(text='Focus only on the product in the image and generate a json file with Name of product, Brand of product, Quantity of Product. Here is an example of the format:\nExample: (Name: Wheat Flour, Brand: Aashirvad, Quantity: 25).\nMake sure that Quanitity is written in number format. If any of the 3 entered parameters are not present then keep the json value of the parameter blank.'),
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