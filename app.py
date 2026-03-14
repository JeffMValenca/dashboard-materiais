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
    # Dados fictícios
    dados_pdm = pd.DataFrame({
        'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'],
        'Realizado': [120, 145, 130, 160, 155],
        'Meta': [150, 150, 150, 150, 150]
    })
    
    dados_barreiras = pd.DataFrame({
        'Status': ['Cadastrados/Revisados', 'Pendentes'],
        'Quantidade': [2100, 4900]
    })
    
    return dados_pdm, dados_barreiras

df_pdm, df_barreiras = carregar_dados()

# ==========================================
# MENU LATERAL (FILTROS)
# ==========================================
with st.sidebar:
    st.header("🔍 Filtros de Análise")
    st.info("Estes filtros serão ativados quando os dados reais forem conectados.")
    mes_filtro = st.selectbox("Selecione o Mês", ["Todos", "Janeiro", "Fevereiro", "Março"])
    frota_filtro = st.selectbox("Selecione a Frota", ["Todas", "Peregrino", "Frota Antiga"])
    st.divider()
    st.caption("Equipe de Confiabilidade - Gestão de Sobressalentes")

# ==========================================
# CABEÇALHO PRINCIPAL
# ==========================================
st.title("⚙️ Dashboard de Gestão de Materiais")
st.markdown("Acompanhamento de Sobressalentes, Metas de Equipamentos Críticos e Rotinas da Equipe.")
st.divider()

# ==========================================
# SEÇÃO 1: METAS DO ANO (AJUSTADA NA HORIZONTAL)
# ==========================================
st.header("🎯 1. Metas do Ano")

# --- 1.1 Cronograma de Equipamentos Críticos ---
st.subheader("1.1 Equip. Críticos (Peregrino)")
st.caption("Documentações verificadas na diária")

# Cria duas colunas: a 1ª menor para o gráfico, a 2ª maior (dobro do tamanho) para o espaço livre
col_11_A, col_11_B = st.columns([1, 2]) 

with col_11_A:
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 78, 
        number = {"suffix": "%"},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#00cc96"},
            'steps': [
                {'range': [0, 50], 'color': "#ffcccb"},
                {'range': [50, 80], 'color': "#ffffcc"},
                {'range': [80, 100], 'color': "#e0ffe0"}
            ]
        }
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col_11_B:
    # Este é o seu espaço livre para o futuro. 
    st.info("💡 **Espaço Reservado:** Esta área lateral inteira está livre para adicionarmos tabelas de pendências, histórico de evolução das reuniões diárias ou detalhamento por família de equipamento no futuro.")

st.divider() # Linha de separação visual

# --- 1.2 PDM de Materiais ---
st.subheader("1.2 PDM de Materiais")
st.caption("Acompanhamento quantitativo D-1 (Contratada)")

# Aqui deixei o gráfico de barras um pouco mais largo ([2, 1]), pois gráficos de linha/barra precisam de extensão
col_12_A, col_12_B = st.columns([2, 1])

with col_12_A:
    fig_pdm = go.Figure()
    fig_pdm.add_trace(go.Bar(x=df_pdm['Dia'], y=df_pdm['Realizado'], name='Realizado', marker_color='#636efa'))
    fig_pdm.add_trace(go.Scatter(x=df_pdm['Dia'], y=df_pdm['Meta'], name='Meta Diária', line=dict(color='red', width=2)))
    fig_pdm.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(yanchor="top", y=1.2, xanchor="left", x=0))
    st.plotly_chart(fig_pdm, use_container_width=True)

with col_12_B:
    st.info("💡 **Espaço Reservado:** Ideal para colocarmos indicadores de qualidade do saneamento da contratada ou um 'Top 5' de atrasos do PDM.")

st.divider()

# --- 1.3 Cronograma de Barreiras de Segurança ---
st.subheader("1.3 Barreiras (Frota Antiga)")
st.caption("Progresso de cadastramento de materiais")

col_13_A, col_13_B = st.columns([1, 2])

with col_13_A:
    fig_donut = px.pie(df_barreiras, values='Quantidade', names='Status', hole=0.6, 
                       color_discrete_sequence=['#19d3f3', '#ef553b'])
    fig_donut.update_traces(textinfo='value+percent')
    fig_donut.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)

with col_13_B:
    st.info("💡 **Espaço Reservado:** Ótimo local para quebrar esse status por disciplina (Mecânica, Elétrica, Instrumentação) ou destacar os itens mais críticos pendentes.")

st.divider()

# ==========================================
# SEÇÃO 2: ROTINAS (DIÁRIAS E SEMANAIS)
# ==========================================
st.header("📅 2. Rotinas Operacionais (SLA Semanal)")
st.markdown("Status de execução das rotinas da equipe de confiabilidade.")

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
    
st.caption("O painel está estruturado e aguardando a conexão com a fonte de dados oficial.")
