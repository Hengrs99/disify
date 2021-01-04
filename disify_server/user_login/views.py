from django.shortcuts import render
from django.http import HttpResponse
import os
from dotenv import load_dotenv

def callback(response):
    client_info = response.GET
    code = client_info['code']
    load_dotenv()
    path = os.getenv("PROJECT_PATH") + "tmp.txt"
    with open(path, 'w') as file:
        file.write(code) 
    return render(response, "user_login/callback.html", {'code': code})
