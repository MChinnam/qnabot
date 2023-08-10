from fastapi import Depends, FastAPI

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from pydantic import BaseModel

class Question(BaseModel):
    question:str


class QuestionAnswering:
    endpoint = "https://sofibot-lang-service.cognitiveservices.azure.com/"
    credential = AzureKeyCredential("eb18002e72554e339d86d333618d78b8")
    knowledge_base_project = "Fission-sales"
    deployment = "production"
    client = None

    def __init__(self):
        try:
            self.client = QuestionAnsweringClient(self.endpoint, self.credential)
        except Exception as ex:
            print(f"Error while connecting to Azure: {ex}")

    def get_output(self, question):
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
            return output.as_dict()
        except Exception as ex:
            raise ValueError(f"Error getting accessing answer: {ex}")
        raise ValueError("Error getting answer")

app = FastAPI()
qa_instance = QuestionAnswering()

@app.post("/qa/")
async def generate_response(question:Question):
    prompt_items = []
    output = qa_instance.get_output(question.question)
    answer = output["answers"][0].get("answer", "")
    if output["answers"][0]["questions"]:
        prompts = output["answers"][0]["dialog"]["prompts"]
        source = output["answers"][0]["metadata"].get("source")
    else:
        prompts = []
        source = None
    for each_prompt in prompts:
        prompt_items.append(each_prompt.get('display_text'))
    return {"answer": answer, "prompts":prompt_items, "source":source}
