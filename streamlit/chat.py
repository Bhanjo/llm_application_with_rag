import streamlit as st
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_classic import hub # langchain은 deprecated 됨
from langchain_classic.chains import RetrievalQA
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# page config
st.set_page_config(page_title="소득세 챗봇", page_icon=":money_with_wings:", layout="wide")
st.title("소득세 챗봇")
st.caption("소득세에 관련된 모든것을 대답해드립니다!")

# streamlit은 hotload 시 코드를 아예 다시 실행함. 즉, 이전 내용을 기억하지 못하기 때문에  session_state에 저장
if 'message_list' not in st.session_state:
    st.session_state['message_list'] = []

for message in st.session_state['message_list']:
    with st.chat_message(message['role']):
        st.write(message['content'])

def getAIMessage(user_message):
    embedding = OpenAIEmbeddings(model="text-embedding-3-large")
    index_name = "tax-index-markdown"
    # pinecone_api_key = os.environ.get("PINECONE_API_KEY")

    database = PineconeVectorStore.from_existing_index(
        embedding=embedding,
        index_name=index_name,
        # pinecone_api_key=pinecone_api_key,
    )

    llm = ChatOpenAI(model="gpt-4o")
    prompt = hub.pull('rlm/rag-prompt')
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=database.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )

    dictionary = ["사람을 나타내는 표현 -> 거주자"]

    prompt = ChatPromptTemplate.from_template(
        f"""
        사용자의 질문을 보고, 우리의 사전을 참고해서 사용자의 질문을 변경해주세요.
        만약 변경할 필요가 없다고 판단된다면, 사용자의 질문을 변경하지 않아도 됩니다.
        사전: {dictionary}
        사용자의 질문: {{question}}
        """
    )

    dictionary_chain = prompt | llm | StrOutputParser()
    tax_chain = {"query": dictionary_chain} | qa_chain
    return tax_chain.invoke({"question": user_message})['result']

if user_qeustion := st.chat_input(placeholder="소득세 관련 질문을 입력하세요!"):
    with st.chat_message("user"):
        st.write(user_qeustion)
    st.session_state['message_list'].append({"role": "user", "content": user_qeustion})

    with st.spinner("답변을 생성하는 중입니다."):
        ai_message = getAIMessage(user_qeustion)

    with st.chat_message('ai'):
        st.write(ai_message)
    st.session_state['message_list'].append({'role': 'ai', 'content': ai_message})

