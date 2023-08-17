import os
import json
import copy
import logging
import sys
os.environ["HNSWLIB_NO_NATIVE"] = '1'
from langchain.document_loaders import url_selenium, WebBaseLoader

from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from __init__ import template,url

class OpenAQuestionAnswering:

    url=[]
    all_documents = []
    embeddings = None
    chain = None
    key=os.environ["OPENAI_API_KEY"]
    
    def __init__(self, urls=None):
        
        """
        setting OpenAI environment variables
        :param urls:
        """
        if urls is None:
            urls = []
        try:
            
            if self.key:
                logging.info("Successfully initialized OpenAI API Key environment variable")
            else:
                logging.warning("No API key provided. You should provide a valid API key.: {self.key}")
           
            
            self.urls = urls
            self.embeddings = OpenAIEmbeddings(openai_api_key=self.key)
            self.prompt = PromptTemplate(template=template, input_variables=["context", "question"])
            logging.info("Successfully initialized OpenAI Key Environment variable")
        except Exception as ex:
            logging.error(f"Error while setting OpenAI Key Environment variable: {ex}")
        return

    def load_urls(self):
        try:
            if len(self.urls) == 0:
                logging.info("No urls available")
                return
            case_studies_exists = False
            case_studies_url = "http://fissionlabs.com/case-studies"
            if case_studies_url in self.urls:
                self.urls.remove(case_studies_url)
                case_studies_exists = True
            if len(self.urls)>0:
                loader = url_selenium.SeleniumURLLoader(urls=self.urls)
                self.all_documents.extend(copy.deepcopy(loader.load()))
            if case_studies_exists:
                loader = WebBaseLoader(urls=self.urls)
                self.all_documents.extend(copy.deepcopy(loader.load()))
                self.urls.append(case_studies_url)
            logging.info(f"Successfully data: {len(self.all_documents)}")
        except Exception as ex:
            logging.error(f"Error while loading data: {ex}")
        return



    def load_data(self):
        try:
            self.load_urls()
            if len(self.all_documents)==0:
                logging.info("we don't have any documents to connect to openai")
                return
            db = Chroma.from_documents(self.all_documents,self.embeddings)
            chain_type_kwargs = {"prompt": self.prompt}
            self.chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(temperature=0,openai_api_key=self.key),
                chain_type="stuff",
                retriever=db.as_retriever(),
                chain_type_kwargs=chain_type_kwargs,
            )
            logging.info("Successfully loaded data to chromadb and connected to langchain")
        except Exception as ex:
            logging.error(f"Error while loading documents to chromadb or connecting to OpenAI: {ex}")

        return

    def query_data(self, query):
        defauult_output={}
        try:
            return self._extracted_from_query_data_4(query)
        except Exception as ex:
            logging.error(f"Error while querying the data: {ex}")
        return "Error while query OpenAI"

    # TODO Rename this here and in `query_data`
    def _extracted_from_query_data_4(self, query):
        if self.urls==0:
            return "No urls exists"
        if self.all_documents==0:
            return "Not able to load document using langchain Selenium loader"
        if self.chain is None:
            return "Not able to connect to OpenAI or failed to create chromdb"
        response = self.chain.run(query)
        output = json.loads(response)
        if output.get('source_url',"N/A")=="N/A":
            return "No answer found"
        #return output["Answer"]
        return output
# if __name__=='__main__':
#     # for chromadb installation export HNSWLIB_NO_NATIVE=1
#     openai_question_answer = OpenAQuestionAnswering(["https://www.fissionlabs.com/about-us"])
#     openai_question_answer.load_data()
#     print(openai_question_answer.query_data("Kishore Poreddy"))
