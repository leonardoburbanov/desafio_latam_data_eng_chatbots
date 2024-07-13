import streamlit as st
from kafka import KafkaProducer
import json
import os
from langchain.chains import ConversationChain
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory

# Kafka producer configuration
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

# OpenAI API client setup using LangChain
llm = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Conversation chain with memory
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

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

    # Get completion from OpenAI API using LangChain
    response = conversation.run(prompt)
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown(response)

    # Append assistant response to session state
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Send assistant response to Kafka
    send_to_kafka({"role": "assistant", "content": response})

# Close Kafka producer
producer.close()
