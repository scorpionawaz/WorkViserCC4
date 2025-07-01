from dotenv import load_dotenv
import os
from groq import Groq
from app.PE.systemprompts import domain_extractor
import ast

load_dotenv()   

def domain_extractor(task_details):
    
    client = Groq(
        # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY") )
    chat_completion = client.chat.completions.create(
        
        temperature=0.0,
        
        messages=[
            {
                "role": "system",
                "content": f"{domain_extractor}"
            },
            {
                "role": "user",
                "content":f"{task_details}",
            }
        ],
        model="llama3-70b-8192",
    )
    extracted_domains = ast.literal_eval(chat_completion.choices[0].message.content)
    return extracted_domains

