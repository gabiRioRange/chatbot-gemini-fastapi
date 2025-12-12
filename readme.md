# 🕵️‍♂️ Chatbot RAG Inteligente com Memória & Docker

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## 📋 Sobre o Projeto

Este projeto é um assistente virtual avançado capaz de **ler documentos PDF** e responder perguntas com base neles (RAG - Retrieval-Augmented Generation).

Diferente de chatbots comuns, este sistema possui:
1.  **Memória de Sessão:** Mantém históricos separados para cada usuário.
2.  **Citações Precisas:** Indica exatamente em qual página do PDF a informação foi encontrada.
3.  **Arquitetura Containerizada:** Roda 100% isolado via Docker.

## 🚀 Funcionalidades

* **🧠 IA Generativa:** Integração com Google Gemini 1.5 Flash.
* **📚 RAG (Retrieval-Augmented Generation):** Upload de PDFs, vetorização e busca semântica com FAISS.
* **💾 Persistência:** Banco de dados SQLite para salvar histórico de conversas.
* **🔒 Privacidade:** Gerenciamento de sessões únicas por usuário.
* **🎨 Interface Visual:** Frontend amigável desenvolvido em Streamlit.
* **🐳 Docker:** Deploy simplificado com `docker-compose`.

## 🛠 Tecnologias

* **Backend:** FastAPI, SQLAlchemy, PyPDF, FAISS.
* **Frontend:** Streamlit.
* **IA:** Google Generative AI (Gemini).
* **Infra:** Docker & Docker Compose.

## 📦 Como Rodar (Modo Fácil - Docker)

Se você tem o Docker instalado, basta um comando:

1.  Clone o repositório e crie um arquivo `.env` com sua chave:
    ```env
    GEMINI_API_KEY=sua_chave_aqui
    ```
2.  Suba a aplicação:
    ```bash
    docker-compose up --build
    ```
3.  Acesse:
    * **Frontend (Chat):** http://localhost:8501
    * **Backend (Docs):** http://localhost:8000/docs

## 💻 Como Rodar (Modo Manual)

1.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
2.  Inicie o servidor Backend:
    ```bash
    uvicorn main:app --reload
    ```
3.  Em outro terminal, inicie o Frontend:
    ```bash
    streamlit run frontend.py
    ```

---
Desenvolvido por Gabriel de Souza
