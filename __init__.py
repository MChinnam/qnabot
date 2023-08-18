template = """Use the following pieces of context to answer the question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}

Please the provide the following in json JSON format with following keys answer and source_url."""

url=["http://fissionlabs.com/about-us"]
default_json = {
    "status": 400,
    "Message": 'success',
    "sessionId": 123,
    "question": "N/A",
    "answer": "N/A",
    "prompts": [],
    "confidence": 0.0,
    "source_url": "N/A",
    "source": "QnA",
}
