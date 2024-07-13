import streamlit as st
from kafka import KafkaProducer
import json
import os
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
# Kafka producer configuration
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

# LangChain and RetrievalQA setup
CONNECTION_STRING = "postgresql+psycopg://testuser:testpwd@localhost:5432/vectordb"
COLLECTION_NAME = "startups_latam"
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

docsearch_load = PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=CONNECTION_STRING,
    use_jsonb=True,
)

# Prompt
template = """Utiliza el contexto para contestar.
Si no conoces la respuesta, contesta no sé. Trata de contestar en 3 oraciones máximo.

Contexto: {context}

Pregunta: {question}

Respuesta:"""
QA_CHAIN_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=template,
)

llm = ChatOpenAI(temperature=0.0, model='gpt-3.5-turbo')
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=docsearch_load.as_retriever(),
    chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to send message to Kafka topic
def send_to_kafka(message):
    producer.send("mytopic", value=message)

# Display messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input field for user message
if prompt := st.chat_input("Consulta desde SQL..."):
    # Append user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='🧑‍💻'):
        st.markdown(prompt)

    # Send user message to Kafka
    send_to_kafka({"role": "user", "content": prompt})

    # Get response from RetrievalQA
    result = qa_chain.run({"query": prompt})
    
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(result)

    # Append assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": result})

    # Send assistant response to Kafka
    send_to_kafka({"role": "assistant", "content": result})

# Close Kafka producer
producer.close()
