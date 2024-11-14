from langchain.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

load_dotenv(find_dotenv())

def answer_tech_question(user_input, format = "Slack App"):

    chat = ChatOpenAI(model_name="grok-beta", temperature=, base_url="https://api.x.ai/v1")

    # chat = ChatGoogleGenerativeAI(
    #     model="gemini-1.5-pro",
    #     temperature=0,
    #     max_tokens=None,
    #     timeout=None,
    #     max_retries=2,
    # )


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
