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
    # Dados 1.1: Tabela de Equipamentos Críticos (Baseado na sua imagem)
    dados_cronograma = pd.DataFrame({
        'EQUIPAMENTO': ['ORG. PORTAL', 'ORG. DOCUMENTAÇÃO', 'BOMBA DE INCENDIO', 'TURBINAS + PACOTE', 'COMPRESSORES DE AR', 'VALVULAS CRITICAS', 'BALEEIRAS / TURCOS', 'BOMBAS INJEÇÃO', 'GUINDASTE', 'UPS + DETECTORES', 'GERADOR DE EMERGENCIA'],
        'INICIO': ['01/01/26', '01/01/26', '05/01/26', '05/01/26', '31/03/26', '06/04/26', '29/05/26', '06/07/26', '11/08/26', '11/08/26', '10/09/26'],
        'FIM': ['15/01/26', '05/02/26', '16/03/26', '05/04/26', '29/05/26', '05/07/26', '07/08/26', '04/09/26', '30/10/26', '09/11/26', '09/11/26'],
        '% PLAN.': ['2%', '5%', '10%', '13%', '9%', '13%', '10%', '9%', '12%', '13%', '9%'],
        '% REAL.': ['2%', '5%', '9%', '0.5%', '-', '-', '-', '-', '-', '-', '-'],
        'STATUS': ['CONCLUIDO', 'CONCLUIDO', 'CONCLUIDO', 'EM ANDAMENTO', 'PENDENTE', 'PENDENTE', 'PENDENTE', 'PENDENTE', 'PENDENTE', 'PENDENTE', 'PENDENTE']
    })

    # Dados 1.1: Dados para a Curva S (Avanço Acumulado Fictício baseado na sua tabela)
    dados_curva_s = pd.DataFrame({
        'Mês': ['Jan/26', 'Fev/26', 'Mar/26', 'Abr/26', 'Mai/26', 'Jun/26', 'Jul/26', 'Ago/26', 'Set/26', 'Out/26', 'Nov/26'],
        'Planejado Acumulado (%)': [2, 7, 17, 30, 39, 52, 62, 71, 83, 96, 100],
        'Realizado Acumulado (%)': [2, 7, 16.5, None, None, None, None, None, None, None, None] # Preenchido até o momento atual
    })

    # Dados 1.2
    dados_pdm = pd.DataFrame({
        'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'],
        'Realizado': [120, 145, 130, 160, 155],
        'Meta': [150, 150, 150, 150, 150]
    })
    
    # Dados 1.3
    dados_barreiras = pd.DataFrame({
        'Status': ['Cadastrados/Revisados', 'Pendentes'],
        'Quantidade': [2100, 4900]
    })
    
    return dados_cronograma, dados_curva_s, dados_pdm, dados_barreiras

df_crono, df_curva, df_pdm, df_barreiras = carregar_dados()

# Função para colorir o status na tabela do Streamlit
def colorir_status(val):
    if val == 'CONCLUIDO': return 'background-color: #00cc96; color: black'
    elif val == 'EM ANDAMENTO': return 'background-color: #ffffcc; color: black'
    elif val == 'PENDENTE': return 'background-color: #ffcccb; color: black'
    return ''

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

# Ajuste das colunas: A (Tabela e Curva S na esquerda - maior) e B (Gauge na direita - menor)
col_11_A, col_11_B = st.columns([2.5, 1]) 

with col_11_A:
    st.markdown("**Status do Cronograma de Verificação de Documentações**")
    # Aplica as cores na tabela e exibe
    st.dataframe(df_crono.style.applymap(colorir_status, subset=['STATUS']), use_container_width=True, hide_index=True)
    
    st.markdown("**Curva S - Avanço Físico do Projeto**")
    # Criação do Gráfico Curva S
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(x=df_curva['Mês'], y=df_curva['Planejado Acumulado (%)'], mode='lines+markers', name='Planejado', line=dict(color='gray', dash='dash')))
    fig_curva.add_trace(go.Scatter(x=df_curva['Mês'], y=df_curva['Realizado Acumulado (%)'], mode='lines+markers', name='Realizado', line=dict(color='#00cc96', width=3)))
    fig_curva.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="% de Avanço", showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig_curva, use_container_width=True)

with col_11_B:
    st.markdown("**Avanço Total Consolidado**")
    # Atualizei o valor do Gauge para 16.5% para refletir os dados reais da sua tabela (2+5+9+0.5)
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 16.5, 
        number = {"suffix": "%"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#2b8cbe"},
            'steps': [
                {'range': [0, 30], 'color': "#ffcccb"},
                {'range': [30, 80], 'color': "#ffffcc"},
                {'range': [80, 100], 'color': "#e0ffe0"}
            ]
        }
    ))
    fig_gauge.update_layout(height=350, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

st.divider()

# --- 1.2 PDM de Materiais ---
st.subheader("1.2 PDM de Materiais")
col_12_A, col_12_B = st.columns([2, 1])

with col_12_A:
    fig_pdm = go.Figure()
    fig_pdm.add_trace(go.Bar(x=df_pdm['Dia'], y=df_pdm['Realizado'], name='Realizado', marker_color='#636efa'))
    fig_pdm.add_trace(go.Scatter(x=df_pdm['Dia'], y=df_pdm['Meta'], name='Meta Diária', line=dict(color='red', width=2)))
    fig_pdm.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(yanchor="top", y=1.2, xanchor="left", x=0))
    st.plotly_chart(fig_pdm, use_container_width=True)

with col_12_B:
    st.info("💡 **Espaço Reservado:** PDM.")

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
    st.info("💡 **Espaço Reservado:** Barreiras.")

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
