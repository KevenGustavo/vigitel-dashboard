# Usa a imagem base do Python oficial (versão Slim para ser mais leve e segura)
FROM python:3.12-slim

# Define variáveis de ambiente para otimização do Python em containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Instala dependências de sistema necessárias (ex: compilação de drivers C para asyncpg se necessário)
# O utilitário gcc e libpq-dev pode ser necessário para algumas wheels, mas tentaremos usar as pré-compiladas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o arquivo de dependências primeiro (aproveita cache de camadas do Docker)
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY src/ /app/src/

# Expõe a porta default para uso local (plataformas injetam sua própria)
EXPOSE 8080

# Comando em forma shell para permitir expansão da variável $PORT que serviços gratuitos usam
CMD uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8080}
