from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient

import logging
import sys
# import streamlit as st
# from streamlit_chat import message

logging.basicConfig(level=logging.INFO, format="%(asctime)s :[%(levelname)s]: %(message)s")
logging.StreamHandler(sys.stdout)

class QuestionAnswering:
    """
    Question Answering using Azure QnA Maker API
    """
    # You should load this from config file as it's just for testing we have directly update it
    # It isn't a good practice when you scaling it as an API

    # azure endpoint
    endpoint = "https://sofibot-lang-service.cognitiveservices.azure.com/"

    # azure credentials, please update credentials
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
            # logging.info("Checking loggers")
            logging.info("Successully connected to azure qa client")
        except Exception as ex:
            logging.error(f"Error while connecting to Azure: {ex}")

    def extract_output(self,output):
        """
        Pre-processing extracted output from Azure QnAmaker API
        :param output:
        :return:
        """
        final_answer = ""
        try:
            # if you want get only the one with max confidence when there are multiple answers
            # max_confidence = self.confidence
            for answer in output.answers:
                if answer.confidence>=self.confidence:

                    ### Headers wrt Streamlit UI
                    final_answer += "###### "+str(answer.answer)+"\n"

                    # Checking if you have any prompts
                    prompt_output = answer.dialog.prompts
                    if len(prompt_output) > 0:
                        temp_answer = ""
                        for prompt in prompt_output:

                            # appending points wrt header wrt streamlit to make it better on UI
                            temp_answer += "* "+str(prompt.display_text)+"\n"
                        if len(temp_answer) > 0:
                            ## If no prompt output don't append it to the final answer
                            final_answer += temp_answer + "\n\n"
            if len(final_answer)==0:
                final_answer = "No answer found"
            logging.info("Successfully extracted output\n")
            return final_answer
        except Exception as ex:
            logging.error(f"Error while extracting output: {ex}")
        return "Error while extracting output"

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
            return self.extract_output(output)
        except Exception as ex:
            logging.error(f"Error getting accessing answer: {ex}")
        return "Error getting answer"


if __name__=='__main__':
    """
    in case if you wanna test the QnA Maker
    """
    try:
        qa_instance = QuestionAnswering()
        logging.info(qa_instance.get_output("services?"))
        logging.info("Successfully the main method is working")
    except Exception as ex:
        logging.error(f"Error while accessing main methoed {ex}")
