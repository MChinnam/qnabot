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


#OPENAI_API_KEY="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"
from __init__ import template,url
"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"
logging.basicConfig(level=logging.INFO, format="%(asctime)s :[%(levelname)s]: %(message)s")
logging.StreamHandler(sys.stdout)



# import nltk
# import ssl

# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context

#nltk.download()

class OpenAQuestionAnswering:
    """
    OpenAI Question Answering
    """
    #OPENAI_API_KEY = "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"
    url=[]
    all_documents = []
    embeddings = None
    chain = None
    db=None

    def __init__(self, urls = []):
        """
        setting OpenAI environment variables
        :param urls:
        """
        try:
            #self.OPENAI_API_KEY = OPENAI_API_KEY
            #os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
            self.urls = urls
            self.embeddings = OpenAIEmbeddings()
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
    
    def load_chormadb(self):
        try:
            
            self.db = Chroma.from_documents(self.all_documents,self.embeddings)
        except Exception as ex:
            logging.error(f"Error while loading chormadb: {ex}")

    def load_data(self):
        try:
            self.load_urls()
            if len(self.all_documents)==0:
                logging.info("we don't have any documents to connect to openai")
                return
            #db = Chroma.from_documents(self.all_documents,self.embeddings)
            self.load_chormadb()
            chain_type_kwargs = {"prompt": self.prompt}
            self.chain = RetrievalQA.from_chain_type(
                llm=ChatOpenAI(temperature=0),
                chain_type="stuff",
                retriever=self.db.as_retriever(),
                chain_type_kwargs=chain_type_kwargs,
            )
            logging.info("Successfully loaded data to chromadb and connected to langchain")
        except Exception as ex:
            logging.error(f"Error while loading documents to chromadb or connecting to OpenAI: {ex}")
        return

    def query_data(self, query):
        defauult_output={}
        try:
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
        except Exception as ex:
            logging.error(f"Error while querying the data: {ex}")
        return "Error while query OpenAI"


# if __name__=='__main__':
#     # for chromadb installation export HNSWLIB_NO_NATIVE=1
#     openai_question_answer = OpenAQuestionAnswering(["https://www.fissionlabs.com/about-us"])
#     openai_question_answer.load_data()
#     print(openai_question_answer.query_data("Kishore Poreddy"))


