from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_models import BedrockChat
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import UnstructuredFileLoader
#from langchain.docstore.document import Document

from langchain_community.embeddings import BedrockEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PythonLoader
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
import faiss
import os



def get_llm():
        
    model_kwargs = { #anthropic
        "max_tokens": 4096,
        "temperature": 0, 
        "top_k": 250, 
        "top_p": 1, 
        "stop_sequences": ["\n\nHuman:"] 
    }
    
    llm = BedrockChat(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0", #set the foundation model
        model_kwargs=model_kwargs) #configure the properties for Claude
    
    return llm


embeddings = BedrockEmbeddings() #create a Titan Embeddings client
    
directory_path = '/home/ubuntu/environment/context-test/'
    
loader = DirectoryLoader(directory_path, glob="**/*.py", loader_cls=PythonLoader)
    
#file_path = "code_for_rag.txt" #assumes local PDF file with this name

#loader = TextLoader(file_path=file_path) #load the pdf file
"""
text_splitter = RecursiveCharacterTextSplitter( #create a text splitter
        separators=["\n\n", "\n", ".", " "], #split chunks at (1) paragraph, (2) line, (3) sentence, or (4) word, in that order
        chunk_size=1000, #divide into 1000-character chunks using the separators above
        chunk_overlap=100 #number of characters that can overlap with previous chunk
)
"""
python_splitter = RecursiveCharacterTextSplitter.from_language(
language=Language.PYTHON, chunk_size=1000, chunk_overlap=200
)
    
index_creator = VectorstoreIndexCreator( #create a vector store factory
    vectorstore_cls=FAISS, #use an in-memory vector store for demo purposes
    embedding=embeddings, #use Titan embeddings
    text_splitter=python_splitter, #use the recursive text splitter
)
    
file_indices = {}
for document in loader.load():
    texts = python_splitter.split_documents([document])
    file_index = index_creator.from_documents(texts)
    file_indices[document.metadata["source"]] = file_index

# Optionally, you can save the indices for each file
for file_path, file_index in file_indices.items():
    print(f"Indexing : {directory_path}/{os.path.basename(file_path)}/")
    file_index.vectorstore.save_local(f"{directory_path}/Indexes/{os.path.basename(file_path)}-Index/")

#index = index_creator.from_loaders([loader])
#faiss_vectorstore = index.vectorstore
#faiss.write_index(faiss_vectorstore.index, "/home/ubuntu/environment/context-test/faiss.index")
#faiss_vectorstore.save_local("/home/ubuntu/environment/context-test/")
#index_from_loader = index_creator.from_loaders([loader]).vectorstore.save_to_disk("/home/ubuntu/environment/context-test/vec-db") 
#create an vector store index from the loaded PDF

