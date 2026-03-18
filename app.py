import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(
    page_title="Dashboard Materiais - Confiabilidade",
    page_icon="⚙️",
    layout="wide"
)

# ==========================================
# PREPARAÇÃO PARA DADOS REAIS
# ==========================================
@st.cache_data
def carregar_dados():
    # ----------------------------------------
    # DADOS 1.1: Equipamentos Críticos
    # ----------------------------------------
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

    # ----------------------------------------
    # DADOS 1.2: PDM DE MATERIAIS
    # ----------------------------------------
    dados_pdm_mensal = pd.DataFrame({
        'MÊS': ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO'],
        'Planejado Mês': [0, 400, 500, 550, 650, 650, 650, 500, 450, 350, 300],
        'Planejado Acum.': [0, 400, 900, 1450, 2100, 2750, 3400, 3900, 4350, 4700, 5000],
        'Realizado Mês': [0, 400, None, None, None, None, None, None, None, None, None],
        'Realizado Acum.': [0, 400, None, None, None, None, None, None, None, None, None],
        '% Concluído do Projeto': ['0%', '8%', None, None, None, None, None, None, None, None, None],
        'GAP (Desvio Acumulado)': [0, 0, None, None, None, None, None, None, None, None, None]
    })
    
    dados_pdm_diario = pd.DataFrame({
        'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'],
        'Realizado': [120, 145, 130, 160, 155],
        'Meta': [150, 150, 150, 150, 150]
    })
    
    # ----------------------------------------
    # DADOS 1.3: Barreiras
    # ----------------------------------------
    dados_barreiras = pd.DataFrame({
        'Status': ['Cadastrados/Revisados', 'Pendentes'],
        'Quantidade': [2100, 4900]
    })

    # ----------------------------------------
    # DADOS 3: Kanban (Demandas Ad-hoc)
    # ----------------------------------------
    dados_kanban = pd.DataFrame({
        'Tarefa': ['Análise de Válvula Urgente (Plataforma X)', 'Revisão LTM Bomba Y', 'Cotação Emergencial Selo Mecânico', 'Saneamento Código Duplicado (Solic. Operação)'],
        'Solicitante': ['Manutenção', 'Engenharia', 'Suprimentos', 'Operação'],
        'Prioridade': ['Alta 🔴', 'Média 🟡', 'Alta 🔴', 'Baixa 🟢'],
        'Status': ['Em Andamento', 'A Fazer', 'Concluído', 'Em Andamento']
    })
    
    return dados_cronograma, dados_curva_s_eqp, dados_pdm_mensal, dados_pdm_diario, dados_barreiras, dados_kanban

df_crono, df_curva_eqp, df_pdm_mensal, df_pdm_diario, df_barreiras, df_kanban = carregar_dados()

def colorir_status_crono(val):
    if val == 'CONCLUIDO': return 'background-color: #00cc96; color: black'
    elif val == 'EM ANDAMENTO': return 'background-color: #ffffcc; color: black'
    elif val == 'PENDENTE': return 'background-color: #ffcccb; color: black'
    return ''

df_pdm_mensal_display = df_pdm_mensal.fillna('-')

# ==========================================
# MENU LATERAL (FILTROS)
# ==========================================
with st.sidebar:
    st.header("🔍 Filtros de Análise")
    mes_filtro = st.selectbox("Selecione o Mês", ["Todos", "Janeiro", "Fevereiro", "Março"])
    frota_filtro = st.selectbox("Selecione a Frota", ["Todas", "Peregrino", "Frota Antiga"])
    st.divider()

# ==========================================
# CABEÇALHO PRINCIPAL
# ==========================================
st.title("⚙️ Dashboard de Gestão de Materiais")
st.markdown("Acompanhamento de Sobressalentes, Metas de Equipamentos Críticos e Rotinas da Equipe.")
st.divider()

# ==========================================
# SEÇÃO 1: METAS DO ANO
# ==========================================
st.header("🎯 1. Metas do Ano")

# --- 1.1 Cronograma de Equipamentos Críticos ---
st.subheader("1.1 Equip. Críticos (Peregrino)")

col_graf1, col_graf2 = st.columns([2, 1])
with col_graf1:
    st.markdown("**Curva S - Avanço Físico do Projeto**")
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(x=df_curva_eqp['Mês'], y=df_curva_eqp['Planejado Acumulado (%)'], mode='lines+markers', name='Planejado', line=dict(color='gray', dash='dash')))
    fig_curva.add_trace(go.Scatter(x=df_curva_eqp['Mês'], y=df_curva_eqp['Realizado Acumulado (%)'], mode='lines+markers', name='Realizado', line=dict(color='#00cc96', width=3)))
    fig_curva.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="% de Avanço", showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig_curva, use_container_width=True)

with col_graf2:
    st.markdown("**Avanço Total Consolidado**")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number", value = 16.5, number = {"suffix": "%"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#2b8cbe"},
                 'steps': [{'range': [0, 30], 'color': "#ffcccb"}, {'range': [30, 80], 'color': "#ffffcc"}, {'range': [80, 100], 'color': "#e0ffe0"}]}
    ))
    fig_gauge.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

st.markdown("**Status do Cronograma de Verificação de Documentações**")
st.dataframe(df_crono.style.applymap(colorir_status_crono, subset=['STATUS DA ATIVIDADE']), use_container_width=True, hide_index=True, height=420)
st.divider()

# --- 1.2 PDM de Materiais ---
st.subheader("1.2 PDM de Materiais")

