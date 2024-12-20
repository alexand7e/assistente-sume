import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

# Page config
st.set_page_config(page_title="SIA Conectividade - Chat com Documentos", layout="wide", page_icon="🪴")

# API Key Management
def save_api_key(api_key):
    st.session_state["api_key"] = api_key

def load_api_key():
    return st.session_state.get("api_key", None)

# PDF Processing
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = "\n".join([page.extract_text() for page in reader.pages])
    return text

def load_instructions():
    try:
        with open("instructions.txt", "r", encoding='utf-8') as instructions_file:
            return instructions_file.read().strip()
    except FileNotFoundError:
        return "Você é um assistente de IA especializado em documentos."
    except Exception as e:
        st.error(f"Erro ao carregar instruções: {e}")
        return "Você é um assistente de IA especializado em documentos."

# Initialize instructions
system_instructions = load_instructions()

# Sidebar for configuration
with st.sidebar:
    st.title("Configurações")
    api_key = st.text_input("Groq API Key:", type="password", value=load_api_key())
    if api_key:
        save_api_key(api_key)
    
    uploaded_file = st.file_uploader("Upload documento PDF:", type=['pdf'])
    if uploaded_file:
        document_text = extract_text_from_pdf(uploaded_file)
        st.success("Documento processado com sucesso!")

# Main chat interface
st.title("Chat com Documentos")

# Initialize Groq
if api_key:
    try:
        client = Groq(api_key=api_key)
        st.success("Cliente Groq configurado com sucesso!")
    except Exception as e:
        st.error(f"Erro ao configurar o cliente Groq: {e}")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Digite sua mensagem:"):
    if api_key:
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
            
        # Add context if document is uploaded
        if 'document_text' in locals():
            context = f"Contexto do documento: {document_text}\n\nPergunta do usuário: {prompt}"
        else:
            context = prompt

        try:
            # Create chat completion with Groq
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": context}
                ],
            temperature=0.15,
            max_tokens=8192,
            top_p=0.17,
            stream=True,
            stop=None,
            )

            response_content = ""
            for chunk in completion:
                response_content += chunk.choices[0].delta.content or ""

            # Display assistant message
            with st.chat_message("assistant"):
                st.write(response_content)

            # Update chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.session_state.chat_history.append({"role": "assistant", "content": response_content})

        except Exception as e:
            st.error(f"Erro ao processar a mensagem: {e}")
    else:
        st.warning("Por favor, configure a API Key do Groq primeiro.")
