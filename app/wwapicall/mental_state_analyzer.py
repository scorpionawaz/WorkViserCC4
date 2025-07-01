from dotenv import load_dotenv
load_dotenv() 
import os
from groq import Groq
import json
from app.PE.systemprompts import mental_status_analyzerprompt
import ast  

# Below function returns the mentor status of the current employee working on the task

# exmaple of the Converstaion Histrory 

# [
#     {"timestamp" : "2024-06-10T13:15:30.123Z","message" : "I am not able to Figure this Out","mental_status" : "confused"},
#     {"timestamp" : "2024-06-10T13:15:30.123Z","message" : "I am giving up","mental_status" : "giveup"}
# ]

def mental_status_analyzer(convo_history,taskdetails):
    
    client = Groq(
        # This is the default and can be omitted
        api_key=os.environ.get("GROQ_API_KEY") )
    chat_completion = client.chat.completions.create(
        
        temperature=0.0,
        
        messages=[
            {
                "role": "system",
                "content": f"{mental_status_analyzerprompt}"
            },
            {
                "role": "user",
                "content": f"Task Details: {taskdetails}\n\nReal/Current Conversation: {json.dumps(convo_history, indent=2)}"
            }
        ],
        model="llama3-70b-8192",
    )
    mental_status = (chat_completion.choices[0].message.content)
    return mental_status


