This reference architecture is implemented with 3 main files. In actual scaled out production versions, the architecture can encompass various components as per the Well-Architected Frameworks. For example, this post the ingestion pipelines, LLM response module and the CARLA client are all running in a Cloud9 environment. In production use cases, these components should be running in different isolated components.

•	Claude3_rag_python_faiss_load.py  This contains the code for ingestion pipeline the document and context code to the RAG vector database with custom splitter.
•	Claude3_rag_python_faiss_stream.py  This contains code for the backend LLM invocation functions and the prompt enhancement modules.
•	Claude3_rag_python_app.py  This is the Streamlit application for the UI

1.	Ingestion Pipeline: Developers can store the context queries/ documentation, based on which the code will be generated. For this blog, the standard RAG technique with a custom splitter is used to store each query in a different in-memory index. Please refer the screenshot below:

![alt text](image1.png)


2.	Once the files have been stored into the Vector database, the next step is to enhance the prompt by combining user input with the tokens from the Vector database. In this post, we use Langchain to create a prompt template and specify the order of inputs and chat history, since we are building a conversational UI.

![alt text](image2.png)

3.	For this post, the front end is a simple Streamlit application which works as the UI for code generation. We also add a section for the validation part, which is a client to interact with the CARLA server and display the images output. For this post we are using a python script running on a docker container on the Cloud9 instance, which also provides the local file setup for storing and retrieving the generated images/ output files. For Production use cases, the UI and other components can be developed based on Well Architected framework. It could also only keep the code generation part as a separate UI and the Validation could be built separately depending on the use case – virtual CAN/ images produced here can be further uploaded to a S3 bucket for seamless access to further deep learning model trainings for autonomous driving and other use cases.

![alt text](image3.png)