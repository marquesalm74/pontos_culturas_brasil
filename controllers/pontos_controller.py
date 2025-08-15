# controllers/pontos_controller.py
from services import database as db

def SelecionarTodos():
    """Retorna lista de dicts dos pontos."""
    return db.listar_pontos()

def Incluir(payload: dict):
    """Insere novo ponto. payload: dict com chaves conforme tabela 'pontos'."""
    return db.inserir_ponto(payload)

def Atualizar(id_ponto, novos_dados: dict):
    return db.atualizar_ponto(id_ponto, novos_dados)

def Deletar(id_ponto):
    return db.deletar_ponto(id_ponto)
