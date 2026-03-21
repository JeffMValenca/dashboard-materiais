import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E CONEXÃO GOOGLE
# ==========================================
st.set_page_config(
    page_title="Dashboard Materiais - Confiabilidade",
    page_icon="⚙️",
    layout="wide"
)

LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/17HqIfoMCwkrXgfRPNNpwJBvWrPt71e-yM_oZVCdxaf8"

@st.cache_resource
def conectar_google_sheets():
    try:
        # Puxa o "crachá" que você guardou no cofre do Streamlit
        creds_json = st.secrets["google_credentials"]
        creds_dict = json.loads(creds_json)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"⚠️ Erro na conexão com o Google. Verifique os Secrets. Detalhe: {e}")
        return None

# ==========================================
# 2. FUNÇÕES PARA LER E ESCREVER NO KANBAN
# ==========================================
def carregar_kanban():
    client = conectar_google_sheets()
    if client:
        try:
            planilha = client.open_by_url(LINK_PLANILHA).worksheet("Kanban")
            dados = planilha.get_all_records()
            if not dados:
                return pd.DataFrame(columns=["ID", "Tarefa", "Solicitante", "Prioridade", "Status"])
            return pd.DataFrame(dados)
        except Exception as e:
            st.error(f"Erro ao ler a aba 'Kanban' na planilha. Garanta que ela se chama 'Kanban'. Detalhe: {e}")
    return pd.DataFrame(columns=["ID", "Tarefa", "Solicitante", "Prioridade", "Status"])

def adicionar_tarefa_planilha(id_tarefa, tarefa, solicitante, prioridade, status):
    client = conectar_google_sheets()
    if client:
        planilha = client.open_by_url(LINK_PLANILHA).worksheet("Kanban")
        planilha.append_row([id_tarefa, tarefa, solicitante, prioridade, status])

def atualizar_status_planilha(id_tarefa, novo_status):
    client = conectar_google_sheets()
    if client:
        planilha = client.open_by_url(LINK_PLANILHA).worksheet("Kanban")
        registros = planilha.get_all_records()
        for i, linha in enumerate(registros):
            if str(linha['ID']) == str(id_tarefa):
                planilha.update_cell(i + 2, 5, novo_status) # Coluna 5 é o Status (E)
                break

def deletar_tarefa_planilha(id_tarefa):
    client = conectar_google_sheets()
    if client:
        planilha = client.open_by_url(LINK_PLANILHA).worksheet("Kanban")
        registros = planilha.get_all_records()
        for i, linha in enumerate(registros):
            if str(linha['ID']) == str(id_tarefa):
                planilha.delete_rows(i + 2)
                break

# ==========================================
# 3. PREPARAÇÃO PARA DADOS FIXOS (METAS)
# ==========================================
@st.cache_data
def carregar_dados_fixos():
    dados_cronograma = pd.DataFrame({
        'TIPO': ['DOCUMENTAÇÃO', 'DOCUMENTAÇÃO', 'EQUIPAMENTO', 'EQUIPAMENTO', 'EQUIPAMENTO', 'EQUIPAMENTO', 'EQUIPAMENTO', 'EQUIPAMENTO', 'EQUIPAMENTO', 'EQUIPAMENTO', 'EQUIPAMENTO'],
        'EQUIPAMENTO': ['ORGANIZAÇÃO PORTAL', 'ORGANIZAÇÃO DA DOCUMENTAÇÃO', 'BOMBA DE INCENDIO', 'TURBINAS + PACOTE', 'COMPRESSORES DE AR', 'VALVULAS CRITICAS', 'BALEEIRAS / TURCOS', 'BOMBAS INJEÇÃO', 'GUINDASTE', 'UPS + DETECTORES', 'GERADOR DE EMERGENCIA'],
        'INICIO': ['01/01/2026', '01/01/2026', '05/01/2026', '05/01/2026', '31/03/2026', '06/04/2026', '29/05/2026', '06/07/2026', '11/08/2026', '11/08/2026', '10/09/2026'],
        'FIM': ['15/01/2026', '05/02/2026', '16/03/2026', '05/04/2026', '29/05/2026', '05/07/2026', '07/08/2026', '04/09/2026', '30/10/2026', '09/11/2026', '09/11/2026'],
        'FIM REAL': ['15/01/2026', '05/02/2026', '20/02/2026', 'EM ANDAMENTO', '-', '-', '-', '-', '-', '-', '-'],
        'TOTAL DE DIAS': [14, 35, 70, 90, 59, 90, 70, 60, 80, 90, 60],
        '% PLANEJADO': ['2%', '5%', '10%', '13%', '9%', '13%', '10%', '9%', '12%', '13%', '9%'],
        '% REALIZADO': ['2%', '5%', '9%', '-', '-', '-', '-', '-', '-', '-', '-'],
        'TOTAL DE DOCUMENTOS': ['0', '0', '1846', '2450', '-', '-', '-', '-', '-', '-', '-'],
        'Doc. Já Analisados': ['0', '0', '1846', '100', '-', '-', '-', '-', '-', '-', '-'],
        'STATUS DA ATIVIDADE': ['CONCLUIDO', 'CONCLUIDO', 'CONCLUIDO', 'EM ANDAMENTO', 'PENDENTE', 'PENDENTE', 'PENDENTE', 'PENDENTE', 'PENDENTE', 'PENDENTE', 'PENDENTE']
    })

    dados_curva_s_eqp = pd.DataFrame({
        'Mês': ['Jan/26', 'Fev/26', 'Mar/26', 'Abr/26', 'Mai/26', 'Jun/26', 'Jul/26', 'Ago/26', 'Set/26', 'Out/26', 'Nov/26'],
        'Planejado Acumulado (%)': [2, 7, 17, 30, 39, 52, 62, 71, 83, 96, 100],
        'Realizado Acumulado (%)': [2, 7, 16.5, None, None, None, None, None, None, None, None] 
    })

    dados_pdm_mensal = pd.DataFrame({
        'MÊS': ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO'],
        'Planejado Mês': [0, 400, 500, 550, 650, 650, 650, 500, 450, 350, 300],
        'Planejado Acum.': [0, 400, 900, 1450, 2100, 2750, 3400, 3900, 4350, 4700, 5000],
        'Realizado Mês': [0, 400, None, None, None, None, None, None, None, None, None],
        'Realizado Acum.': [0, 400, None, None, None, None, None, None, None, None, None],
        '% Concluído do Projeto': ['0%', '8%', None, None, None, None, None, None, None, None, None]
    })
    
    dados_pdm_diario = pd.DataFrame({
        'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'],
        'Realizado': [120, 145, 130, 160, 155],
        'Meta': [150, 150, 150, 150, 150]
    })
    
    dados_barreiras = pd.DataFrame({
        'Status': ['Cadastrados/Revisados', 'Pendentes'],
        'Quantidade': [2100, 4900]
    })

    return dados_cronograma, dados_curva_s_eqp, dados_pdm_mensal, dados_pdm_diario, dados_barreiras

