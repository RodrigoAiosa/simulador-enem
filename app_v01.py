import streamlit as st

st.set_page_config(layout="wide")

# -------------------------
# CSS PREMIUM OFICIAL
# -------------------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    background-color: #0a0f1c;
    font-family: 'Poppins', sans-serif;
}

header, footer, #MainMenu {
    visibility: hidden;
}

/* Container central */
.block-container {
    padding-top: 3rem;
    max-width: 1100px;
}

/* Topo pequeno */
.topo {
    text-align:center;
    letter-spacing: 6px;
    font-size: 12px;
    color: #ff7a00;
    margin-bottom: 20px;
}

/* ENEM */
.titulo-enem {
    text-align:center;
    font-family: 'Playfair Display', serif;
    font-size: 90px;
    font-weight: 800;
    color: #f3efe7;
    margin-bottom: -25px;
}

/* Simulador */
.subtitulo {
    text-align:center;
    font-size: 42px;
    color: #ff7a00;
    font-style: italic;
    margin-bottom: 25px;
}

/* descrição */
.descricao {
    text-align:center;
    color: #7f8794;
    font-size: 14px;
    letter-spacing: 1px;
    margin-bottom: 50px;
}

/* seção */
.secao {
    text-align:center;
    color:#7f8794;
    letter-spacing:3px;
    font-size:13px;
    margin-bottom:30px;
}

/* Cards */
.card {
    padding: 28px;
    border-radius: 20px;
    border: 1.5px solid;
    margin-bottom: 18px;
    transition: 0.3s ease;
}

.card:hover {
    transform: scale(1.02);
}

.laranja {
    border-color:#ff7a00;
    background: linear-gradient(145deg, rgba(255,122,0,0.07), rgba(255,122,0,0.02));
}

.verde {
    border-color:#00e0a4;
    background: linear-gradient(145deg, rgba(0,224,164,0.07), rgba(0,224,164,0.02));
}

.roxo {
    border-color:#a855f7;
    background: linear-gradient(145deg, rgba(168,85,247,0.07), rgba(168,85,247,0.02));
}

.azul {
    border-color:#3b82f6;
    background: linear-gradient(145deg, rgba(59,130,246,0.07), rgba(59,130,246,0.02));
}

.card h3 {
    margin-bottom:5px;
    font-weight:600;
}

.card p {
    font-size:13px;
    color:#7f8794;
}

/* Botões secundários */
.stButton > button {
    background: transparent;
    border:1px solid #ff7a00;
    color:#ff7a00;
    border-radius:12px;
    padding:8px 18px;
}

.stButton > button:hover {
    background:#ff7a00;
    color:white;
}

/* Botão principal */
.botao-principal button {
    background:#ff7a00 !important;
    color:white !important;
    font-weight:600;
    border:none !important;
    border-radius:14px !important;
    padding:14px 35px !important;
    box-shadow:0 0 25px rgba(255,122,0,0.5);
    transition:0.3s;
}

.botao-principal button:hover {
    transform: scale(1.05);
}

.center {
    display:flex;
    justify-content:center;
    margin-top:35px;
}

.contador {
    text-align:center;
    color:#7f8794;
    margin-top:10px;
    font-size:13px;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.markdown('<div class="topo">PREPARATÓRIO OFICIAL</div>', unsafe_allow_html=True)
st.markdown('<div class="titulo-enem">ENEM</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Simulador</div>', unsafe_allow_html=True)
st.markdown('<div class="descricao">40 questões · 4 áreas · Análise por competência · Shuffled</div>', unsafe_allow_html=True)
st.markdown('<div class="secao">SELECIONE AS ÁREAS DO SIMULADO</div>', unsafe_allow_html=True)

# -------------------------
# CARDS
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card laranja">
        <h3 style="color:#ff7a00;">✍ Linguagens</h3>
        <p>10 questões</p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✓ LINGUAGENS")

with col2:
    st.markdown("""
    <div class="card verde">
        <h3 style="color:#00e0a4;">🔬 Ciências da Natureza</h3>
        <p>10 questões</p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✓ CIÊNCIAS DA NATUREZA")

col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class="card roxo">
        <h3 style="color:#a855f7;">🏛 Ciências Humanas</h3>
        <p>10 questões</p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✓ CIÊNCIAS HUMANAS")

with col4:
    st.markdown("""
    <div class="card azul">
        <h3 style="color:#3b82f6;">📐 Matemática</h3>
        <p>10 questões</p>
    </div>
    """, unsafe_allow_html=True)
    st.button("✓ MATEMÁTICA")

st.markdown('<div class="contador">40 questões selecionadas</div>', unsafe_allow_html=True)

st.markdown('<div class="center botao-principal">', unsafe_allow_html=True)
st.button("INICIAR SIMULADO →")
st.markdown('</div>', unsafe_allow_html=True)
