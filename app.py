import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. CONFIGURAÇÃO E CONEXÃO GOOGLE
# ==========================================
st.set_page_config(page_title="Dashboard Materiais - Confiabilidade", page_icon="⚙️", layout="wide")

LINK_PLANILHA = "https://docs.google.com/spreadsheets/d/17HqIfoMCwkrXgfRPNNpwJBvWrPt71e-yM_oZVCdxaf8"

@st.cache_resource
def conectar_google_sheets():
    try:
        creds_json = st.secrets["google_credentials"]
        creds_dict = json.loads(creds_json)
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"⚠️ Erro na conexão com o Google. Detalhe: {e}")
        return None

# ==========================================
# 2. LEITURA DOS DADOS (GRÁFICOS E TABELAS)
# ==========================================
@st.cache_data(ttl=300)
def carregar_dados_planilha():
    client = conectar_google_sheets()
    
    crono_bkp = pd.DataFrame({'TIPO': ['EQUIPAMENTO'], 'EQUIPAMENTO': ['EXEMPLO'], 'INICIO': ['01/01/26'], 'FIM': ['10/01/26'], 'FIM REAL': ['-'], 'TOTAL DE DIAS': [10], '% PLANEJADO': ['10%'], '% REALIZADO': ['-'], 'TOTAL DE DOCUMENTOS': ['0'], 'Doc. Já Analisados': ['0'], 'STATUS DA ATIVIDADE': ['PENDENTE']})
    curva_bkp = pd.DataFrame({'Mês': ['Jan/26'], 'Planejado Acumulado (%)': [10], 'Realizado Acumulado (%)': [5]})
    pdm_m_bkp = pd.DataFrame({'MÊS': ['JAN'], 'Planejado Mês': [10], 'Planejado Acum.': [10], 'Realizado Mês': [5], 'Realizado Acum.': [5], '% Concluído do Projeto': ['5%']})
    pdm_d_bkp = pd.DataFrame({'Data': ['01', '02', '03', '04', '05'], 'Meta Diária': [150, 150, 150, 150, 150], 'Realizado Dia': [120, 145, 130, None, None]})
    
    # NOVO BACKUP DA ABA BARREIRAS (ATUALIZADO)
    barreiras_bkp = pd.DataFrame({
        'ATIVO': ['FRADE', 'FORTE', 'BRAVO', 'POLVO'], 
        "TOTAL DE TAG's": [450, 450, 450, 450],
        "TOTAL DE TAG's FEITAS": [23, 11, 4, 16],
        'PERCENTUAL': ['5,11%', '2,44%', '0,89%', '3,56%']
    })

    if not client: return crono_bkp, curva_bkp, pdm_m_bkp, pdm_d_bkp, barreiras_bkp

    try:
        planilha = client.open_by_url(LINK_PLANILHA)
        df_crono = pd.DataFrame(planilha.worksheet("Cronograma").get_all_records()).replace('', None)
        df_curva = pd.DataFrame(planilha.worksheet("Curva_S").get_all_records()).replace('', None)
        df_pdm_mensal = pd.DataFrame(planilha.worksheet("PDM_Mensal").get_all_records()).replace('', None)
        df_pdm_diario = pd.DataFrame(planilha.worksheet("PDM_Diario").get_all_records()).replace('', None)
        df_barreiras = pd.DataFrame(planilha.worksheet("Barreiras").get_all_records()).replace('', None)
        return df_crono, df_curva, df_pdm_mensal, df_pdm_diario, df_barreiras
    except Exception as e:
        st.warning(f"⚠️ Algumas abas não foram encontradas. Usando base de teste.")
        return crono_bkp, curva_bkp, pdm_m_bkp, pdm_d_bkp, barreiras_bkp

df_crono, df_curva_eqp, df_pdm_mensal, df_pdm_diario, df_barreiras = carregar_dados_planilha()

# --- CORREÇÃO DO VELOCÍMETRO (SOMA DA COLUNA % REALIZADO) ---
try: 
    soma_realizado = df_crono['% REALIZADO'].astype(str).str.replace('%', '').str.replace(',', '.')
    val_crono = pd.to_numeric(soma_realizado, errors='coerce').sum()
except: 
    val_crono = 0

try: val_pdm = pd.to_numeric(df_pdm_mensal['% Concluído do Projeto'].astype(str).str.replace('%', ''), errors='coerce').dropna().iloc[-1]
except: val_pdm = 0

# ==========================================
# 3. KANBAN (FUNÇÕES)
# ==========================================
def carregar_kanban():
    client = conectar_google_sheets()
    if client:
        try: return pd.DataFrame(client.open_by_url(LINK_PLANILHA).worksheet("Kanban").get_all_records())
        except: pass
    return pd.DataFrame(columns=["ID", "Tarefa", "Solicitante", "Prioridade", "Status"])

