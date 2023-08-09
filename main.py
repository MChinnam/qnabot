import streamlit as st
import requests

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

endpoint = "https://sofibot-lang-service.cognitiveservices.azure.com/"
credential = AzureKeyCredential("eb18002e72554e339d86d333618d78b8")
knowledge_base_project = "Fission-sales"
deployment = "production"


def get_answer(question):
    client = QuestionAnsweringClient(endpoint, credential)
    with client:
        output = client.get_answers(
            question=question,
            project_name=knowledge_base_project,
            deployment_name=deployment
        )
        if output.answers:
            return output.answers[0].answer
        else:
            return "Sorry, I couldn't find an answer for your question."

def main():
    st.title("Azure QnA Maker Chatbot")

    user_query = st.text_input("Enter your question:")

    if st.button("Ask"):
        if user_query:
            answer = get_answer(user_query)
            st.text_area("Chatbot:", value=answer)

if __name__ == "__main__":
    main()

