import streamlit as st
from openai import OpenAI
import os

# Configure sua chave de API da OpenAI
os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# Inicializa o cliente OpenAI
client = OpenAI()

# Inicializar o estado da sessão para armazenar histórico de chat e informações do thread
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Função para criar um novo thread
def create_thread():
    thread = client.beta.threads.create()  # Cria um novo thread
    print("Thread Criada:", thread)
    return thread.id  # Supondo que o objeto thread tenha um atributo id

# Função para criar e enviar uma mensagem do usuário
def create_message(thread_id, content):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content
    )
    print("Messagem Criada:", message)
    return message

# Função para criar e executar a solicitação para o assistant
def get_openai_assistant_response(thread_id, assistant_id, instructions):
    # Cria e executa o assistant usando o método novo
    print("Starting Assistant")
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=instructions
    )
    
    if run.status == 'completed':
        # Busca as mensagens se o status for completado
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages
    else:
        # Retorna o status se não foi completado
        return run.status

# Interface do chat no Streamlit
st.title("Papaki Chat Interface")

# Exibição do histórico de chat
if st.session_state.messages:
    for message in st.session_state.messages:
        st.write(message["role"] + ": " + message["content"])

# Exibe campo de entrada para o usuário
user_input = st.text_input("Digite sua mensagem e pressione Enter", value=st.session_state.user_input, key="user_input_input")

# Processa a entrada do usuário
if st.button('Enviar') and user_input:
    # Cria um thread se ele não existir
    if not st.session_state.thread_id:
        st.session_state.thread_id = create_thread()

    # Armazena a mensagem do usuário no estado da sessão
    st.session_state.messages.append({"role": "User", "content": user_input})
    
    # IDs para o thread e o assistant (substitua com o assistant ID real)
    thread_id = st.session_state.thread_id
    assistant_id = "asst_NtKDnspJ6Pm67EfP2kXE5m9o"  # Substitua pelo assistant ID real
    
    # Cria a mensagem do usuário
    create_message(thread_id, user_input)

    # Instruções para o assistant
    instructions = "Você é um analista de dados que trabalha em um grupo de publicidade chamado Papaki. Sua tarefa é ajudar a sumariazar dados de gastos da empresa."
    
    # Obtém a resposta do assistant usando o novo método
    response = get_openai_assistant_response(thread_id, assistant_id, instructions)
    
    # Verifica se a resposta é uma lista de mensagens ou apenas um status
    if isinstance(response, list):
        # Se for uma lista de mensagens, exibe-as
        for message in response:
            st.session_state.messages.append({"role": "Assistant", "content": message["content"]})
    else:
        # Se for um status, exibe o status
        st.session_state.messages.append({"role": "Assistant", "content": response.data[0].content[0].text.value})

    # Após o envio, limpa o campo de entrada
    st.session_state.user_input = ""

# Exibe o histórico de chat atualizado
if st.session_state.messages:
    for message in st.session_state.messages:
        st.write(message["role"] + ": " + message["content"])
