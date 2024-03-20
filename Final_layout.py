from types import ClassMethodDescriptorType
from click import prompt
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain import PromptTemplate
from langchain.chains import LLMChain
import streamlit as st
from streamlit_extras.let_it_rain import rain
import os
import time
import random 

#setting up the prerequites

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('openai_key')
llm = OpenAI(temperature = 0.8)
#llm2 = OpenAI(model_name = "gpt-4-turbo-preview", temperature = 0.7)

st.set_page_config(page_title="Test",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="collapsed")

rain(
    emoji="❄️",
    font_size=20,
    falling_speed=10,
    animation_length="infinite",
)

with open( "style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.markdown("<h1 style='text-align: center; color: white; text-decoration: underline; font-family: 'Times New Roman';'>SQL Generator</h1>", unsafe_allow_html=True)
col1 , col2 = st.columns([0.4,0.6], gap="large")

col1.header("Database Schema Input")
schema_input = col1.text_area("Submit Database Schema", height=450)
schema_submit_button = col1.button("Submit Schema", key="schema_submit")

col2.header("Enter your question")
user_prompt = col2.text_area("User's Prompt", height=150)
prompt_submit_button = col2.button("Submit Prompt", key="prompt_submit")

col2.markdown("---")

#query prompt
q_template = """You are an expert in writing SQL queries thus, based on the table schema below, 
write a SQL query that would answer the user's question:
{schema} \n Question: {user_prompt} \nSQL Query:"""

## Prompt Templates
first_input_prompt = PromptTemplate(
    input_variables = ['schema','user_prompt'],
    template = q_template
)

#query chain
chain1  = LLMChain(llm = llm, prompt = first_input_prompt, verbose=True, output_key='query')
########################

#scenario prompt
s_template = """Based on the following schema, generate 9 sql questions that 
are relevant to the schema. The questions should be in increasing order of difficulty and complexity.
Include atleast one problem which involves "join" operation. 
Just describe the problem statement in one line. Schema: {schema}  """

third_input_prompt = PromptTemplate(
    input_variables = ['schema'],
    template = s_template
)

#scenario chain
chain3 = LLMChain(llm = llm, prompt = third_input_prompt, verbose=True, output_key='scenario')

if schema_submit_button:
    with col1:
        with st.spinner('Wait for it...'):
            time.sleep(random.random() * 3)
        col1.success("Schema Submitted Successfully!!")
    
    
    expander = col1.expander("See Scenarios")
    scenarios = chain3({"schema": schema_input}, return_only_outputs=True)
    expander.write(scenarios["scenario"])
      

############################
    
#algorithm prompt
a_template = """You are an expert in explaining SQL queries thus
Explain the following SQL Query in an Algorithmic step-by-step fashion. Write "Start" and "End" to denote the begining 
and ending of the Algorithm. Write at least 4 lines and a maximum of 12 lines to explain.
Explain each step briefly, in a single line. Refer the below example.

Example : Start
1. Start by selecting distinct customer details and product application details.
2. Join the customers table with the life events table on customer id.
3. Join the resulting set with the products table on customer_id.
4. Filter for customers who are household heads.
5. Filter for customers located in California.
6. Filter for life events that include 'relocation'.
7. Filter for life events that occurred in the last 6 months.
8. Filter for product applications that include 'insurance'.
9. Filter for product applications that occurred in the last 6 months.
\n
End

Query: {query}"""

second_input_prompt = PromptTemplate(
    input_variables = ['query'],
    template = a_template
)

#algorithm chain
chain2  = LLMChain(llm = llm, prompt = second_input_prompt, verbose=True, output_key='algorithm')

if prompt_submit_button:
    with st.spinner('Generating response...'):
            qu = chain1({"schema": schema_input, "user_prompt":user_prompt}, return_only_outputs=True)
            #print(type(qu))
            col2.subheader("Query")
            col2.code(qu["query"], language="sql")
            #st.write(qu["query"])
            col2.markdown("---")
            col2.subheader("Algorithm")
            algo = chain2({"query": qu}, return_only_outputs=True)
            col2.write(algo["algorithm"])
            






