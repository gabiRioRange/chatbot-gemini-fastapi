# Usa uma imagem leve do Python
FROM python:3.12-slim
# Define a pasta de trabalho dentro do container
WORKDIR /app

# Instala dependências do sistema necessárias para o SQLite e Build
RUN apt-get update && apt-get install -y build-essential

# Copia os arquivos de dependência primeiro (para cachear)
COPY requirements.txt .

# Instala as bibliotecas Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o resto do código
COPY . .

# Expõe as portas (8000 backend, 8501 frontend)
EXPOSE 8000 8501

# Cria um script para rodar os dois serviços juntos
RUN echo '#!/bin/bash\nuvicorn main:app --host 0.0.0.0 --port 8000 & streamlit run frontend.py --server.port 8501 --server.address 0.0.0.0' > start.sh
RUN chmod +x start.sh

# Comando para iniciar
CMD ["./start.sh"]