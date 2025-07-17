from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import os
from dotenv import load_dotenv
import sys
import pandas as pd

# Carregar variáveis de ambiente
load_dotenv()

# Ler a string de conexão do .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Criar engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Testar conexão com tratamento de erro detalhado
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("✅ Conexão bem-sucedida com o banco de dados!")
except Exception as e:
    print("❌ Falha ao conectar ao banco de dados.")
    print("💥 Detalhes do erro:", str(e))
    sys.exit(1)  # Encerra o script com erro

def insert_csv_to_db(csv_path: str, tbl_ponto: str, engine: Engine):
    """
    Carrega um arquivo CSV e insere os dados na tabela do banco via SQLAlchemy.
    
    Args:
        csv_path (str): Caminho do arquivo CSV.
        table_name (str): Nome da tabela no banco.
        engine (Engine): Engine SQLAlchemy conectada ao banco.
    """
    # Carrega o CSV usando o parâmetro
    csv_path = 'C:/Users/alessandro.marques/Desktop/htdocs/cadastro_pontos/tbl_ponto.csv'
    df = pd.read_csv(csv_path)
    
    # Opcional: exibe as primeiras linhas
    print(df.head())
    
    # Insere os dados no banco (adiciona sem apagar dados existentes)
    df.to_sql(tbl_ponto, engine, if_exists='append', index=False)
    
    print(f"Dados do arquivo '{csv_path}' inseridos com sucesso na tabela '{tbl_ponto}'.")
    
insert_csv_to_db('caminho.csv', 'tbl_ponto', engine)