df_crono, df_curva_eqp, df_pdm_mensal, df_pdm_diario, df_barreiras = carregar_dados_fixos()

def colorir_status_crono(val):
    if val == 'CONCLUIDO': return 'background-color: #00cc96; color: black'
    elif val == 'EM ANDAMENTO': return 'background-color: #ffffcc; color: black'
    elif val == 'PENDENTE': return 'background-color: #ffcccb; color: black'
    return ''

# ==========================================
# 4. INTERFACE DO DASHBOARD
# ==========================================
with st.sidebar:
    st.header("🔍 Filtros de Análise")
    mes_filtro = st.selectbox("Selecione o Mês", ["Todos", "Janeiro", "Fevereiro", "Março"])
    frota_filtro = st.selectbox("Selecione a Frota", ["Todas", "Peregrino", "Frota Antiga"])
    st.divider()

st.title("⚙️ Dashboard de Gestão de Materiais")
st.markdown("Acompanhamento de Sobressalentes, Metas de Equipamentos Críticos e Rotinas da Equipe.")
st.divider()

# --- SEÇÃO 1 e 2 (Metas e Rotinas) ---
st.header("🎯 1. Metas do Ano")

st.subheader("1.1 Equip. Críticos (Peregrino)")
col_graf1, col_graf2 = st.columns([2, 1])
with col_graf1:
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(x=df_curva_eqp['Mês'], y=df_curva_eqp['Planejado Acumulado (%)'], mode='lines+markers', name='Planejado', line=dict(color='gray', dash='dash')))
    fig_curva.add_trace(go.Scatter(x=df_curva_eqp['Mês'], y=df_curva_eqp['Realizado Acumulado (%)'], mode='lines+markers', name='Realizado', line=dict(color='#00cc96', width=3)))
    fig_curva.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig_curva, use_container_width=True)

with col_graf2:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = 16.5, number = {"suffix": "%"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#2b8cbe"},
                 'steps': [{'range': [0, 30], 'color': "#ffcccb"}, {'range': [30, 80], 'color': "#ffffcc"}, {'range': [80, 100], 'color': "#e0ffe0"}]}
    ))
    fig_gauge.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

st.dataframe(df_crono.style.applymap(colorir_status_crono, subset=['STATUS DA ATIVIDADE']), use_container_width=True, hide_index=True, height=420)
st.divider()

st.subheader("1.2 PDM de Materiais")
col_pdm_1, col_pdm_2 = st.columns([2, 1])
with col_pdm_1:
    fig_curva_pdm = go.Figure()
    fig_curva_pdm.add_trace(go.Scatter(x=df_pdm_mensal['MÊS'], y=df_pdm_mensal['Planejado Acum.'], mode='lines+markers', name='Planejado Acum.', line=dict(color='gray', dash='dash')))
    fig_curva_pdm.add_trace(go.Scatter(x=df_pdm_mensal['MÊS'], y=df_pdm_mensal['Realizado Acum.'], mode='lines+markers', name='Realizado Acum.', line=dict(color='#636efa', width=3)))
    fig_curva_pdm.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig_curva_pdm, use_container_width=True)

