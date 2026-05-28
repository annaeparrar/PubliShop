import re
import streamlit as st
from google import genai
from google.genai import types

# 1. Configuración de la interfaz (Estilo minimalista similar a tu CSS original)
st.set_page_config(
    page_title="Shopee Ads Generator PRO",
    page_icon="🛍️",
    layout="centered"
)

# Inyección de estilos CSS para mantener tus fuentes, bordes redondeados y espaciados
st.markdown("""
    <style>
    body { background-color: #f7f7f8; }
    .main .block-container { max-width: 750px; padding-top: 3rem; }
    h1 { font-size: 24px; font-weight: 700; color: #1E1E1E; margin-bottom: 20px; }
    /* Estilo para las cajas de salida (output-box) */
    .output-box {
        padding: 15px;
        border-radius: 12px;
        background-color: #fafafa;
        border: 1px solid #eee;
        margin-bottom: 12px;
    }
    .box-label { font-size: 12px; color: gray; margin-bottom: 5px; font-weight: 600; }
    .box-content { font-size: 14px; color: #333; white-space: pre-wrap; }
    </style>
""", unsafe_allow_html=True)

st.title("🛍️ Shopee Ads Generator PRO")

# 2. Inicialización de la API de Gemini de forma segura
try:
    # Streamlit buscará esta variable en tu archivo secrets.toml local
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("Falta la configuración de 'GEMINI_API_KEY' en los Secrets de Streamlit.")
    st.stop()

# 3. Componentes de la Interfaz (Inputs del usuario)
product = st.text_input("Nome do produto / Producto", placeholder="Ej. Kit Festa Infantil Personalizado em Feltro")
features = st.text_area("Características", placeholder="Ej. Feito à mão, alta durabilidade, cores vibrantes...")
description = st.text_area("Descrição / Descripción", placeholder="Ej. Detalhes sobre o tamanho, materiais utilizados e prazos...")

# Ponemos los selectores de Tom e Idioma uno al lado del otro
col1, col2 = st.columns(2)
with col1:
    tone = st.selectbox("Tom / Tono", ["Emocional", "Premium", "Urgencia", "Divertido"])
with col2:
    language = st.selectbox("Idioma", ["Português do Brasil 🇧🇷", "Español 🇪🇸"], index=0)

# Mapeo de idioma para el prompt
lang_text = "português do Brasil" if "🇧🇷" in language else "espanhol"

# Función auxiliar para extraer las secciones usando Regex (idéntica a tu función 'extract' de JS)
def extract_section(text, key):
    pattern = rf"{key}(.*?)(?=TÍTULO:|COPY:|CTA:|HASHTAGS:|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""

# 4. Lógica principal al hacer clic en "Gerar anúncio"
if st.button("Gerar anúncio", type="primary"):
    if not product:
        st.warning("Por favor, informe o nome do produto.")
    else:
        with st.spinner("Gerando anúncio com o Gemini..."):
            # Recreamos exactamente tu prompt original
            prompt = f"""
Crie conteúdo para Shopee em {lang_text} com tom {tone.lower()}:

Produto: {product}
Características: {features}
Descrição: {description}

Separe claramente:

TÍTULO:
COPY:
CTA:
HASHTAGS:
"""
            try:
                # Usamos el modelo recomendado actual (gemini-1.5-flash)
                response = client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7
                    )
                )
                
                # Guardamos el resultado completo en la sesión para mantenerlo tras interactuar con la página
                st.session_state['last_result'] = response.text
                
            except Exception as e:
                st.error(f"Erro ao conectar com o Gemini: {e}")

# 5. Renderizado de Resultados (si existen en la sesión)
if 'last_result' in st.session_state:
    text_result = st.session_state['last_result']
    
    # Extraemos las secciones usando nuestra función regex de Python (CORREGIDO)
    titulo = extract_section(text_result, "TÍTULO:")
    copy = extract_section(text_result, "COPY:")
    cta = extract_section(text_result, "CTA:")
    hashtags = extract_section(text_result, "HASHTAGS:")
    
    st.markdown("### ✨ Resultados Gerados")
    
    # Diccionario para mapear las secciones a sus etiquetas visuales
    sections_dict = {
        "Título SEO": titulo,
        "Copy": copy,
        "CTA": cta,
        "Hashtags": hashtags
    }
    
    # Renderizado en cajas individuales con botón de copia nativo
    for label, content in sections_dict.items():
        if content:
            st.markdown(f"""
            <div class="output-box" style="margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;">
                <div class="box-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
            # El componente code de Streamlit incluye un botón nativo de "Copiar al portapapeles" en la esquina superior derecha
            st.code(content, language=None)
            st.markdown("<br>", unsafe_allow_html=True)
            
    st.markdown("---")
    
    # Botón para exportar a TXT (reemplaza tu función exportTXT en JS)
    st.download_button(
        label="⬇️ Exportar TXT",
        data=text_result,
        file_name="shopee_ads.txt",
        mime="text/plain",
        use_container_width=True
    )