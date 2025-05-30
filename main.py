import streamlit as st
import json
import os
from datetime import datetime

# Caminho do arquivo de dados
DB_PATH = "dados/servicos.json"

# Funções auxiliares
def carregar_servicos():
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r") as f:
        return json.load(f)

def salvar_servico(servico):
    servicos = carregar_servicos()
    servicos.append(servico)
    with open(DB_PATH, "w") as f:
        json.dump(servicos, f, indent=4)

def atualizar_servicos(servicos):
    with open(DB_PATH, "w") as f:
        json.dump(servicos, f, indent=4)

# Interface
st.set_page_config(page_title="Sat Track", layout="wide")
st.title("📡 Sat Track - Sistema de Instalações")

menu = st.sidebar.selectbox("Escolha sua função:", ["Empresa", "Técnico"])

if menu == "Empresa":
    st.header("📄 Solicitação de Serviço")
    with st.form("form_empresa"):
        nome_empresa = st.text_input("Nome da Empresa")
        cnpj = st.text_input("CNPJ")
        endereco_empresa = st.text_input("Endereço da Empresa")

        st.subheader("📋 Dados do Cliente")
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
                "empresa": nome_empresa,
                "cnpj": cnpj,
                "endereco_empresa": endereco_empresa,
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
            salvar_servico(novo_servico)
            st.success("Solicitação enviada com sucesso!")

elif menu == "Técnico":
    st.header("🛠️ Solicitações Disponíveis")
    servicos = carregar_servicos()
    pendentes = [s for s in servicos if s["status"] == "Aguardando técnico"]

    if pendentes:
        for i, s in enumerate(pendentes):
            with st.expander(f"{s['tipo']} - {s['placa']} ({s['cliente']})"):
                st.write(f"📍 Local: {s['endereco_instalacao']}")
                st.write(f"📆 Período: {s['data_inicio']} a {s['data_fim']} | {s['horario']}")
                st.write(f"🚗 Veículo: {s['modelo']}")
                if st.button(f"Aceitar solicitação #{i+1}"):
                    s["status"] = "Aguardando aprovação da empresa"
                    s["resposta_tecnico"] = f"Técnico aceitou em {str(datetime.now())}"
                    atualizar_servicos(servicos)
                    st.success("Você aceitou essa solicitação.")
    else:
        st.info("Nenhuma solicitação pendente no momento.")
