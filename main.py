import os
import google.generativeai as genai
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. Carrega as variáveis de ambiente (sua chave no arquivo .env)
load_dotenv()

# 2. Configura a API do Google Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("⚠️ ERRO: A chave GEMINI_API_KEY não foi encontrada no arquivo .env")

genai.configure(api_key=api_key)

# Configuração do modelo (gemini-3-pro-preview é avançado e poderoso)
generation_config = {
    "temperature": 0.7,  # Criatividade (0 a 1)
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-flash-latest",
    generation_config=generation_config,
)

# 3. Inicia o servidor FastAPI
app = FastAPI(
    title="Chatbot Inteligente - Gabriel",
    description="API de Chatbot integrada com Google Gemini"
)

# 4. Memória Simples (Lista para guardar o contexto)
chat_session = model.start_chat(history=[])

# Modelo de dados para receber o JSON do usuário
class MensagemUsuario(BaseModel):
    texto: str

@app.get("/")
def home():
    return {"status": "online", "mensagem": "O Chatbot do Gabriel está rodando com Gemini!"}

@app.post("/chat")
async def conversar(msg: MensagemUsuario):
    entrada = msg.texto.strip()
    
    # --- Lógica de Comandos Especiais ---
    if entrada.startswith("/resumir"):
        texto = entrada.replace("/resumir", "").strip()
        prompt = f"Resuma o seguinte texto de forma concisa em tópicos: {texto}"
        response = model.generate_content(prompt)
        return {"resposta": response.text, "tipo": "comando_resumo"}

    elif entrada.startswith("/sentimento"):
        texto = entrada.replace("/sentimento", "").strip()
        prompt = f"Analise o sentimento deste texto. Responda APENAS: 'Positivo', 'Negativo' ou 'Neutro'. Texto: {texto}"
        response = model.generate_content(prompt)
        return {"resposta": response.text.strip(), "tipo": "comando_sentimento"}

    # --- Conversa Normal (com Memória) ---
    try:
        # Envia a mensagem para a sessão de chat ativa (que guarda histórico)
        response = chat_session.send_message(entrada)
        return {"resposta": response.text}
        
    except Exception as e:
        return {"erro": f"Erro na comunicação com o Gemini: {str(e)}"}