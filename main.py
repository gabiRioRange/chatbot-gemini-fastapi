import os
import datetime
import uuid
import numpy as np
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import faiss
from pypdf import PdfReader

# --- Configurações ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("⚠️ Chave GEMINI_API_KEY não encontrada!")

genai.configure(api_key=api_key)
generation_config = {"temperature": 0.3, "max_output_tokens": 8192}
model = genai.GenerativeModel("gemini-flash-latest", generation_config=generation_config)

# --- Banco de Dados (Com Session ID) ---
DATABASE_URL = "sqlite:///./chat.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class MensagemDB(Base):
    __tablename__ = "mensagens"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True) # Separa usuários
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# --- Variáveis Globais RAG ---
# Dicionário simples para guardar texto + página
# Ex: chunks_data = [{"text": "...", "page": 1}, ...]
vector_index = None
chunks_data = [] 

def gerar_embeddings_em_lote(lista_textos):
    todos_embeddings = []
    tamanho_lote = 50
    print(f"🚀 Gerando embeddings para {len(lista_textos)} trechos...")
    for i in range(0, len(lista_textos), tamanho_lote):
        lote = lista_textos[i:i + tamanho_lote]
        if not lote: continue
        try:
            result = genai.embed_content(model="models/text-embedding-004", content=lote, task_type="retrieval_document")
            if 'embedding' in result: todos_embeddings.extend(result['embedding'])
        except Exception as e:
            print(f"❌ Erro lote {i}: {e}")
    return todos_embeddings

app = FastAPI(title="Chatbot Ultimate")

# Modelos de Dados
class ChatRequest(BaseModel):
    texto: str
    session_id: str = "default"

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_index, chunks_data
    print(f"📂 Processando: {file.filename}")
    
    reader = PdfReader(file.file)
    chunks_data = [] 
    
    texto_total_debug = "" # Variável para a gente ver

    for i, page in enumerate(reader.pages):
        texto_pagina = page.extract_text() or ""
        texto_total_debug += texto_pagina + "\n" # Junta tudo para mostrar

        pedacos = [texto_pagina[j:j+1000] for j in range(0, len(texto_pagina), 1000)]
        for pedaco in pedacos:
            if len(pedaco) > 20: 
                chunks_data.append({"text": pedaco, "page": i + 1})

    # --- HORA DA VERDADE: MOSTRAR O TEXTO NO TERMINAL ---
    print("\n" + "="*40)
    print("🔍 O QUE O ROBÔ LEU (Primeiros 500 caracteres):")
    print(texto_total_debug[:500]) 
    print("="*40 + "\n")
    
    if len(texto_total_debug.strip()) < 10:
        print("⚠️ ALERTA: O texto extraído parece vazio!")

    # 2. Gera Vetores
    textos_apenas = [c["text"] for c in chunks_data]
    embeddings = gerar_embeddings_em_lote(textos_apenas)
    
    if embeddings:
        dim = len(embeddings[0])
        vector_index = faiss.IndexFlatL2(dim)
        vector_index.add(np.array(embeddings))
        return {"status": "Sucesso", "chunks": len(chunks_data)}
    
    return {"erro": "Falha ao processar"}
    # 2. Gera Vetores
    textos_apenas = [c["text"] for c in chunks_data]
    embeddings = gerar_embeddings_em_lote(textos_apenas)
    
    # 3. Cria Índice
    if embeddings:
        dim = len(embeddings[0])
        vector_index = faiss.IndexFlatL2(dim)
        vector_index.add(np.array(embeddings))
        return {"status": "Sucesso", "chunks": len(chunks_data)}
    return {"erro": "Falha ao processar"}

@app.post("/chat")
async def conversar(req: ChatRequest, db: Session = Depends(get_db)):
    entrada = req.texto.strip()
    session_id = req.session_id
    
    # Salva histórico isolado por sessão
    db.add(MensagemDB(session_id=session_id, role="user", content=entrada))
    db.commit()

    contexto = ""
    fontes = []

    # --- Busca Inteligente (RAG) ---
    if vector_index and chunks_data:
        query_emb = genai.embed_content(model="models/text-embedding-004", content=entrada, task_type="retrieval_query")["embedding"]
        D, I = vector_index.search(np.array([query_emb]), k=3) # Top 3 trechos
        
        for idx in I[0]:
            if idx < len(chunks_data):
                item = chunks_data[idx]
                texto_trecho = item["text"]
                num_pag = item["page"]
                contexto += f"\n--- Trecho (Pág {num_pag}) ---\n{texto_trecho}\n"
                if num_pag not in fontes: fontes.append(num_pag)

    prompt = entrada
    if contexto:
        prompt = (
            f"Você é um assistente prestativo. Use o contexto abaixo para responder.\n"
            f"Tente encontrar a resposta no texto fornecido. Cite a página se encontrar.\n"
            f"Se a pergunta for genérica (como 'resuma' ou 'fale sobre'), faça um resumo do que você está vendo no contexto.\n\n"
            f"CONTEXTO DO PDF:{contexto}\n\nPERGUNTA: {entrada}"
        )

    try:
        response = model.generate_content(prompt)
        resposta_final = response.text
    except Exception as e:
        resposta_final = f"Erro: {str(e)}"

    db.add(MensagemDB(session_id=session_id, role="bot", content=resposta_final))
    db.commit()

    return {"resposta": resposta_final}

@app.get("/historico/{session_id}")
def ler_historico(session_id: str, db: Session = Depends(get_db)):
    # Retorna apenas msg desta sessão
    msgs = db.query(MensagemDB).filter(MensagemDB.session_id == session_id).order_by(MensagemDB.timestamp.desc()).limit(50).all()
    return msgs[::-1]