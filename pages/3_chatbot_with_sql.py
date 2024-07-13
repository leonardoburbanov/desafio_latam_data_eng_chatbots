import streamlit as st
from kafka import KafkaProducer
import json
import os
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import ChatOpenAI

# Kafka producer configuration
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

# SQLAlchemy and LangChain setup
engine = create_engine('postgresql+psycopg://testuser:testpwd@localhost:5432/vectordb')
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
db = SQLDatabase(engine)
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=False)

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
if prompt := st.chat_input("What's on your mind?"):
    # Append user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar='🧑‍💻'):
        st.markdown(prompt)

    # Send user message to Kafka
    send_to_kafka({"role": "user", "content": prompt})

    # Get response from SQL agent
    response = agent_executor.invoke(prompt)

    # Extract output from response and format it
    output = response["output"]
    
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(output)

    # Append assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": output})

    # Send assistant response to Kafka
    send_to_kafka({"role": "assistant", "content": output})

# Close Kafka producer
producer.close()
