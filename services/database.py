import os
import streamlit as st
from supabase import create_client, Client

SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Variáveis de ambiente do Supabase não encontradas. Configure o arquivo secrets.toml ou variáveis de ambiente.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --------------------------
# PONTOS
# --------------------------
def listar_pontos():
    """Retorna lista com todos os pontos cadastrados."""
    try:
        resp = supabase.table("tbl_pontos").select("*").execute()
        return resp.data or []
    except Exception as e:
        raise RuntimeError(f"Erro ao listar pontos: {e}")

def inserir_ponto(dados: dict):
    """Insere um novo ponto no banco."""
    try:
        resp = supabase.table("tbl_pontos").insert(dados).execute()
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Erro ao inserir ponto: {e}")

def atualizar_ponto(id_ponto, novos_dados: dict):
    """Atualiza um ponto existente pelo id."""
    try:
        resp = supabase.table("tbl_pontos").update(novos_dados).eq("id", id_ponto).execute()
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Erro ao atualizar ponto: {e}")

def deletar_ponto(id_ponto):
    """Exclui um ponto pelo id."""
    try:
        resp = supabase.table("tbl_pontos").delete().eq("id", id_ponto).execute()
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Erro ao deletar ponto: {e}")

# --------------------------
# USUÁRIOS
# --------------------------
def buscar_usuario_por_email(email: str):
    """Busca um usuário pelo e-mail."""
    try:
        resp = supabase.table("tbl_usuarios").select("*").eq("email", email).execute()
        return resp.data[0] if resp.data else None
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar usuário: {e}")

def inserir_usuario(dados: dict):
    """Insere um novo usuário na tabela de usuários."""
    try:
        resp = supabase.table("tbl_usuarios").insert(dados).execute()
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Erro ao inserir usuário: {e}")

def atualizar_usuario(email: str, dados: dict):
    """Atualiza os dados de um usuário pelo e-mail."""
    try:
        resp = supabase.table("tbl_usuarios").update(dados).eq("email", email).execute()
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Erro ao atualizar usuário: {e}")

def deletar_usuario(email: str):
    """Remove um usuário pelo e-mail."""
    try:
        resp = supabase.table("tbl_usuarios").delete().eq("email", email).execute()
        return resp.data
    except Exception as e:
        raise RuntimeError(f"Erro ao deletar usuário: {e}")

# --------------------------
# MUNICÍPIOS
# --------------------------
def carregar_estados():
    try:
        resp = supabase.table("estados_unicos").select("*").execute()
        data = resp.data or []
        estados = sorted({(d.get("name_state") or "").strip() for d in data if d.get("name_state")})
        return estados
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar estados da view: {e}")



def carregar_municipios(estado: str = None):
    """
    Retorna municípios.
    - Se 'estado' for None → retorna todos.
    - Se 'estado' for string → retorna só do estado.
    """
    try:
        query = supabase.table("tbl_municipiosbr") \
                        .select("name_state, code_muni, name_muni, name_intermmediate, name_immediate")

        if estado:
            query = query.eq("name_state", estado.strip())

        resp = query.execute()
        return resp.data or []
    except Exception as e:
        raise RuntimeError(f"Erro ao carregar municípios: {e}")