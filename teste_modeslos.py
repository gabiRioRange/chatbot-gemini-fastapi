import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("AIzaSyBSPFaCPH85dgo9PhElTgAhSVhQXz66eac"))

print("Buscando modelos disponíveis para sua chave...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Erro ao conectar: {e}")