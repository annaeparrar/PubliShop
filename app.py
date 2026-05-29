import streamlit as st
import re
import os
from google import genai
from google.genai.errors import APIError

# 1. Configuração da página (Deve ser a primeira instrução de Streamlit)
st.set_page_config(
    page_title="Shopee Ads Generator PRO",
    page_icon="🛍️",
    layout="centered"
)

# 2. Estilos CSS personalizados (Uso correto de unsafe_allow_html=True)
st.markdown("""
    <style>
    .main-title {
        font-size: 32px;
        font-weight: bold;
        color: #111111;
        margin-bottom: 5px;
    }
    .subtitle {
        font-size: 14px;
        color: #666666;
        margin-bottom: 25px;
    }
    .wise-container {
        display: flex;
        justify-content: center;
        margin-top: 40px;
        margin-bottom: 20px;
    }
    .wise-button {
        background-color: #9FE870;
        color: #163300 !important;
        padding: 14px 24px;
        border-radius: 12px;
        text-decoration: none;
        font-family: Arial, sans-serif;
        font-size: 18px;
        font-weight: bold;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
        transition: transform 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 10px;
    }
    .wise-button:hover {
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# 3. Função auxiliar para extrair as seções geradas
def extract_section(text, header):
    pattern = rf"{header}:([\s\S]*?)(?=TÍTULO:|COPY:|CTA:|HASHTAGS:|$)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else ""

# 4. Inicialização Segura e Híbrida da API Key (Mapeia local e nuvem automaticamente)
api_key = None

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Correção do st.environ utilizando a biblioteca integrada 'os'
    api_key = os.environ.get("GEMINI_API_KEY", None)

if not api_key:
    st.error("❌ Faltando a configuração de 'GEMINI_API_KEY' nos Secrets do Streamlit ou ambiente local.")
    st.stop()

try:
    # Inicialização oficial do SDK moderno da Google
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"❌ Erro ao inicializar o cliente Gemini: {e}")
    st.stop()

# 5. Interface do Usuário (UI) - Textos e strings corrigidos sem quebras
st.markdown('<div class="main-title">🛍️ Shopee Ads Generator PRO</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Crie anúncios de alta conversão em segundos com Inteligência Artificial.</div>', unsafe_allow_html=True)

product = st.text_input("Nome do produto / Producto", placeholder="Ex: Sapatos de inverno")
features = st.text_area("Características", placeholder="Ex: Sapatos de inverno tamanho 36-38", height=80)
description = st.text_area("Descrição / Descripción", placeholder="Ex: Cores preto e marrom", height=100)

col1, col2 = st.columns(2)
with col1:
    tone = st.selectbox("Tom / Tono", ["Emocional", "Premium", "Urgência", "Divertido"])
with col2:
    language = st.selectbox("Idioma", ["Português do Brasil 🇧🇷", "Español 🇪🇸"])

# 6. Lógica de Geração de Conteúdo (Alinhamento rigoroso de blocos try/except)
if st.button("Gerar anúncio", type="primary", use_container_width=True):
    if not product:
        st.warning("Por favor, insira o nome do produto.")
    else:
        with st.spinner("Gerando conteúdo estratégico..."):
            lang_text = "português do Brasil" if "Português" in language else "espanhol"
            
            prompt = f"""
            Crie um anúncio de alta conversão para a plataforma Shopee em {lang_text} com o tom {tone.lower()}.
            Use técnicas de SEO e gatilhos mentais apropriados.

            Produto: {product}
            Características: {features}
            Descrição complementar
