from langchain.llms import OpenAIChat
import os
import streamlit as st
from common.ttc_utils import get_matches_carrier, get_best_matches_carrier, get_tasks_carrier
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.prompts import BaseChatPromptTemplate
from langchain import LLMChain
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, HumanMessage
import re
import openai

from langchain.callbacks import get_openai_callback

os.environ['OPENAI_API_KEY'] = "ef3be09daa914800ab7210a5c01256eb"

queryParams = st.experimental_get_query_params()

if 'carrier_uuid' not in st.session_state and queryParams['carrierId'] is not None:
    st.session_state['carrier_uuid'] = queryParams['carrierId'][0]


def get_matches(match_type):
    return get_matches_carrier(match_type)


def get_best_matches(match_type):
    return get_matches_carrier('best')


def get_tasks(carrier_id):
    return get_tasks_carrier()


# Set up the base template
template = """Complete the objective as best you can. Do not make up things. Get all valid input from the user.
if you don't have tools to find the answer, say you don't have the required tools to fullfill the request.
 You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

These were previous tasks you completed:



Begin!

Question: {input}
{agent_scratchpad}"""


# Set up a prompt template
class CustomPromptTemplate(BaseChatPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: List[Tool]

    def format_messages(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        formatted = self.template.format(**kwargs)
        return [HumanMessage(content=formatted)]


tools = [
    Tool(
        name="get matches",
        func=get_matches,
        description="This will get all my matches without checking best matches",
    ),
    # Tool(
    #     name="find my best matches",
    #     func=get_best_matches,
    #     description="This will get my best matches alone, should not use for all matches ot my matches",
    # ),
    Tool(
        name="get tasks",
        func=get_tasks,
        description="This will get my pending tasks",
    )
]

prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps"]
)

openai.api_type = os.getenv("OPENAI_API_TYPE") or "azure"
openai.api_base = os.getenv("OPENAI_API_BASE") or "https://trimblehackathon2023.openai.azure.com/"
openai.api_version = os.getenv("OPENAI_API_VERSION") or "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY") or "ef3be09daa914800ab7210a5c01256eb"
default_engine_name = os.getenv("OPENAI_ENGINE_NAME") or "gpt-35-turbo"
# Initiate our LLM - default is 'gpt-3.5-turbo'

llm = OpenAIChat(engine=default_engine_name, openai_api_key=openai.api_key,
                 openai_api_base=openai.api_base, temperature=0)

# LLM chain consisting of the LLM and a prompt
llm_chain = LLMChain(llm=llm, prompt=prompt)

# Using tools, the LLM chain and output_parser to make an agent
tool_names = [tool.name for tool in tools]


class CustomOutputParser(AgentOutputParser):

    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:

        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action: (.*?)[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)

        # If it can't parse the output it raises an error
        # You can add your own logic here to handle errors in a different way i.e. pass to a human, give a canned response
        if not match:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output},
                log=llm_output,
            )
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)


output_parser = CustomOutputParser()

agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    # We use "Observation" as our stop sequence so it will stop when it receives Tool output
    # If you change your prompt template you'll need to adjust this as well
    stop=["\nObservation:"],
    allowed_tools=tool_names
)

# Initiate the agent that will respond to our queries
# Set verbose=True to share the CoT reasoning the LLM goes through
# return_intermediate_steps=True
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True,
                                                    return_intermediate_steps=True, max_iterations=3)

st.sidebar.title("EngageLane APIs")

st.title("EngageLane APIs")

st.markdown(""" 
This agent has access to  tools,
1. get all matches
2. get all best matches
3. get all tasks

           
Few command that works ,
1. get matches, and show me in bullet points
2. get matches with best type, and show me in bullet points
3. get tasks, and show me in bullet points

""")

user_command = st.text_input("command", "get matches with best type, and show me in bullet points")

with get_openai_callback() as cb:
    agent_response = agent_executor(user_command)

st.markdown("#### Agent Response:")
st.write(agent_response['output'])
st.markdown("#### Agent Thought process:")

i = 1
# st.write(agent_response)
for thought in agent_response['intermediate_steps']:
    # Access the agent action and tool input
    agent_action = thought[0]
    # Print the agent action and tool input
    st.write(agent_action)

cost = cb.total_cost
st.sidebar.write("**The cost of this command execution is ${cost}**".format(cost=cost))