def acao_kanban(acao, id_tarefa, *args):
    client = conectar_google_sheets()
    if client:
        planilha = client.open_by_url(LINK_PLANILHA).worksheet("Kanban")
        registros = planilha.get_all_records()
        if acao == 'adicionar':
            planilha.append_row([id_tarefa, args[0], args[1], args[2], args[3]])
        else:
            for i, linha in enumerate(registros):
                if str(linha['ID']) == str(id_tarefa):
                    if acao == 'atualizar': planilha.update_cell(i + 2, 5, args[0])
                    elif acao == 'deletar': planilha.delete_rows(i + 2)
                    break

# ==========================================
# 4. INTERFACE DO DASHBOARD
# ==========================================
def colorir_status(val):
    if val == 'CONCLUIDO': return 'background-color: #00cc96; color: black'
    elif val == 'EM ANDAMENTO': return 'background-color: #ffffcc; color: black'
    elif val == 'PENDENTE': return 'background-color: #ffcccb; color: black'
    return ''

with st.sidebar:
    st.header("🔍 Filtros")
    st.info("O painel lê os dados do Google Sheets de 5 em 5 minutos para otimizar velocidade.")
    if st.button("🔄 Forçar Atualização Agora"):
        st.cache_data.clear()
        st.rerun()

st.title("⚙️ Dashboard de Gestão de Materiais")
st.markdown("Acompanhamento de Sobressalentes, Metas de Equipamentos Críticos e Rotinas da Equipe.")
st.divider()

# --- 1.1 Cronograma ---
st.header("🎯 1. Metas do Ano")
st.subheader("1.1 Equip. Críticos (Peregrino)")
col_g1, col_g2 = st.columns([2, 1])

with col_g1:
    fig_curva = go.Figure()
    fig_curva.add_trace(go.Scatter(x=df_curva_eqp['Mês'], y=df_curva_eqp['Planejado Acumulado (%)'], mode='lines+markers', name='Planejado', line=dict(color='gray', dash='dash')))
    fig_curva.add_trace(go.Scatter(x=df_curva_eqp['Mês'], y=df_curva_eqp['Realizado Acumulado (%)'], mode='lines+markers', name='Realizado', line=dict(color='#00cc96', width=3)))
    fig_curva.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig_curva, use_container_width=True)

with col_g2:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number", value=val_crono, number={"suffix": "%"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#2b8cbe"}, 'steps': [{'range': [0, 30], 'color': "#ffcccb"}, {'range': [30, 80], 'color': "#ffffcc"}, {'range': [80, 100], 'color': "#e0ffe0"}]}
    ))
    fig_gauge.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

st.dataframe(df_crono.fillna('-').style.map(colorir_status, subset=['STATUS DA ATIVIDADE']), use_container_width=True, hide_index=True)
st.divider()

# --- 1.2 PDM ---
st.subheader("1.2 PDM de Materiais")
col_p1, col_p2 = st.columns([2, 1])
with col_p1:
    fig_curva_pdm = go.Figure()
    fig_curva_pdm.add_trace(go.Scatter(x=df_pdm_mensal['MÊS'], y=df_pdm_mensal['Planejado Acum.'], mode='lines+markers', name='Planejado Acum.', line=dict(color='gray', dash='dash')))
    fig_curva_pdm.add_trace(go.Scatter(x=df_pdm_mensal['MÊS'], y=df_pdm_mensal['Realizado Acum.'], mode='lines+markers', name='Realizado Acum.', line=dict(color='#636efa', width=3)))
    fig_curva_pdm.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))
    st.plotly_chart(fig_curva_pdm, use_container_width=True)

with col_p2:
    fig_gauge_pdm = go.Figure(go.Indicator(
        mode="gauge+number", value=val_pdm, number={"suffix": "%"},
        gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#636efa"}, 'steps': [{'range': [0, 30], 'color': "#ffcccb"}, {'range': [30, 80], 'color': "#ffffcc"}, {'range': [80, 100], 'color': "#e0ffe0"}]}
    ))
    fig_gauge_pdm.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_gauge_pdm, use_container_width=True)

st.dataframe(df_pdm_mensal.fillna('-'), use_container_width=True, hide_index=True)

# ---- NOVO GRÁFICO PDM DIÁRIO (MENSALIZADO) ----
st.markdown("**Evolução Diária da Contratada no Mês Atual**")
fig_pdm_diario = go.Figure()
fig_pdm_diario.add_trace(go.Bar(x=df_pdm_diario['Data'], y=df_pdm_diario['Realizado Dia'], name='Realizado', marker_color='#636efa'))
fig_pdm_diario.add_trace(go.Scatter(x=df_pdm_diario['Data'], y=df_pdm_diario['Meta Diária'], name='Meta Diária', line=dict(color='red', width=2, dash='dot')))
fig_pdm_diario.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), xaxis_title="Dias do Mês", showlegend=True, legend=dict(yanchor="top", y=1.2, xanchor="left", x=0))
st.plotly_chart(fig_pdm_diario, use_container_width=True)
st.divider()

