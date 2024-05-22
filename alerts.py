from twilio.rest import Client
from bhashini import translation
import os
from dotenv import load_dotenv
load_dotenv()
account_sid = os.getenv("TWILIO_SID") 
auth_token = os.getenv("TWILIO_TOKEN")
client = Client(account_sid, auth_token)


async def twilio_message(reply):
    message = client.messages.create(
        from_='+12515122573',
        body=reply,
        to='+919594450405')
    print(message.sid)


async def alert_message(operation,Name, Brand, language):
    try: 
        if language == "English":
            if operation=="decrement":
                message = f"Your stock for {Name} of {Brand} has decreased the threshold value."
            elif operation == "delete":
                message = f"Your product {Name} of {Brand} has been successfully deleted"
            messi = await twilio_message(message)
            return {"success":True, "alert_message":message}
        else:
            if operation=="decrement":
                message = f"Your stock for {Name} of {Brand} has decreased the threshold value."
                trans_message = await translation("English", language, message)
                print(trans_message['translated_content'])
            elif operation == "delete":
                message = f"Your product {Name} of {Brand} has been successfully deleted"
                trans_message = await translation("English", language, message)
                print(trans_message['translated_content'])
            messi = await twilio_message(trans_message['translated_content'])
            return {"success":True, "alert_message":trans_message['translated_content']}
    except Exception as e:
        print(f"Error: {str(e)}")
        return { "message": "Error processing alert message text", "success": False}
