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

# 4. Inicialização Segura e Híbrida da API Key
api_key = None

if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    # Fallback seguro usando a biblioteca os integrada do sistema
    api_key = os.environ.get("GEMINI_API_KEY", None)

if not api_key:
    st.error("❌ Faltando a configuração de 'GEMINI_API_KEY' nos Secrets do Streamlit ou ambiente local.")
    st.stop()

try:
    # Inicialização do cliente oficial usando a chave validada
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"❌ Erro ao inicializar o cliente Gemini: {e}")
    st.stop()

# 5. Interfaz de Usuário (UI) - Correção total de strings e tags HTML
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

# 6. Lógica de Geração de Conteúdo com Try-Except Completo
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
            Descrição complementar: {description}

            Retorne a resposta dividida EXATAMENTE com estes cabeçalhos em letras maiúsculas:

            TÍTULO:
            (Escreva um título atraente e otimizado para buscas)

            COPY:
            (Desenvolva o corpo do texto do anúncio focando nos benefícios)

            CTA:
            (Crie uma chamada para ação persuasiva)

            HASHTAGS:
            (Insira as hashtags mais relevantes separadas por espaços)
            """
            
            try:
                # Chamada estável utilizando o modelo atualizado gemini-2.5-flash
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                generated_text = response.text
                
                # Extração e segmentação de blocos
                titulo = extract_section(generated_text, "TÍTULO")
                copy = extract_section(generated_text, "COPY")
                cta = extract_section(generated_text, "CTA")
                hashtags = extract_section(generated_text, "HASHTAGS")
                
                st.markdown("## ✨ Resultados Gerados")
                
                st.subheader("📝 Título SEO")
                st.code(titulo if titulo else generated_text, language=None)
                
                if copy:
                    st.subheader("🎯 Copy do Anúncio")
                    st.info(copy)
                if cta:
                    st.subheader("🚀 Call to Action (CTA)")
                    st.code(cta, language=None)
                if hashtags:
                    st.subheader("🏷️ Hashtags Sugeridas")
                    st.text(hashtags)
                
                # Geração de arquivo para download do usuário
                full_download = f"TÍTULO:\n{titulo}\n\nCOPY:\n{copy}\n\nCTA:\n{cta}\n\nHASHTAGS:\n{hashtags}"
                st.download_button(
                    label="📥 Exportar Anúncio (.txt)",
                    data=full_download,
                    file_name=f"{product.replace(' ', '_')}_shopee_ad.txt",
                    mime="text/plain"
                )
                
            except APIError as e:
                if e.code == 503:
                    st.error("⚠️ Os servidores do Gemini estão sob alta demanda temporária. Por favor, aguarde alguns segundos e tente novamente.")
                elif e.code == 404:
                    st.error("⚠️ Erro 404: Modelo não encontrado. Verifique a sintaxe da chamada do modelo.")
                elif e.code == 401:
                    st.error("⚠️ Erro de Autenticação (401): A API Key configurada parece inválida.")
                else:
                    st.error(f"Erro na API do Gemini: {e.message}")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")

# 7. Rodapé e Injeção de Link Externo
st.markdown("---")
st.markdown("<p style='text-align: center; color: #aaa; font-size: 12px;'>Powered by Gemini AI • Shopee Ads Generator PRO</p>", unsafe_allow_html=True)

st.markdown("""
    <div class="wise-container">
        <a href="https://wise.com/pay/r/A03_lpdchRegPpo" target="_blank" rel="noopener noreferrer" class="wise-button">
            💚 Donar con Wise
        </a>
    </div>
""", unsafe_allow_html=True)
