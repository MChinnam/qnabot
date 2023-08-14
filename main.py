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

url=["http://fissionlabs.com/about-us",
"http://fissionlabs.com/case-studies/iot-driven-fleet-management-platform"]


openai_question_answer = OpenAQuestionAnswering(urls=url)
openai_question_answer.load_data()



class QuestionAnswering:
    """
    Question Answering using Azure QnA Maker API
    """
    # You should load this from config file as it's just for testing we have directly update it
    # It isn't a good practice when you scaling it as an API

    # azure endpoint
    endpoint = "https://sofibot-lang-service.cognitiveservices.azure.com/"

    # azure credentials
    credential = AzureKeyCredential("eb18002e72554e339d86d333618d78b8")

    # project name
    knowledge_base_project = "Fission-sales"

    # It's the default value
    deployment = "production"

    # It would be updated once we connect to Azure QnAmaker API
    client = None

    # we are setting default confidence please feel free to fine-tune
    confidence = None

    def __init__(self, confidence=0.5):
        """
        Azure client
        :param confidence:
        """
        try:
            self.client = QuestionAnsweringClient(self.endpoint, self.credential)
            self.confidence = confidence
            logging.info("Successully connected to azure qa client")
        except Exception as ex:
            logging.error(f"Error while connecting to Azure: {ex}")

    def extract_output(self,output):
        """
        Pre-processing extracted output from Azure QnAmaker API
        :param output:
        :return:
        """
        all_answers = []
        default_json = {"answer": "N/A", "prompts": [], "confidence":0.0, "source":"N/A", "source_url":"N/A"}
        try:
            # if you want only the one with max confidence when there are multiple answers
            # max_confidence = self.confidence
            for answer in output.answers:
                if answer.confidence>=self.confidence:
                    #creating a copy so they aren't using same variable
                    temp_json = copy.deepcopy(default_json)

                    temp_json["answer"] = str(answer.answer).strip()
                    temp_json["confidence"] = answer.confidence
                    temp_json["source"] = answer.metadata.get("source","N/A")
                    temp_json["source_url"] = answer.metadata.get("source_url", "N/A")
                    if temp_json["source_url"]!="N/A":
                        temp_json["source_url"] = temp_json["source_url"].replace("_com",".com").replace("@","/")
                    # Checking if you have any prompts
                    prompt_output = answer.dialog.prompts
                    if len(prompt_output) > 0:
                        temp_answer = ""
                        for prompt in prompt_output:

                            # appending points wrt header wrt streamlit to make it better on UI
                            temp_answer = str(prompt.display_text).strip()
                            if len(temp_answer) > 0:
                                ## If no prompt output don't append it to the final answer
                                temp_json["prompts"].append(temp_answer)
                    all_answers.append(temp_json)
            logging.info("Successfully extracted output\n")
            return all_answers
        except Exception as ex:
            logging.error(f"Error while extracting output: {ex}")
        return all_answers

    def get_output(self, question):
        """
        Retrieving the output of a question
        :param question:
        :return:
        """
        try:
            if self.client is None:
                return "Error while connecting to Azure bot"
            if type(question)!=str:
                return "Enter a valid intput"
            question = question.strip()
            if len(question)==0:
                return "enter a valid input"
            output = self.client.get_answers(
                question=question,
                project_name=self.knowledge_base_project,
                deployment_name=self.deployment
            )
            logging.info("Successfully retrieved output from azure environment")
            return self.extract_output(output)[0]
        except Exception as ex:
            logging.error(f"Error getting accessing answer: {ex}")
        return {}


    def api_call(self,question):
        resp=self.get_output(question)
        if len(resp)!=0:
            return resp
        else: 
            return openai_question_answer.query_data(question)



app = FastAPI()
qa_instance = QuestionAnswering()

@app.get("/")
async def check_service():
    """
    Checking if service is up and running
    :return:
    """
    return {"status": 200, "message": "Service is up and running"}


@app.post("/qa/")
async def generate_response(question:Question):
    prompt_items = []
    output = qa_instance.api_call(question.question)
    # answer = output["answers"][0].get("answer", "")
    # if output["answers"][0]["questions"]:
    #     prompts = output["answers"][0]["dialog"]["prompts"]
    #     source = output["answers"][0]["metadata"].get("source")
    # else:
    #     prompts = []
    #     source = None
    # for each_prompt in prompts:
    #     prompt_items.append(each_prompt.get('display_text'))
    # return {"answer": answer, "prompts":prompt_items, "source":source}
    
    return output

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
#     #print(qa_instance.api_call("kishore poreddy"))
