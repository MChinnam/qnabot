import copy
from fastapi import FastAPI
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
import uvicorn
import logging
import sys
from pydantic import BaseModel
from OpenAIqa import OpenAQuestionAnswering
OpenAIqa=OpenAQuestionAnswering()
import os
os.environ["HNSWLIB_NO_NATIVE"] = '1'
logging.basicConfig(level=logging.INFO, format="%(asctime)s :[%(levelname)s]: %(message)s")
logging.StreamHandler(sys.stdout)


class Question(BaseModel):
    question:str

import os

def main():
    # Get the OpenAI API key from the environment variable
    openai_api_key = os.environ.get("OPENAI_API_KEY")

    if openai_api_key:
        print("OpenAI API Key:", openai_api_key)
        # Now you can use the 'openai_api_key' variable to make API calls or perform other tasks
        return openai_api_key
    else:
        print("OpenAI API Key is not set.")
        return "Ken not loaded"


app = FastAPI()


@app.get("/")
async def check_service():
    """
    Checking if service is up and running
    :return:
    """
    main()
    return {"status": 200, "message": "Service is up and running","KEY":main()}


# if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)
# #print(qa_instance.api_call("kishore poreddy"))
