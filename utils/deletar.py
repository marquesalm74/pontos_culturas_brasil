import streamlit as st
from controllers.pontos_controller import PontosController

EMAILS_AUTORIZADOS = st.secrets["emails"]["autorizados"]

def deletar():
    st.title("Excluir Ponto")

    email_usuario = st.text_input("Digite seu e-mail para acessar a função de exclusão")
    if not email_usuario:
        st.info("Digite seu e-mail para continuar.")
        return

    if email_usuario.lower() not in [email.lower() for email in EMAILS_AUTORIZADOS]:
        st.warning("E-mail não autorizado para exclusão.")
        return

    st.success(f"Acesso liberado para o e-mail: {email_usuario}")

    id_sel = st.number_input("ID do registro a excluir", min_value=1, step=1)

    if st.button("Excluir registro"):
        if id_sel <= 0:
            st.warning("Digite um ID válido.")
            return
        try:
            PontosController.Deletar(int(id_sel))
            st.success(f"Registro com ID {id_sel} excluído com sucesso.")
            st.session_state.pop("df", None)
        except Exception as e:
            st.error(f"Erro ao excluir: {e}")

