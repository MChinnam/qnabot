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
#from __init__ import default_json

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
class Question(BaseModel):
    question:str
    
url=["http://fissionlabs.com/about-us"]
# "http://fissionlabs.com/how-we-work",
# "http://fissionlabs.com/public-relations-csr",
# "http://fissionlabs.com/careers",
# "http://fissionlabs.com/contact-us",
# "http://fissionlabs.com/services/web-mobile-application-development-services",
# "http://fissionlabs.com/services/data-engineering-services",
# "http://fissionlabs.com/services/cloud-consulting-services",
# "http://fissionlabs.com/services/ai-ml-based-solutions",
# "http://fissionlabs.com/services/quality-assurance-services",
# "http://fissionlabs.com/services/salesforce-consulting-services",
# "http://fissionlabs.com/blog",
# "http://fissionlabs.com/case-studies",
# "https://www.fissionlabs.com/case-study/hospital-management-analytics-platform",
# "http://fissionlabs.com/case-study/ai-based-object-volume-estimator",
# "http://fissionlabs.com/case-study/multi-device-iot-communication-platform",
# "http://fissionlabs.com/case-study/realtime-health-records-monitoring-platform",
# "http://fissionlabs.com/case-study/fully-automated-managed-cloud-services-platform-for-healthcare-industry",
# "http://fissionlabs.com/case-study/advertising-sales-automation-workflow-platform"
# "https://www.fissionlabs.com/case-study/fleet-tracking-portal",
# "https://www.fissionlabs.com/case-study/pathology-radiology-e-learning-platform",
# "https://www.fissionlabs.com/case-study/enterprise-hrms-labour-analysis-platform",
# "http://fissionlabs.com/case-studies/integrated-campaign-management-platform",
# "http://fissionlabs.com/case-studies/workflow-management-platform",
# "http://fissionlabs.com/case-studies/iot-driven-fleet-management-platform",
# "http://fissionlabs.com/case-studies/life-science-and-regulatory-platform",
# "http://fissionlabs.com/case-studies/integrated-telehealth-platform",
# "http://fissionlabs.com/e-book-whitepapers",
# "http://fissionlabs.com/blog-posts/selecting-the-right-software-development-vendor-how-proof-of-concept-trials-can-help"]


openai_question_answer = OpenAQuestionAnswering(urls=url)
openai_question_answer.load_data()

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
    deployment = "productionii"

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
        
        try:
            # if you want only the one with max confidence when there are multiple answers
            # max_confidence = self.confidence
            for answer in output.answers:
                if answer.confidence>=self.confidence:
                    #creating a copy so they aren't using same variable
                    temp_json = copy.deepcopy(default_json)
                    temp_json['status']=200
                    temp_json['Message']="success"
                    temp_json["answer"] = str(answer.answer).strip()
                    temp_json["confidence"] = answer.confidence
                    #temp_json["source"] = answer.metadata.get("source","N/A")
                    
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
                            if temp_answer != "":
                                ## If no prompt output don't append it to the final answer
                                temp_json["prompts"].append(temp_answer)
                    all_answers.append(temp_json)
            logging.info("Successfully extracted output\n")
            return all_answers
        except Exception as ex:
            logging.error(f"Error while extracting output: {ex}")
            temp_json['status']=400
            temp_json['Message']=f"Error while extracting output: {ex}"
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
            if len(self.extract_output(output))>0:
                return self.extract_output(output)[0]
        except Exception as ex:
            logging.error(f"Error getting accessing answer: {ex}")
            default_json['status']=400
            default_json['Message']=f"Error getting accessing answer: {ex}"
        return {}
    
        


    def api_call(self,question):
        resp=self.get_output(question)
        return resp if len(resp)!=0 else openai_question_answer.query_data(question)




app = FastAPI()
qa_instance = QuestionAnswering()

#respp=qa_instance.api_call(question="service")

from datetime import datetime
#qa_instance.api_call(question="services")


@app.get("/")
async def check_service():
    """
    Checking if service is up and running
    :return:
    """
    return {"status": 200, "message": "Service is up and running"}



@app.post("/qa/")
async def generate_response(question:Question):
#     prompt_items = []
#     # respp=qa_instance.api_call(question.question)
#     # respp['question']=question.question
#     # respp['timestamp']=datetime.now().strftime("%m/%d/%YT%H:%M:%S.%f")
    
#     # return respp
    resp=qa_instance.get_output(question.question)
    if len(resp)!=0:
        resp['question']=question.question
        resp['timestamp']=datetime.now().strftime("%m/%d/%YT%H:%M:%S.%f")
        return resp
    else:
        return openai_question_answer.query_data(question.question)

        
        


# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
    #print(qa_instance.api_call("kishore poreddy"))