with col_pdm_2:
    fig_gauge_pdm = go.Figure(go.Indicator(
        mode = "gauge+number", value = 8, number = {"suffix": "%"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#636efa"},
                 'steps': [{'range': [0, 30], 'color': "#ffcccb"}, {'range': [30, 80], 'color': "#ffffcc"}, {'range': [80, 100], 'color': "#e0ffe0"}]}
    ))
    fig_gauge_pdm.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_gauge_pdm, use_container_width=True)

st.dataframe(df_pdm_mensal.fillna('-'), use_container_width=True, hide_index=True)
st.divider()

st.subheader("1.3 Barreiras (Frota Antiga)")
col_13_A, col_13_B = st.columns([1, 2])
with col_13_A:
    fig_donut = px.pie(df_barreiras, values='Quantidade', names='Status', hole=0.6, color_discrete_sequence=['#19d3f3', '#ef553b'])
    fig_donut.update_traces(textinfo='value+percent')
    fig_donut.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)
with col_13_B:
    st.info("💡 Espaço Reservado: Tabela ou Gráficos de Barreiras de Segurança.")
st.divider()

st.header("📅 2. Rotinas Operacionais (SLA Semanal)")
r_col1, r_col2, r_col3, r_col4 = st.columns(4)
with r_col1:
    st.metric(label="2.1 MRP", value="3/3", delta="No prazo")
with r_col2:
    st.metric(label="2.2 Chamados", value="2/2", delta="No prazo")
with r_col3:
    st.metric(label="2.3 LTM's", value="2/2", delta="No prazo")
with r_col4:
    st.metric(label="2.5 Códigos 6", value="1/2", delta="-1 Pendente", delta_color="inverse")
st.divider()

# ==========================================
# 5. SEÇÃO 3: KANBAN LIGADO AO GOOGLE SHEETS
# ==========================================
st.header("🗂️ 3. Solicitações Fora do Escopo (Ad-hoc)")
st.markdown("Demandas extras da equipe vinculadas diretamente ao seu Google Sheets.")

# Puxa os dados atualizados da planilha
df_kanban = carregar_kanban()

# Descobre qual o próximo ID disponível (para não sobrescrever)
if not df_kanban.empty and "ID" in df_kanban.columns and pd.to_numeric(df_kanban["ID"], errors="coerce").notnull().any():
    prox_id = int(pd.to_numeric(df_kanban["ID"], errors="coerce").max()) + 1
else:
    prox_id = 1

# Formulário para adicionar nova tarefa
with st.expander("➕ Adicionar Nova Solicitação", expanded=False):
    with st.form("form_nova_tarefa", clear_on_submit=True):
        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
        with f_col1:
            nova_desc = st.text_input("Descrição da Tarefa*")
        with f_col2:
            novo_solic = st.text_input("Solicitante")
        with f_col3:
            nova_prior = st.selectbox("Prioridade", ['Baixa 🟢', 'Média 🟡', 'Alta 🔴'])
        
        btn_salvar = st.form_submit_button("Salvar")
        if btn_salvar and nova_desc:
            adicionar_tarefa_planilha(prox_id, nova_desc, novo_solic, nova_prior, 'A Fazer')
            st.rerun() # Recarrega a página para puxar a nova linha da planilha

# Construindo as colunas do Kanban
k_col1, k_col2, k_col3 = st.columns(3)

def desenhar_cartao(linha, ant_status, prox_status):
    with st.container(border=True):
        st.markdown(f"**{linha['Tarefa']}**")
        st.caption(f"👤 {linha['Solicitante']} | {linha['Prioridade']}")
        
        b1, b2, b3 = st.columns(3)
        with b1:
            if ant_status and st.button("⏪", key=f"voltar_{linha['ID']}", help="Mover para trás"):
                atualizar_status_planilha(linha['ID'], ant_status)
                st.rerun()
        with b2:
            if st.button("❌", key=f"del_{linha['ID']}", help="Excluir tarefa"):
                deletar_tarefa_planilha(linha['ID'])
                st.rerun()
        with b3:
            if prox_status and st.button("⏩", key=f"avancar_{linha['ID']}", help="Avançar tarefa"):
                atualizar_status_planilha(linha['ID'], prox_status)
                st.rerun()

# Preenchendo a coluna A Fazer
with k_col1:
    st.subheader("📋 A Fazer")
    if not df_kanban.empty:
        df_todo = df_kanban[df_kanban['Status'] == 'A Fazer']
        for index, linha in df_todo.iterrows():
            desenhar_cartao(linha, None, 'Em Andamento')

# Preenchendo a coluna Em Andamento
with k_col2:
    st.subheader("⏳ Em Andamento")
    if not df_kanban.empty:
        df_doing = df_kanban[df_kanban['Status'] == 'Em Andamento']
        for index, linha in df_doing.iterrows():
            desenhar_cartao(linha, 'A Fazer', 'Concluído')

# Preenchendo a coluna Concluído
with k_col3:
    st.subheader("✅ Concluído")
    if not df_kanban.empty:
        df_done = df_kanban[df_kanban['Status'] == 'Concluído']
        for index, linha in df_done.iterrows():
            desenhar_cartao(linha, 'Em Andamento', None)
