from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from dotenv import find_dotenv, load_dotenv
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)


load_dotenv(find_dotenv())

def answer_tech_question(user_input):

    chat = ChatOpenAI(model_name="grok-beta", temperature=1, base_url="https://api.x.ai/v1")

    template = """
    
    You are a tech expert and a helpful assistant that answer all tech question clear and in details.
    
    Your goal is to help the user to answer theirs questions, also help them to quickly and deeply understand the answer.
    
    Keep your reply in structure and details.

    Response must be in Slack Format.
        
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

    return response