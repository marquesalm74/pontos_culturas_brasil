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
    """
    Retorna lista de estados no formato:
    [{'code_state': '11', 'name_state': 'Rondônia', 'abbrev_state': 'RO'}, ...]
    """
    try:
        resp = supabase.table("tbl_estados").select(
            "code_state, name_state, abbrev_state"
        ).order("name_state").limit(None).execute()
        
        if resp.data:
            # Usar tuplas para garantir unicidade
            estados_unicos = {
                (str(e["code_state"]), e["name_state"], e["abbrev_state"])
                for e in resp.data
            }
            
            # Retornar lista ordenada pelo nome do estado
            return [
                {"code_state": e[0], "name_state": e[1], "abbrev_state": e[2]}
                for e in sorted(estados_unicos, key=lambda x: x[1])
            ]
        return []
    except Exception as e:
        print("Erro carregar_estados:", e)
        return []

############### Carrega os Municipios
# def carregar_municipios(code_state):
#     """
#     Retorna lista de municípios de um estado (filtra pelo code_state numérico)
#     """
#     try:
#         resp = supabase.table("tbl_municipiosbr").select(
#             ["code_state", "name_state", "abbrev_state", "code_muni", "name_muni"]
#         ).eq("code_state", code_state).order("name_muni").limit(None).execute()
        
#         if resp.data:
#             return resp.data
#         return []
#     except Exception as e:
#         print("Erro carregar_municipios:", e)
#         return []

def carregar_municipios(code_state):
    """
    Retorna lista de municípios de um estado (filtra pelo code_state como string)
    """
    try:
        code_state = str(code_state)  # garante que seja string simples
        resp = supabase.table("tbl_municipiosbr").select(
            "code_state, code_muni, name_muni"
        ).eq("code_state", code_state).order("name_muni").limit(None).execute()

        if resp.data:
            # Certifica que code_state e code_muni em cada registro são strings
            for m in resp.data:
                if isinstance(m.get("code_state"), list):
                    m["code_state"] = str(m["code_state"][0])
                if isinstance(m.get("code_muni"), list):
                    m["code_muni"] = str(m["code_muni"][0])
            return resp.data
        return []
    except Exception as e:
        print("Erro carregar_municipios:", e)
        return []
    
############### Limite dos Municipios    
def carregar_limite_municipio(code_muni):
    """Retorna WKT do município pelo código."""
    try:
        resp = supabase.table("tbl_municipiosbr").select("geom_wkt").eq("code_muni", code_muni).execute()
        return resp.data[0]["geom_wkt"] if resp.data else None
    except Exception as e:
        print("Erro carregar_limite_municipio:", e)
        return None