import streamlit as st
import requests
import uuid

st.set_page_config(page_title="Chatbot Pro", page_icon="🕵️")
st.title("🕵️ Chatbot com Fontes & Memória Privada")

API_URL = "http://127.0.0.1:8000"

# --- 1. Gestão de Sessão (Privacidade) ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4()) # Gera ID único
    st.write(f"🔒 Sessão Segura ID: {st.session_state.session_id}")

session_id = st.session_state.session_id

# --- 2. Barra Lateral (Upload Melhorado) ---
with st.sidebar:
    st.header("Base de Conhecimento")
    uploaded_file = st.file_uploader("Enviar PDF", type="pdf")
    
    if uploaded_file and st.button("Processar"):
        with st.spinner("Lendo e indexando..."):
            files = {"file": uploaded_file.getvalue()}
            try:
                res = requests.post(f"{API_URL}/upload", files=files)
                
                if res.status_code == 200:
                    dados = res.json()
                    # VERIFICAÇÃO DE ERRO NO JSON
                    if "erro" in dados:
                        st.error(f"❌ Erro: {dados['erro']}")
                    else:
                        qtd_chunks = dados.get("chunks", 0)
                        st.success(f"✅ PDF Indexado! ({qtd_chunks} trechos lidos)")
                else:
                    st.error(f"Erro no servidor: {res.status_code}")
                    
            except Exception as e:
                st.error(f"Erro de conexão: {e}")

# --- 3. Carregar Histórico Antigo (Persistence) ---
if "carregou_historico" not in st.session_state:
    try:
        res = requests.get(f"{API_URL}/historico/{session_id}")
        if res.status_code == 200:
            historico = res.json()
            st.session_state.messages = [{"role": m["role"], "content": m["content"]} for m in historico]
        else:
            st.session_state.messages = []
    except:
        st.session_state.messages = []
    st.session_state.carregou_historico = True

# --- 4. Chat ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Pergunte algo..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Consultando fontes..."):
            try:
                # Envia o ID da sessão junto!
                payload = {"texto": prompt, "session_id": session_id}
                response = requests.post(f"{API_URL}/chat", json=payload)
                
                if response.status_code == 200:
                    resposta = response.json()["resposta"]
                    st.markdown(resposta)
                    st.session_state.messages.append({"role": "assistant", "content": resposta})
                else:
                    st.error("Erro no servidor.")
            except Exception as e:
                st.error(f"Erro: {e}")