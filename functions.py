import os
import json
# from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv(find_dotenv())

def answer_tech_question(user_input, model):

    print(model)

    chat = ChatOpenAI(model_name="grok-beta", temperature=0, base_url="https://api.x.ai/v1") if model == "Grok" else ChatGoogleGenerativeAI(
                    model="gemini-1.5-pro",
                    temperature=0,
                    max_tokens=None,
                    timeout=None,
                    max_retries=2,
                )


    template = f"""
    
    You are a tech expert and a helpful assistant that answer all tech question clear and in details.
    
    Your goal is to help the user to answer theirs questions, also help them to quickly and deeply understand the answer.
    
    Keep your reply in structure and details.

    Please respond in normal plane_text format with below rule (and do not apply any another rules which not described below)

    bold: please use *this text is bold*
    *Section header*
    '1 tab - 4 space'◦ Sub-section header
    '2 tabs - 8 spaces - Paragraph
    ```source_code```

    Make sure to include additional consideration points at the end.
    
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    human_template = "{user_input}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = LLMChain(llm=chat, prompt=chat_prompt)
    response = chain.run(user_input=user_input)

    return response.replace("**", "*")  # for Grok, remove **


def answer_with_history(user_input, history_data, model="Grok"):
    """
    Answers a user's question based on the provided history data.

    Args:
        user_input (str): The user's question.
        history_data (list): A list of strings representing the history data.
        model (str, optional): The LLM model to use. Defaults to "Grok".

    Returns:
        str: The answer to the user's question.
    """

    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    print("|| ".join(history_data))  # Print the history data separated by "||"

    # Create a vectorstore from the history data using Google Generative AI Embeddings
    vectorstore = FAISS.from_texts(history_data, embedding=embedding)
    retriever = vectorstore.as_retriever()  # Create a retriever from the vectorstore

    print(retriever)  # Print the retriever object

    system_template = f"""
    
    You are a highly skilled software engineer with extensive knowledge in many programming languages, frameworks, design patterns, and best practices.
    
    You are also a helpful assistant that answer all questions clearly.
    
    Your goal is to help the user to answer theirs questions, also help them to quickly understand the answer.
    
    Keep your reply in structure, easy to understand but not too details.

    Please respond in normal plane_text format with below rule (and do not apply any another rules which not described below)

    bold: please use *this text is bold*
    *Section header*
    '1 tab - 4 space'◦ Sub-section header
    '2 tabs - 8 spaces - Paragraph
    ```source_code```
    
    """

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)


    # Define the prompt template
    human_template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """

    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    # prompt = ChatPromptTemplate.from_template(human_template)

    # Initialize the chat model based on the selected model
    chat = ChatOpenAI(model_name="grok-beta", temperature=0, base_url="https://api.x.ai/v1") if model == "Grok" else ChatGoogleGenerativeAI(
        model="gemini-1.5-pro",
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )

    # Create the retrieval chain
    retrieval_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | chat
        | StrOutputParser()
    )

    # Invoke the retrieval chain with the user input
    response = retrieval_chain.invoke(user_input)
    return response

