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

# 2. Cabeçalho
st.title("⚙️ Dashboard de Gestão de Materiais - Confiabilidade")
st.markdown("Acompanhamento de Sobressalentes, Metas de Equipamentos Críticos e Rotinas da Equipe.")
st.divider()

# ==========================================
# SEÇÃO 1: METAS DO ANO
# ==========================================
st.header("🎯 1. Metas do Ano")
col1, col2, col3 = st.columns(3)

# 1.1 Cronograma de Equipamentos Críticos (Gauge)
with col1:
    st.subheader("1.1 Equip. Críticos (Peregrino)")
    st.caption("Documentações verificadas na diária")
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = 78, # Valor fictício atual
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

# 1.2 PDM de Materiais (Gráfico Combinado Real x Meta)
with col2:
    st.subheader("1.2 PDM de Materiais")
    st.caption("Acompanhamento quantitativo D-1 (Contratada)")
    
    # Dados fictícios dos últimos 5 dias
    df_pdm = pd.DataFrame({
        'Dia': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex'],
        'Realizado': [120, 145, 130, 160, 155],
        'Meta': [150, 150, 150, 150, 150]
    })
    
    fig_pdm = go.Figure()
    fig_pdm.add_trace(go.Bar(x=df_pdm['Dia'], y=df_pdm['Realizado'], name='Realizado', marker_color='#636efa'))
    fig_pdm.add_trace(go.Scatter(x=df_pdm['Dia'], y=df_pdm['Meta'], name='Meta Diária', line=dict(color='red', width=2)))
    
    fig_pdm.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(yanchor="top", y=1.2, xanchor="left", x=0))
    st.plotly_chart(fig_pdm, use_container_width=True)

# 1.3 Cronograma de Barreiras de Segurança (Gráfico de Rosca)
with col3:
    st.subheader("1.3 Barreiras (Frota Antiga)")
    st.caption("Percentual de materiais cadastrados")
    
    df_barreiras = pd.DataFrame({
        'Status': ['Cadastrado', 'Pendente'],
        'Valores': [65, 35] # Valores fictícios
    })
    
    fig_donut = px.pie(df_barreiras, values='Valores', names='Status', hole=0.6, 
                       color_discrete_sequence=['#19d3f3', '#ef553b'])
    fig_donut.update_traces(textinfo='percent+label')
    fig_donut.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig_donut, use_container_width=True)

st.divider()

# ==========================================
# SEÇÃO 2: ROTINAS (DIÁRIAS E SEMANAIS)
# ==========================================
st.header("📅 2. Rotinas Operacionais (SLA Semanal)")
st.markdown("Status de execução das rotinas da equipe de confiabilidade.")

# Usando colunas para criar um grid de "Cards" (Métricas)
r_col1, r_col2, r_col3, r_col4 = st.columns(4)

with r_col1:
    st.metric(label="2.1 MRP (3x/sem)", value="3/3", delta="Meta Atingida", delta_color="normal")
    st.metric(label="2.5 Códigos '6' (2x/sem)", value="1/2", delta="-1 Pendente", delta_color="inverse")

with r_col2:
    st.metric(label="2.2 Portal Chamados (2x/sem)", value="2/2", delta="Meta Atingida", delta_color="normal")
    st.metric(label="2.6 Duplicidade (2x/sem)", value="2/2", delta="Meta Atingida", delta_color="normal")

with r_col3:
    st.metric(label="2.3 LTM's (2x/sem)", value="2/2", delta="Meta Atingida", delta_color="normal")
    st.metric(label="2.7 Primarização (1x/sem)", value="0/1", delta="-1 Pendente", delta_color="inverse")

with r_col4:
    # Acompanhamento diário em destaque
    st.info("**2.4 Lev. Técnico de Campo**\n\nAcompanhamento Diário consolidado com sucesso no dia de hoje.")
    
st.caption("Última atualização: Hoje. (No futuro, você pode conectar isso a um banco de dados para atualizar automaticamente).")