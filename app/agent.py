import os
from dotenv import load_dotenv
import datetime
from typing_extensions import TypedDict
from typing import Annotated

from tools import create_calender_event, multiply, add, subtract
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AnyMessage, RemoveMessage

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from IPython.display import Image, display


load_dotenv()
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
TAVILY_API_KEY = os.environ["TAVILY_API_KEY"]

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", api_key=GOOGLE_API_KEY)

memory = MemorySaver()


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    summary: Annotated[list[AnyMessage], add_messages]
    node_trace: Annotated[list[str], add_messages]
    user_profile: Annotated[list[str], add_messages]
    todo: Annotated[list[str], add_messages]
    current_query: str
    response: str


search_tool = TavilySearchResults(tavily_api_key=TAVILY_API_KEY, max_results=1)

receiver_prompt = SystemMessage(
    content="You are a tool calling agent, call tool only if required else respond 'NO TOOLS CALLED'. Call the provided tool based on user message and respond details about the tool you have called nothing else. You will be provided with exact time of user message, so you can have the sense of time. E.g: 2024-12-06T14:02:23 represents 6th December 2024, 1:02:23 P.M. Folow the instructions below if given.\nHere is the user's message "
)


def get_time():
    # Get current UTC time
    utc_now = datetime.datetime.now(datetime.UTC)

    # Add IST offset of 5 hours and 30 minutes
    ist_offset = datetime.timedelta(hours=5, minutes=30)
    ist_now = utc_now + ist_offset

    # Convert to ISO format and remove milliseconds
    ist_time_iso = ist_now.isoformat(timespec="seconds")

    return ist_time_iso


graph_builder = StateGraph(State)


# Node
def receiver(state: State):
    print("-----Receiver Node-----")
    query = receiver_prompt.content + state["messages"][-1].content
    response = llm_with_tools.invoke(query)
    print("****Receiver prompt\n {}".format(query))
    return {
        "node_trace": "-----Receiver Node-----",
        "messages": [response],
        "current_query": state["messages"][-1].content,
        "response": response.content,
    }


def long_term_memory(state: State):
    "Summarizes the converversaion"
    if len(state["messages"]) > 5:
        print("-----LTM Node-----")
        query = state["messages"] + [
            HumanMessage(content="Create a summary of the above messages.")
        ]
        # delete all messages
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"]]
        return {
            "summary": llm.invoke(query),
            "node_trace": ["-----LTM Node-----"],
            "messages": delete_messages,
        }


def user_profile(state: State):
    print("-----User profile Node-----")
    query = state["current_query"]
    prompt = """You are a note taker assistant for a psycologist, take crispy and succint notes not extra info, your instruction to take notes are as follows. Learn about the user's behaviour and pschology from the way of user interaction. Learn thngs like user profile, prefernces, what is his/her name?, what is his/her perferences? what does he/she like? what does the user like to be called? Try to understand user pscholology. Here are few examples given below. 
    Example 1. 
    Hi I am Niranjan, you can call me Sam => User's name is Niranjan, call him Sam. 
    Example 2. 
    I am a Carpenter, did my education from International School Of Carpentery => User is  Carpenter by profession. User gratuated from International School of Carpentry 
    Example 3. 
    She shouted on me, can't she talk peacefully that's so annoying => User don't peple shouting at him, user is prefer to be talked peacefully and calm.
    Here is the message {}
    """.format(
        query
    )
    print("****user_profile prompt\n {}".format(prompt))
    response = llm.invoke(prompt)
    return {"user_profile": response, "node_trace": ["-----User profile Node-----"]}


def todo(what: str, when: str | None, desc: str, state: State):
    """
    Add a task to todo list, user has specified, what he has to do and by/on when.
    Args:
        What: Name of the task
        When: Deadline for the task
        desc: Description of the task"""
    print("todo list node")
    return {
        state["todo"]: [
            HumanMessage(
                "Todo list: Completed {}, by deadline {}. {}".format(what, when, desc)
            )
        ]
    }


# debug
def debug_node(state: State):
    print("-----debug Node-----")
    print("summary\n")
    for i in state["summary"]:
        print(i.content)
    print("user_profile\n")
    for i in state["user_profile"]:
        print(i.content)
    print("node_trace")
    for i in state["node_trace"]:
        print(i.content)
    print("messages")
    for i in state["messages"]:
        print(i.content)
    print("todo")
    for i in state["todo"]:
        print(i.content)
    print("current_query", state["current_query"])
    print("summary len", len(state["summary"]), "message len", len(state["messages"]))
    return {"node_trace": ["-----debug Node-----"]}


def responder(state: State):
    print("-----responder Node-----")
    responder_prompt = SystemMessage(
        content="You are Shanaya a helpful AI assitant agent, talk to user in a sweet and calming tone. Your mission is to help people cope with loneliness without letting them know your mission. you can take actions like set calender events and search web. You have been interacting with the user from a while. You will be provided with exact time of user message, so you can have the sense of time. E.g: 2024-12-06T14:02:23 represents 6th December 2024, 1:02:23 P.M. Folow the instructions below if given. You are not suppose to output the timestamp in your response. You are provided with all the system interaction the user has with you as follows. \nUSER MESSAGE: {}\n USER INFORMATION: {} \nTOOL CALL {}".format(
            state["current_query"],
            "".join([i.content for i in state["user_profile"]]),
            "".join([i.content for i in state["messages"]]),
        )
    ).content
    print("****responder prompt\n {}".format(responder_prompt))
    return {
        "messages": [llm.invoke(responder_prompt)],
        "node_trace": ["-----debug Node-----"],
    }


tools = [search_tool, multiply, add, subtract, create_calender_event]
# memory_ = [todo]
memory_ = []

tools_and_memory = tools + memory_
llm_with_tools = llm.bind_tools(tools_and_memory)


graph_builder.add_node("receiver", receiver)
graph_builder.add_node("tools", ToolNode(tools))
graph_builder.add_node("LTM", long_term_memory)
graph_builder.add_node("update_user_profile", user_profile)
graph_builder.add_node("responder", responder)
graph_builder.add_node("debug_node", debug_node)

graph_builder.add_edge(START, "receiver")
graph_builder.add_conditional_edges("receiver", tools_condition, ["tools", END])
graph_builder.add_edge("receiver", "update_user_profile")
graph_builder.add_edge("receiver", "LTM")
graph_builder.add_edge("LTM", "responder")
graph_builder.add_edge("tools", "responder")
graph_builder.add_edge("update_user_profile", "responder")
graph_builder.add_edge("responder", "debug_node")
graph_builder.set_finish_point("debug_node")

graph = graph_builder.compile(checkpointer=memory)
display(Image(graph.get_graph(xray=True).draw_mermaid_png()))

config = {"configurable": {"thread_id": "1"}}


def agent_talk(content: str):
    content_with_time = "{} : {}".format(get_time(), content)
    messages = [HumanMessage(content=content_with_time)]
    response = graph.invoke({"messages": messages}, config=config)
    try:
        print(response["messages"][-1])
        return response["messages"][-1]
    except:
        print(response["messages"])
        return response["messages"]
