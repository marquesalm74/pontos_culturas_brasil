# controllers/pontos_controller.py
from services import database as db

class PontosController:
    @staticmethod
    def SelecionarTodos():
        return db.listar_pontos()

    @staticmethod
    def Incluir(payload: dict):
        return db.inserir_ponto(payload)

    @staticmethod
    def Atualizar(id_ponto, novos_dados: dict):
        return db.atualizar_ponto(id_ponto, novos_dados)

    @staticmethod
    def Deletar(id_ponto):
        return db.deletar_ponto(id_ponto)
    
def SelecionarTodos():
    return db.listar_pontos()

def Atualizar(id_ponto, novos_dados: dict):
    return db.atualizar_ponto(id_ponto, novos_dados)


