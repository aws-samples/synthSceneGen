from langchain.memory import ConversationBufferMemory
from langchain_community.chat_models import BedrockChat
from langchain.chains import ConversationalRetrievalChain
from langchain.chains import ConversationChain
from langchain_core.prompts import PromptTemplate
from langchain.schema import HumanMessage, AIMessage

from langchain_community.embeddings import BedrockEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PythonLoader
import faiss
import os





def get_llm(streaming_callback):
        
    model_kwargs = { #anthropic
        "max_tokens": 4096,
        "temperature": 0, 
        "top_k": 250, 
        "top_p": 1, 
        "stop_sequences": ["\n\nHuman:"]
    }
    
    llm = BedrockChat(
        model_id="anthropic.claude-3-sonnet-20240229-v1:0", #set the foundation model
        model_kwargs=model_kwargs,
        streaming=True,
        callbacks=[streaming_callback],
        ) #configure the properties for Claude
    
    return llm

def get_memory(): #create memory for this chat session
    
    memory = ConversationBufferMemory(memory_key="history", return_messages=True) #Maintains a history of previous messages
    #memory = ConversationBufferWindowMemory(memory_key="chat_history", k=2)
    #memory = ConversationBufferWindowMemory(k=2)
    return memory

def get_rag_chat_response(input_text, memory, streaming_callback): #chat client function
    
    llm = get_llm(streaming_callback)
    embeddings = BedrockEmbeddings()
    #vectorstore = FAISS.load_local("/home/ubuntu/environment/context-test/", embeddings, allow_dangerous_deserialization=True)
    directory_path = '/home/ubuntu/environment/context-test/'

    # Load the indexes
    loaded_indices = {}
    for file_path in os.listdir(os.path.join(directory_path, 'Indexes')):
        if file_path.endswith('-Index'):
            index_path = os.path.join(directory_path, 'Indexes', file_path)
            vectorstore = FAISS.load_local(index_path, embeddings,allow_dangerous_deserialization=True)
            loaded_indices[file_path[:-6]] = vectorstore
    
    #search_results = vectorstore.similarity_search_with_score(input_text, k=5)
    all_search_results = []
    for vectorstore in loaded_indices.values():
        search_results = vectorstore.similarity_search_with_score(input_text,k=5)
        all_search_results.extend(search_results)

    # Extract the Document objects and join their page_content
    context = "\n".join([doc.page_content for doc, _ in all_search_results])

    history_messages = memory.load_memory_variables({})["history"]
    history = "\n".join([
        f"Human: {msg.content}" if isinstance(msg, HumanMessage) else f"Assistant: {msg.content}"
        for msg in history_messages
    ])
    
    template = """
        Refer to the code mentioned here. DO NOT DO ANYTHING unless asked.
        {context}
        Based on the {context}, Modify or Write high-quality python script for the following task, something a Carla 0.9.13 python expert would write. 
        You are writing code for an experienced developer so only add comments for things that are non-obvious. Make sure to include any imports required.
        Any comments or explanation should be commented as per the programming language.

        
        Current conversation:
        {history}
        Human: DO NOT DO ANYTHING unless asked.{input}
        Assistant:
        """
    
    #final_template = "Human: Refer to the code below. Do not analyse it until asked."+"\n"+context+"\n"+template
    
    prompt_template = PromptTemplate.from_template(template).partial(context=context)

    conversation_with_retrieval = ConversationChain( #create a chat client
        llm = llm, #using the Bedrock LLM
        memory=memory, #with the summarization memory
        verbose = True, #print out some of the internal states of the chain while running
        #combine_docs_chain_kwargs={"prompt": get_prompt(input_text)}
        prompt = prompt_template
    )
    
    conversation_with_retrieval.prompt = prompt_template
    chat_response = conversation_with_retrieval.invoke(input=input_text) #pass the user message and summary to the model
    
    return chat_response['response']
