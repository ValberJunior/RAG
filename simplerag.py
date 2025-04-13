#!/usr/bin/env python
# coding: utf-8

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
import os
import json

OPEN_AI_API_KEY = os.environ["OPENAI_API_KEY"]

# Load models

embeddings_model = OpenAIEmbeddings()
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    max_tokens=200
)


def loadData():
    # Load PDF
    pdf_link = 'Lei_geral_protecao_dados_pessoais_1ed.pdf'
    loader = PyPDFLoader(pdf_link, extract_images=False)
    pages = loader.load_and_split()  
    # Separar em Chunks (Pedaços de documento)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000,
        chunk_overlap=20,  # Número de palavras que se sobrepõem entre os chunks
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(pages)  # Separar o documento em pedaços
    # Salvar no vector DB
    vectordb = Chroma.from_documents(chunks,embeddings_model)  
    # Load Retriever (buscador)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})  # k = número de documentos retornados
    return retriever


def getRelevantDocs(question):
    retriever = loadData()
    context = retriever.invoke(question) 
    return context  # Pega os documentos relevantes


def ask(question,llm):
    TEMPLATE="""
    Você é um especialista sobre a Lei Geral de Proteção de Dados Pessoais (LGPD) no Brasil.
    Responda a pergunta abaixo utilizando o contexto informado;
    Contexto: {context}
    Pergunta: {question}
    """
    prompt = PromptTemplate(
        input_variables=["contexto", "question"],
        template=TEMPLATE
    )
    sequence = RunnableSequence(prompt | llm)
    context = getRelevantDocs(question)  # Pega os documentos relevantes
    response = sequence.invoke({
        "context": context,
        "question": question
    })
    return response


# lambda function AWS
def lambda_handler(event, context):
    # query = event.get('question')
    body = json.loads(event.get('body'),{})
    query = body.get('question')
    if not query:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing question parameter'})
        }
    response = ask(query, llm).content
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': 'Tarefa concluída com sucesso',
            'details': response
        })
    }