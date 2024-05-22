import os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_API")
supabase = create_client(url, key)


async def check_existing_user(field_name, value):
    result = supabase.table("users").select(field_name).eq(field_name, value).execute()
    if result.data and len(result.data) > 0:
        return True
    return False

"""
async def add_into_users(id, username, email, isverified):
    language = "Hindi"
    contact: "1234567891"
    response = supabase.table("users").insert({
            "id": id,
            "username": username,
            "email": email,
            "language": language,
            "contact": contact,
            "isverified": isverified
        }).execute()
    return response
"""

async def get_user_data(user_id):
    try:
        data = supabase.table("users").select("username", "email", "language","contact","city").eq("user_id",user_id).execute()
        print("data from get_user_data", data.data)
        return data.data
    except Exception as e:
        print(f"Error: {str(e)}")
        return ({"response":"Unableto fetch the user detail"})


async def get_data(operation, Name, Brand, user_id):
    try:
        data = None
        if(operation == "all"):
            data = supabase.table("inventory").select("product_name", "brand", "quantity", "price", "threshold", "category", "netweight").eq("user_id",user_id).order("quantity").execute()
            return data.data
        elif(operation == "decrement"):
            data = supabase.table("inventory").select("threshold","quantity").eq("product_name", Name).eq("brand", Brand).execute()
            return data.data
        elif(operation == "language"):
            data = supabase.table("users").select("language").eq("user_id", user_id).execute()
            print("data from get_data", data)
            return data.data
        elif(operation == "lowstock"):
            data = supabase.table("inventory").select("product_name", "brand", "quantity", "threshold").eq("user_id",user_id).execute()
            return data.data
    except Exception as e:
        print(f"Error: {str(e)}")
        return ({"response":"Unable to read the data from supabase"})
    
async def add_to_supabase(json):
    try:
        data = supabase.table("inventory").insert(json).execute()
        if(data.data):
            return ({"success":True, "resp_message":"success"})
        else:
            return ({"success":False, "resp_message":"Item Unavailable"})
    except Exception as e:
        print(f"Error: {str(e)}")
        return ({"resp_message":"Unable to add please try again","success":False})
    
async def increment_to_supabase(json):
    try:
        print(json)
        Name = json["Name"]
        Brand = json["Brand"]
        Quantity = json["Margin"]
        user_id = json["userId"]
        present_quantity= supabase.table("inventory").select("*").eq("product_name",Name).eq("brand",Brand).eq("user_id",user_id).execute()
        print(present_quantity)
        if(present_quantity.data):
            present_quantity = int(present_quantity.data[0]["quantity"])
            quantity = present_quantity+Quantity
            print(quantity)
            supabase.table("inventory").update({"quantity": quantity}).eq("product_name", Name).eq("brand", Brand).eq("user_id",user_id).execute()
            return ({"resp_message":"success","success":True})
        else:
            return({"success":False,"resp_message": "Item unavailable"})
    except Exception as e:
        print(f"Error: {str(e)}")
        return ({"resp_message":"Unable to increment please try again","success":False})
    
async def decrement_to_supabase(json):
    try:
        Name = json['Name']
        Brand = json["Brand"]
        Quantity = json["Margin"]
        user_id = json["userId"]
        result = supabase.table("inventory").select("quantity").eq("product_name",Name).eq("brand",Brand).eq("user_id",user_id).execute()
        if result.data and len(result.data) > 0:
            # Assuming the result is a list of dictionaries
            present_quantity = result.data[0].get("quantity")
            print("Current quantity from database:", present_quantity)
        quantity = present_quantity-Quantity
        supabase.table("inventory").update({"quantity": quantity}).eq("product_name", Name).eq("brand", Brand).eq("user_id",user_id).execute()
        return ({"success":True,"resp_message":"success","Name":Name, "Brand":Brand})
    except Exception as e:
        print(f"Error: {str(e)}")
        return ({"resp_message":"Unable to decrement please try again","success":False})

async def delete_supabase(json):
    try:     
        Brand = json["Brand"]
        Name = json["Name"]
        user_id = json["userId"]
        dat = supabase.table("inventory").delete().eq("product_name",Name).eq("brand",Brand).eq("user_id",user_id).execute()
        if dat.data:
            return ({"success":True,"resp_message":"success"})
        else:
            return ({"success":False,"resp_message":"Item Unavailable"})
    except Exception as e:
        print(f"Error: {str(e)}")
        return ({"resp_message":"Unable to delete, please try again","success":False})
#json = {"Name":"Butter", "Brand":"Amul", "Category": "Bakery", "Net Weight": "250 grams", "Quantity": 45, "Price":150, "Threshold": 22}
#data = add_to_supabase(json)
#print(data)
