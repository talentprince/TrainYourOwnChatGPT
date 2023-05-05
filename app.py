from llama_index import SimpleDirectoryReader, ServiceContext, GPTVectorStoreIndex, LLMPredictor, PromptHelper, StorageContext, load_index_from_storage
from langchain.chat_models import ChatOpenAI
import gradio as gr
import sys
import os

os.environ["OPENAI_API_KEY"] = '<your key>'

def construct_index(directory_path):
    max_input_size = 4096
    num_outputs = 512
    max_chunk_overlap = 20
    chunk_size_limit = 600

    prompt_helper = PromptHelper(max_input_size, num_outputs, max_chunk_overlap, chunk_size_limit=chunk_size_limit)

    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo", max_tokens=num_outputs))

    documents = SimpleDirectoryReader(directory_path).load_data()

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

    index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)

    index.storage_context.persist(persist_dir='index.json')

    return index

def chatbot(input_text):
    storage_context = StorageContext.from_defaults(persist_dir="index.json")
    index = load_index_from_storage(storage_context)
    query_engine = index.as_query_engine()
    response = query_engine.query(input_text)
    return response

iface = gr.Interface(fn=chatbot,
                     inputs=gr.components.Textbox(lines=7, label="Enter your text"),
                     outputs="text",
                     title="Custom-trained AI Chatbot")

construct_index("docs")
iface.launch(share=True)