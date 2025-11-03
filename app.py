import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import time
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="VYNNOS • Fight Intelligence", page_icon="🥷", layout="wide")

# ================== CSS CORRIGIDO ==================
st.markdown("""
<style>
.stApp { 
    background: #0a0a0a; 
    color: white;
}
 
.stSidebar {
    background: #101010 !important;
    border-right: 1px solid #1c1c1c;
}

h1, h2, h3, h4, h5, h6, p, span, label, div {
    color: #ffffff !important;
}

.vy-card {
    background: #111111;
    border: 1px solid rgba(200, 16, 46, 0.35);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
}

.vy-title {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05rem;
    opacity: 0.9;
    margin-bottom: 8px;
}

.vy-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #c8102e;
    margin: 8px 0;
}

.vy-sub {
    font-size: 0.7rem;
    color: #aaaaaa !important;
}

.top-bar {
    background: linear-gradient(90deg, #131313 0%, #0a0a0a 100%);
    border: 1px solid #1f1f1f;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 20px;
}

.ufc-badge {
    background: #c8102e;
    color: white;
    padding: 6px 14px;
    border-radius: 8px;
    font-weight: 700;
    letter-spacing: 0.1rem;
    text-transform: uppercase;
    font-size: 0.8rem;
    display: inline-block;
    margin-bottom: 8px;
}

.fight-card {
    background: #111111;
    border: 1px solid rgba(200, 16, 46, 0.35);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 12px;
    border-left: 4px solid #c8102e;
}

.fight-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.fight-card-fighters {
    font-weight: 700;
    font-size: 1.1rem;
    color: white;
}

.fight-card-stats {
    display: flex;
    gap: 20px;
    font-size: 0.8rem;
}

.fight-card-stat {
    text-align: center;
}

.fight-card-value {
    font-weight: 700;
    color: #c8102e;
    font-size: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ================== DADOS MOCK CORRIGIDOS ==================
def create_mock_data():
    """Cria dados mock realistas"""
    lutas_df = pd.DataFrame([
        {
            "evento": "UFC 301", 
            "data": "2024-12-15", 
            "local": "Las Vegas, NV",
            "lutador_a": "Jon Jones", 
            "lutador_b": "Alexander Gustafsson", 
            "odd_a": 1.65, 
            "odd_b": 2.25, 
            "conf_vynnos": 0.78, 
            "ev_vynnos": 8.3,
            "categoria": "Light Heavyweight"
        },
        {
            "evento": "UFC 301", 
            "data": "2024-12-15", 
            "local": "Las Vegas, NV", 
            "lutador_a": "Israel Adesanya", 
            "lutador_b": "Alex Pereira",
            "odd_a": 1.85, 
            "odd_b": 1.95, 
            "conf_vynnos": 0.65, 
            "ev_vynnos": 5.2,
            "categoria": "Middleweight"
        },
        {
            "evento": "UFC 302", 
            "data": "2024-12-20", 
            "local": "Miami, FL",
            "lutador_a": "Charles Oliveira", 
            "lutador_b": "Justin Gaethje", 
            "odd_a": 1.75, 
            "odd_b": 2.10, 
            "conf_vynnos": 0.72, 
            "ev_vynnos": 6.8,
            "categoria": "Lightweight"
        }
    ])
    
    sinais_df = pd.DataFrame([
        {
            "luta": "Jon Jones x Gustafsson", 
            "mercado": "ML", 
            "odd": 1.65,
            "ev": 8.3, 
            "conf": 0.78, 
            "fonte": "Betano", 
            "evento": "UFC 301",
            "data_evento": "2024-12-15", 
            "risco": "alto", 
            "lutador": "Jon Jones"
        },
        {
            "luta": "Adesanya x Pereira", 
            "mercado": "ML", 
            "odd": 1.85,
            "ev": 5.2, 
            "conf": 0.65, 
            "fonte": "Bet365", 
            "evento": "UFC 301",
            "data_evento": "2024-12-15", 
            "risco": "medio", 
            "lutador": "Israel Adesanya"
        }
    ])
    
    analises_df = pd.DataFrame([
        {
            "luta": "Jon Jones x Gustafsson",
            "analise_tatica": "Jones controla distância com jab e low kicks. Vantagem no clinch e ground. Gustafsson precisa manter distância e usar reach advantage.",
            "alerta": "Não entrar odd < 1.55. Observar peso do Jones.",
            "momento": "Jones em fase de retorno, Gustafsson consistente",
            "vantagens": "Wrestling, experiência, clinch",
            "desvantagens": "Tempo fora do octógono"
        }
    ])
    
    return lutas_df, sinais_df, analises_df

# ================== CARREGAMENTO SIMPLIFICADO ==================
@st.cache_data
def load_data():
    """Carrega dados de forma simplificada"""
    try:
        # Tenta carregar arquivos reais
        if os.path.exists("dados/lutas_futuras.xlsx"):
            lutas_df = pd.read_excel("dados/lutas_futuras.xlsx")
        else:
            lutas_df, _, _ = create_mock_data()
            
        if os.path.exists("sinais/sinais_atual.xlsx"):
            sinais_df = pd.read_excel("sinais/sinais_atual.xlsx")
        else:
            _, sinais_df, _ = create_mock_data()
            
        if os.path.exists("sinais/analises_atual.xlsx"):
            analises_df = pd.read_excel("sinais/analises_atual.xlsx")
        else:
            _, _, analises_df = create_mock_data()
            
        return lutas_df, sinais_df, analises_df, False
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        # Fallback para mock
        lutas_df, sinais_df, analises_df = create_mock_data()
        return lutas_df, sinais_df, analises_df, True

# ================== CARREGAR DADOS ==================
lutas_df, sinais_df, analises_df, using_mock = load_data()

# Processar datas
if 'data' in lutas_df.columns:
    lutas_df['data'] = pd.to_datetime(lutas_df['data'], errors='coerce')
    hoje = pd.to_datetime(date.today())
    lutas_futuras = lutas_df[lutas_df['data'] >= hoje].copy()
else:
    lutas_futuras = lutas_df.copy()

if lutas_futuras.empty:
    lutas_futuras = lutas_df.copy()

# ================== SIDEBAR CORRIGIDO ==================
with st.sidebar:
    # Logo local ou placeholder
    try:
        st.image("https://upload.wikimedia.org/wikipedia/commons/9/92/UFC_Logo.svg", width=120)
    except:
        st.markdown("### 🥊 UFC")
    
    st.markdown("## **VYNNOS**")
    st.markdown("### Fight Intelligence")
    st.markdown("---")
    
    # Navegação
    page = st.radio(
        "**Navegação**",
        ["📊 Dashboard", "📅 Próximos Cards", "💰 Sinais / Bets", "🔍 Análise Técnica", "⚙️ Config"],
        index=0
    )
    
    st.markdown("---")
    
    # Status
    if using_mock:
        st.warning("⚠️ Usando dados de exemplo")
    else:
        st.success("✅ Dados reais carregados")
    
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    st.caption(f"v2.0 • {datetime.now().strftime('%d/%m %H:%M')}")

# ================== HEADER CORRIGIDO ==================
st.markdown("""
<div class="top-bar">
    <div>
        <div class="ufc-badge">UFC FIGHT INTELLIGENCE</div>
        <h1 style="margin: 8px 0; font-size: 1.8rem;">Painel Oficial VYNNOS</h1>
        <p style="margin: 0; opacity: 0.8;">Sistema de análise e inteligência para lutas UFC</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ================== CARDS TOPO CORRIGIDOS ==================
total_eventos = lutas_futuras['evento'].nunique() if not lutas_futuras.empty else 0
sinais_ev_count = len(sinais_df[sinais_df['ev'] > 0]) if 'ev' in sinais_df.columns else 0
total_lutas = len(lutas_futuras)

# Próxima data
proxima_data = "-"
if not lutas_futuras.empty and 'data' in lutas_futuras.columns:
    datas_validas = lutas_futuras[lutas_futuras['data'].notna()]
    if not datas_validas.empty:
        proxima_data = datas_validas['data'].min().strftime('%d/%m/%Y')

# Layout dos cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="vy-card">
        <div class="vy-title">Próximos Cards</div>
        <div class="vy-value">{total_eventos}</div>
        <div class="vy-sub">eventos futuros</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="vy-card">
        <div class="vy-title">Sinais EV+</div>
        <div class="vy-value">{sinais_ev_count}</div>
        <div class="vy-sub">oportunidades positivas</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="vy-card">
        <div class="vy-title">Próxima Data</div>
        <div class="vy-value">{proxima_data}</div>
        <div class="vy-sub">próximo evento</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="vy-card">
        <div class="vy-title">Total Lutas</div>
        <div class="vy-value">{total_lutas}</div>
        <div class="vy-sub">analisadas</div>
    </div>
    """, unsafe_allow_html=True)

# ================== PÁGINAS CORRIGIDAS ==================
if "📊 Dashboard" in page:
    st.header("📊 Dashboard")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("🎯 Melhores Oportunidades")
        if not sinais_df.empty:
            # Ordenar por EV
            if 'ev' in sinais_df.columns:
                top_sinais = sinais_df.sort_values('ev', ascending=False).head(10)
                st.dataframe(
                    top_sinais[['luta', 'mercado', 'odd', 'ev', 'fonte', 'risco']],
                    use_container_width=True
                )
            else:
                st.dataframe(sinais_df, use_container_width=True)
        else:
            st.info("Nenhum sinal disponível")
        
        st.subheader("📅 Próximas Lutas")
        if not lutas_futuras.empty:
            display_cols = ['evento', 'data', 'lutador_a', 'lutador_b', 'categoria']
            display_cols = [col for col in display_cols if col in lutas_futuras.columns]
            
            display_df = lutas_futuras[display_cols].copy()
            if 'data' in display_df.columns:
                display_df['data'] = display_df['data'].dt.strftime('%d/%m/%Y')
            
            st.dataframe(display_df.head(8), use_container_width=True)
        else:
            st.info("Nenhuma luta futura encontrada")
    
    with col2:
        st.subheader("📈 Top EV+")
        if not sinais_df.empty and 'ev' in sinais_df.columns:
            top_ev = sinais_df.nlargest(5, 'ev')
            
            fig = px.bar(
                top_ev,
                x='ev',
                y='luta',
                orientation='h',
                title='',
                color='ev',
                color_continuous_scale='reds'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=300,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🎲 Distribuição de Risco")
        if not sinais_df.empty and 'risco' in sinais_df.columns:
            risco_counts = sinais_df['risco'].value_counts()
            fig2 = px.pie(
                values=risco_counts.values,
                names=risco_counts.index,
                title=''
            )
            fig2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=300
            )
            st.plotly_chart(fig2, use_container_width=True)

elif "📅 Próximos Cards" in page:
    st.header("📅 Próximos Cards UFC")
    
    if not lutas_futuras.empty:
        # Filtros simples
        col1, col2 = st.columns(2)
        with col1:
            eventos = ['Todos'] + sorted(lutas_futuras['evento'].unique().tolist())
            evento_sel = st.selectbox('Evento', eventos)
        
        with col2:
            categorias = ['Todas'] + sorted(lutas_futuras['categoria'].unique().tolist()) if 'categoria' in lutas_futuras.columns else ['Todas']
            categoria_sel = st.selectbox('Categoria', categorias)
        
        # Aplicar filtros
        filtered_df = lutas_futuras.copy()
        if evento_sel != 'Todos':
            filtered_df = filtered_df[filtered_df['evento'] == evento_sel]
        if categoria_sel != 'Todas' and 'categoria' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['categoria'] == categoria_sel]
        
        # Mostrar dados
        display_cols = ['evento', 'data', 'local', 'lutador_a', 'lutador_b', 'odd_a', 'odd_b', 'categoria']
        display_cols = [col for col in display_cols if col in filtered_df.columns]
        
        display_df = filtered_df[display_cols].copy()
        if 'data' in display_df.columns:
            display_df['data'] = display_df['data'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(display_df, use_container_width=True)
        
    else:
        st.info("Nenhum card futuro encontrado")

elif "💰 Sinais / Bets" in page:
    st.header("💰 Sinais / Bets")
    
    if not sinais_df.empty:
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            eventos = ['Todos'] + sorted(sinais_df['evento'].unique().tolist())
            evento_sel = st.selectbox('Evento', eventos, key='sinais_evento')
        
        with col2:
            min_ev = st.slider('EV Mínimo', -5.0, 20.0, 0.0, 0.5)
        
        # Aplicar filtros
        filtered_sinais = sinais_df.copy()
        if evento_sel != 'Todos':
            filtered_sinais = filtered_sinais[filtered_sinais['evento'] == evento_sel]
        
        if 'ev' in filtered_sinais.columns:
            filtered_sinais = filtered_sinais[filtered_sinais['ev'] >= min_ev]
        
        st.dataframe(filtered_sinais, use_container_width=True)
        
    else:
        st.warning("Nenhum sinal disponível")

elif "🔍 Análise Técnica" in page:
    st.header("🔍 Análise Técnica")
    
    if not analises_df.empty:
        luta_sel = st.selectbox('Selecionar Luta', analises_df['luta'].unique())
        
        analise = analises_df[analises_df['luta'] == luta_sel].iloc[0]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"🥊 {analise['luta']}")
            st.write(f"**🎯 Momento:** {analise.get('momento', 'N/A')}")
            
            st.write("**📋 Análise Tática:**")
            st.info(analise.get('analise_tatica', 'N/A'))
            
            st.write("**⚠️ Alerta:**")
            st.warning(analise.get('alerta', 'Sem alertas'))
        
        with col2:
            st.write("**✅ Vantagens:**")
            st.success(analise.get('vantagens', 'N/A'))
            
            st.write("**❌ Desvantagens:**")
            st.error(analise.get('desvantagens', 'N/A'))
    
    else:
        st.info("Nenhuma análise técnica disponível")

else:  # Config
    st.header("⚙️ Configuração")
    
    st.write("**Estrutura de arquivos necessária:**")
    st.code("""
vynnos_ufc/
├── app.py
├── dados/
│   └── lutas_futuras.xlsx
└── sinais/
    ├── sinais_atual.xlsx
    └── analises_atual.xlsx
    """)
    
    st.info("""
    **Formato dos arquivos:**
    
    **lutas_futuras.xlsx:** evento, data, local, lutador_a, lutador_b, odd_a, odd_b, conf_vynnos, ev_vynnos, categoria
    
    **sinais_atual.xlsx:** luta, mercado, odd, ev, conf, fonte, evento, data_evento, risco, lutador
    
    **analises_atual.xlsx:** luta, analise_tatica, alerta, momento, vantagens, desvantagens
    """)

# ================== DEBUG INFO ==================
with st.expander("🔧 Informações de Debug"):
    st.write(f"**Dados carregados:** {len(lutas_df)} lutas, {len(sinais_df)} sinais, {len(analises_df)} análises")
    st.write(f"**Usando mock data:** {using_mock}")
    st.write(f"**Lutas futuras:** {len(lutas_futuras)}")
    
    if st.button("Recarregar App"):
        st.cache_data.clear()
        st.rerun()