# Usar imagem base com Python 3.12
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Diretório de trabalho
WORKDIR /app

# Copiar os arquivos do projeto
COPY pyproject.toml poetry.lock* ./
COPY .env .env

# Instalar dependências com Poetry (sem criar novo virtualenv)
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copiar o restante do código
COPY . .

# Expor a porta padrão do Streamlit
EXPOSE 8501

# Comando padrão para rodar o Streamlit
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]