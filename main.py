import streamlit as st
import json
import os
from datetime import datetime

# Caminhos dos arquivos
USUARIOS_PATH = "dados/usuarios.json"
SERVICOS_PATH = "dados/servicos.json"

# ========== Funções Auxiliares ==========
def carregar_dados(caminho):
    if not os.path.exists(caminho):
        return []
    with open(caminho, "r") as f:
        return json.load(f)

def salvar_dados(caminho, dados):
    with open(caminho, "w") as f:
        json.dump(dados, f, indent=4)

def autenticar_usuario(email, senha, tipo):
    usuarios = carregar_dados(USUARIOS_PATH)
    for u in usuarios:
        if u["email"] == email and u["senha"] == senha and u["tipo"] == tipo:
            return u
    return None

def usuario_existe(email):
    usuarios = carregar_dados(USUARIOS_PATH)
    return any(u["email"] == email for u in usuarios)

# ========== INÍCIO DO APP ==========
st.set_page_config(page_title="Sat Track", layout="wide")
st.title("📡 Sat Track - Sistema de Instalações")

# ========== LOGIN OU CADASTRO ==========
modo = st.sidebar.radio("Escolha:", ["Login", "Cadastro"])
tipo_usuario = st.sidebar.selectbox("Você é:", ["Empresa", "Técnico"])

# Sessão de login
if modo == "Login":
    st.subheader("🔐 Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        usuario = autenticar_usuario(email, senha, tipo_usuario)
        if usuario:
            st.success(f"Bem-vindo, {usuario['nome']}!")
            st.session_state["usuario"] = usuario
        else:
            st.error("Email, senha ou tipo incorreto.")

# Sessão de cadastro
else:
    st.subheader("📝 Cadastro")
    nome = st.text_input("Nome Completo")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if tipo_usuario == "Empresa":
        cnpj = st.text_input("CNPJ")
        endereco = st.text_input("Endereço")
    else:
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        cidade = st.text_input("Cidade")
        endereco = st.text_input("Endereço de Partida")

    if st.button("Cadastrar"):
        if usuario_existe(email):
            st.warning("Já existe um usuário com esse e-mail.")
        else:
            novo_usuario = {
                "tipo": tipo_usuario,
                "nome": nome,
                "email": email,
                "senha": senha,
                "criado_em": str(datetime.now())
            }
            if tipo_usuario == "Empresa":
                novo_usuario.update({"cnpj": cnpj, "endereco": endereco})
            else:
                novo_usuario.update({
                    "cpf": cpf,
                    "telefone": telefone,
                    "cidade": cidade,
                    "endereco": endereco
                })
            usuarios = carregar_dados(USUARIOS_PATH)
            usuarios.append(novo_usuario)
            salvar_dados(USUARIOS_PATH, usuarios)
            st.success("Cadastro realizado com sucesso! Faça login para continuar.")

# ========== ÁREA LOGADA ==========
if "usuario" in st.session_state:
    user = st.session_state["usuario"]
    st.sidebar.success(f"Logado como: {user['nome']} ({user['tipo']})")

    if user["tipo"] == "Empresa":
        st.header("📄 Solicitação de Serviço")
        with st.form("form_empresa"):
            nome_cliente = st.text_input("Nome do Cliente")
            cpf_cliente = st.text_input("CPF do Cliente")
            modelo_carro = st.text_input("Modelo do Carro")
            placa = st.text_input("Placa do Veículo")
            endereco_instalacao = st.text_input("Endereço da Instalação")

            tipo_servico = st.selectbox("Tipo de Serviço", ["Instalação", "Manutenção", "Retirada"])
            data_inicio = st.date_input("Data Início")
            data_fim = st.date_input("Data Fim")
            horario = st.text_input("Horário (Ex: 08:00 às 18:00)")

            submit = st.form_submit_button("Enviar Solicitação")
            if submit:
                novo_servico = {
                    "empresa": user["nome"],
                    "empresa_email": user["email"],
                    "cliente": nome_cliente,
                    "cpf_cliente": cpf_cliente,
                    "modelo": modelo_carro,
                    "placa": placa,
                    "endereco_instalacao": endereco_instalacao,
                    "tipo": tipo_servico,
                    "data_inicio": str(data_inicio),
                    "data_fim": str(data_fim),
                    "horario": horario,
                    "status": "Aguardando técnico",
                    "resposta_tecnico": None,
                    "data_envio": str(datetime.now())
                }
                servicos = carregar_dados(SERVICOS_PATH)
                servicos.append(novo_servico)
                salvar_dados(SERVICOS_PATH, servicos)
                st.success("Solicitação enviada com sucesso!")

    elif user["tipo"] == "Técnico":
        st.header("🛠️ Solicitações Disponíveis")
        servicos = carregar_dados(SERVICOS_PATH)
        pendentes = [s for s in servicos if s["status"] == "Aguardando técnico"]

        if pendentes:
            for i, s in enumerate(pendentes):
                with st.expander(f"{s['tipo']} - {s['placa']} ({s['cliente']})"):
                    st.write(f"📍 Local: {s['endereco_instalacao']}")
                    st.write(f"📆 Período: {s['data_inicio']} a {s['data_fim']} | {s['horario']}")
                    st.write(f"🚗 Veículo: {s['modelo']}")
                    if st.button(f"Aceitar solicitação #{i+1}"):
                        s["status"] = "Aguardando aprovação da empresa"
                        s["resposta_tecnico"] = f"Aceito por {user['nome']} em {str(datetime.now())}"
                        salvar_dados(SERVICOS_PATH, servicos)
                        st.success("Solicitação aceita!")
        else:
            st.info("Nenhuma solicitação pendente no momento.")