col_pdm_1, col_pdm_2 = st.columns([2, 1])
with col_pdm_1:
    st.markdown("**Curva S - Avanço Acumulado do PDM**")
    fig_curva_pdm = go.Figure()
    fig_curva_pdm.add_trace(go.Scatter(x=df_pdm_mensal['MÊS'], y=df_pdm_mensal['Planejado Acum.'], mode='lines+markers', name='Planejado Acum.', line=dict(color='gray', dash='dash')))
    fig_curva_pdm.add_trace(go.Scatter(x=df_pdm_mensal['MÊS'], y=df_pdm_mensal['Realizado Acum.'], mode='lines+markers', name='Realizado Acum.', line=dict(color='#636efa', width=3)))
    fig_curva_pdm.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Quantitativo de Materiais", showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig_curva_pdm, use_container_width=True)

with col_pdm_2:
    st.markdown("**Avanço Total Consolidado**")
    fig_gauge_pdm = go.Figure(go.Indicator(
        mode = "gauge+number", value = 8, number = {"suffix": "%"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#636efa"},
                 'steps': [{'range': [0, 30], 'color': "#ffcccb"}, {'range': [30, 80], 'color': "#ffffcc"}, {'range': [80, 100], 'color': "#e0ffe0"}]}
    ))
    fig_gauge_pdm.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_gauge_pdm, use_container_width=True)

st.markdown("**Tabela de Controle Mensal - PDM de Materiais**")
st.dataframe(df_pdm_mensal_display, use_container_width=True, hide_index=True)

st.markdown("**Acompanhamento Diário D-1 (Ritmo da Contratada)**")
fig_pdm_diario = go.Figure()
fig_pdm_diario.add_trace(go.Bar(x=df_pdm_diario['Dia'], y=df_pdm_diario['Realizado'], name='Realizado Dia', marker_color='#636efa'))
fig_pdm_diario.add_trace(go.Scatter(x=df_pdm_diario['Dia'], y=df_pdm_diario['Meta'], name='Meta Diária', line=dict(color='red', width=2)))
fig_pdm_diario.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(yanchor="top", y=1.2, xanchor="left", x=0))
st.plotly_chart(fig_pdm_diario, use_container_width=True)
st.divider()

# --- 1.3 Cronograma de Barreiras de Segurança ---
st.subheader("1.3 Barreiras (Frota Antiga)")
col_13_A, col_13_B = st.columns([1, 2])
with col_13_A:
    fig_donut = px.pie(df_barreiras, values='Quantidade', names='Status', hole=0.6, color_discrete_sequence=['#19d3f3', '#ef553b'])
    fig_donut.update_traces(textinfo='value+percent')
    fig_donut.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)

with col_13_B:
    st.info("💡 **Espaço Reservado:** Tabela ou Gráficos de Barreiras de Segurança.")
st.divider()

# ==========================================
# SEÇÃO 2: ROTINAS (DIÁRIAS E SEMANAIS)
# ==========================================
st.header("📅 2. Rotinas Operacionais (SLA Semanal)")

r_col1, r_col2, r_col3, r_col4 = st.columns(4)

with r_col1:
    st.metric(label="2.1 MRP (3x/sem)", value="3/3", delta="No prazo", delta_color="normal")
    st.metric(label="2.5 Códigos '6' (2x/sem)", value="1/2", delta="-1 Pendente", delta_color="inverse")
with r_col2:
    st.metric(label="2.2 Portal Chamados (2x/sem)", value="2/2", delta="No prazo", delta_color="normal")
    st.metric(label="2.6 Duplicidade (2x/sem)", value="2/2", delta="No prazo", delta_color="normal")
with r_col3:
    st.metric(label="2.3 LTM's (2x/sem)", value="2/2", delta="No prazo", delta_color="normal")
    st.metric(label="2.7 Primarização (1x/sem)", value="0/1", delta="-1 Pendente", delta_color="inverse")
with r_col4:
    st.info("**2.4 Lev. Técnico de Campo**\n\nConsolidado de hoje: Realizado.")
st.divider()

# ==========================================
# SEÇÃO 3: DEMANDAS FORA DO ESCOPO (KANBAN)
# ==========================================
st.header("🗂️ 3. Solicitações Fora do Escopo (Ad-hoc)")
st.markdown("Acompanhamento de demandas extras absorvidas pela equipe (Estilo Quadro Kanban).")

# Criando as 3 colunas do Trello
k_col1, k_col2, k_col3 = st.columns(3)

# Função auxiliar para desenhar os "Cartões"
def criar_cartao(tarefa, solicitante, prioridade):
    with st.container(border=True): # Isso cria o contorno do "Card"
        st.markdown(f"**{tarefa}**")
        st.caption(f"👤 Solicitante: {solicitante}")
        st.caption(f"🏷️ Prioridade: {prioridade}")

# Desenhando os cartões na coluna "A Fazer"
with k_col1:
    st.subheader("📋 A Fazer")
    df_todo = df_kanban[df_kanban['Status'] == 'A Fazer']
    for index, row in df_todo.iterrows():
        criar_cartao(row['Tarefa'], row['Solicitante'], row['Prioridade'])

# Desenhando os cartões na coluna "Em Andamento"
with k_col2:
    st.subheader("⏳ Em Andamento")
    df_doing = df_kanban[df_kanban['Status'] == 'Em Andamento']
    for index, row in df_doing.iterrows():
        criar_cartao(row['Tarefa'], row['Solicitante'], row['Prioridade'])

# Desenhando os cartões na coluna "Concluído"
with k_col3:
    st.subheader("✅ Concluído")
    df_done = df_kanban[df_kanban['Status'] == 'Concluído']
    for index, row in df_done.iterrows():
        criar_cartao(row['Tarefa'], row['Solicitante'], row['Prioridade'])