# --- 1.3 Barreiras ---
st.subheader("1.3 Barreiras de Segurança")

# Tratamento para garantir que o Plotly entenda os percentuais (removendo % e convertendo vírgula para ponto)
df_barreiras['Perc_Num'] = pd.to_numeric(df_barreiras['PERCENTUAL'].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce')
# Ordenando os dados para o gráfico ficar mais bonito
df_barreiras_ordenado = df_barreiras.sort_values(by='Perc_Num', ascending=False)

col_b1, col_b2 = st.columns([1, 2])
with col_b1:
    # Gráfico de Barras novo
    fig_bar = px.bar(df_barreiras_ordenado, x='ATIVO', y='Perc_Num', text='PERCENTUAL', 
                     color_discrete_sequence=['#4169E1'])
    
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(height=250, margin=dict(l=10, r=10, t=20, b=10), showlegend=False,
                          xaxis_title="Ativos", yaxis_title="Percentual (%)")
    
    # Dando espaço extra em cima da barra para o texto não sumir
    if not df_barreiras_ordenado['Perc_Num'].isna().all():
        max_val = df_barreiras_ordenado['Perc_Num'].max()
        fig_bar.update_yaxes(range=[0, max_val + (max_val * 0.3)])
        
    st.plotly_chart(fig_bar, use_container_width=True)
    
with col_b2:
    # Exibindo a tabela original, removendo apenas a coluna de tratamento (Perc_Num)
    st.dataframe(df_barreiras.drop(columns=['Perc_Num'], errors='ignore'), use_container_width=True, hide_index=True)
    
st.divider()

# --- Rotinas ---
st.header("📅 2. Rotinas Operacionais (SLA Semanal)")
r_c1, r_c2, r_c3, r_c4 = st.columns(4)
r_c1.metric("2.1 MRP", "3/3", "No prazo")
r_c2.metric("2.2 Chamados", "2/2", "No prazo")
r_c3.metric("2.3 LTM's", "2/2", "No prazo")
r_c4.metric("2.5 Códigos 6", "1/2", "-1 Pendente", "inverse")
st.divider()

# --- Kanban ---
st.header("🗂️ 3. Solicitações Fora do Escopo (Ad-hoc)")
df_kanban = carregar_kanban()
prox_id = int(pd.to_numeric(df_kanban["ID"], errors="coerce").max() + 1) if not df_kanban.empty and "ID" in df_kanban.columns and pd.to_numeric(df_kanban["ID"], errors="coerce").notnull().any() else 1

with st.expander("➕ Adicionar Nova Solicitação", expanded=False):
    with st.form("form_nova_tarefa", clear_on_submit=True):
        f1, f2, f3 = st.columns([2, 1, 1])
        nova_desc = f1.text_input("Descrição da Tarefa*")
        novo_solic = f2.text_input("Solicitante")
        nova_prior = f3.selectbox("Prioridade", ['Baixa 🟢', 'Média 🟡', 'Alta 🔴'])
        if st.form_submit_button("Salvar") and nova_desc:
            acao_kanban('adicionar', prox_id, nova_desc, novo_solic, nova_prior, 'A Fazer')
            st.rerun()

k1, k2, k3 = st.columns(3)
def desenhar_cartao(linha, ant, prox):
    with st.container(border=True):
        st.markdown(f"**{linha['Tarefa']}**")
        st.caption(f"👤 {linha['Solicitante']} | {linha['Prioridade']}")
        b1, b2, b3 = st.columns(3)
        if b1.button("⏪", key=f"v_{linha['ID']}") and ant:
            acao_kanban('atualizar', linha['ID'], ant)
            st.rerun()
        if b2.button("❌", key=f"d_{linha['ID']}"):
            acao_kanban('deletar', linha['ID'])
            st.rerun()
        if b3.button("⏩", key=f"a_{linha['ID']}") and prox:
            acao_kanban('atualizar', linha['ID'], prox)
            st.rerun()

with k1:
    st.subheader("📋 A Fazer")
    for _, l in df_kanban[df_kanban['Status'] == 'A Fazer'].iterrows(): desenhar_cartao(l, None, 'Em Andamento')
with k2:
    st.subheader("⏳ Em Andamento")
    for _, l in df_kanban[df_kanban['Status'] == 'Em Andamento'].iterrows(): desenhar_cartao(l, 'A Fazer', 'Concluído')
with k3:
    st.subheader("✅ Concluído")
    for _, l in df_kanban[df_kanban['Status'] == 'Concluído'].iterrows(): desenhar_cartao(l, 'Em Andamento', None)
