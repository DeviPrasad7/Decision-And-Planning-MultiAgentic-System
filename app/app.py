import time
import chainlit as cl
from datetime import datetime
from collections import deque
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import Config
from core import init_router, CustomLLM
from tools import search_web

GLOBAL_ROUTER = init_router()

def get_realtime_info():
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    time_str = now.strftime("%I:%M %p")
    location = "Hyderabad, Telangana, India"
    return f"**Current Date:** {date_str}\n\n**Current Time:** {time_str}\n\n**Location:** {location}"

def get_contextual_input(user_input, memory):
    realtime_context = get_realtime_info()
    
    if not memory:
        return f"SYSTEM_CONTEXT:\n{realtime_context}\n\nUSER_REQUEST:\n{user_input}"
    
    history_str = "\n".join([f"User: {q}\nAI: {a}" for q, a in memory])
    
    return f"""SYSTEM_CONTEXT:
{realtime_context}

PREVIOUS CONVERSATION HISTORY:
{history_str}

CURRENT USER REQUEST:
{user_input}"""

def get_brain_decision(user_input, llm):
    tmpl = Config.load_prompt("router.txt")
    chain = PromptTemplate(template=tmpl, input_variables=["input"]) | llm | StrOutputParser()
    try:
        decision = chain.invoke({"input": user_input}).strip().upper()
        if "COMPLEX" in decision: return "COMPLEX"
        return "DIRECT"
    except:
        return "COMPLEX"

async def execute_complex_react(llm, plan, context, max_steps=4):
    history = ""
    executor_tmpl = Config.load_prompt("executor.txt")
    searched = set()

    for i in range(max_steps):
        prompt = executor_tmpl.format(plan=plan, context=context, history=history)
        
        response = await cl.make_async(llm.invoke)(prompt)
        response = response.content.strip()

        if "Final Answer:" in response:
            return response.split("Final Answer:")[-1].strip()

        if "Action: SEARCH" in response:
            try:
                if "Action Input:" in response:
                    query = response.split("Action Input:")[1].split("\n")[0].strip()
                else:
                    query = response.split("SEARCH")[1].strip()
                
                query = query.strip('"').strip("'")

                if query in searched:
                    history += f"\nSystem: Already searched '{query}'. Skip.\n"
                    continue
                
                with cl.Step(name="Search Tool", type="tool") as step:
                    step.input = query
                    searched.add(query)
                    res = await cl.make_async(search_web)(query)
                    step.output = res
                
                history += f"\nAgent: {response}\nSystem: {res}\n"
            except:
                history += f"\nSystem Error: Invalid Action Format.\n"
        else:
            history += f"\nAgent: {response}\n"
            if "Action:" not in response: return response

    return f"Context from Search Tools (Synthesize this): {history}"

async def process_request(query, memory):
    start_time = time.time()
    
    fast_llm = CustomLLM(router=GLOBAL_ROUTER, group="fast-tier")   
    smart_llm = CustomLLM(router=GLOBAL_ROUTER, group="smart-tier") 
    contextual_input = get_contextual_input(query, memory)

    task_list = cl.TaskList()
    task_list.status = "Running"
    
    task_brain = cl.Task(title="Brain: Routing", status=cl.TaskStatus.RUNNING)
    task_plan = cl.Task(title="Planner: Strategy", status=cl.TaskStatus.READY)
    task_exec = cl.Task(title="Executor: Action", status=cl.TaskStatus.READY)
    task_refine = cl.Task(title="Refiner: Polish", status=cl.TaskStatus.READY)

    await task_list.add_task(task_brain)
    await task_list.add_task(task_plan)
    await task_list.add_task(task_exec)
    await task_list.add_task(task_refine)
    await task_list.send()

    with cl.Step(name="Brain", type="llm") as step:
        step.input = query
        decision = await cl.make_async(get_brain_decision)(contextual_input, fast_llm)
        step.output = decision

    task_brain.status = cl.TaskStatus.DONE
    await task_list.send()

    if decision == "DIRECT":
        task_plan.status = cl.TaskStatus.DONE
        task_plan.title = "Planner: Skipped (Direct)"
        task_exec.status = cl.TaskStatus.DONE
        task_exec.title = "Executor: Skipped (Direct)"
        task_refine.status = cl.TaskStatus.DONE
        task_refine.title = "Refiner: Skipped (Direct)"
        await task_list.send()

        chain = PromptTemplate(template=Config.load_prompt("fast_lane.txt"), input_variables=["input"]) | fast_llm | StrOutputParser()
        res = await cl.make_async(chain.invoke)({"input": contextual_input})
        
        end_time = time.time()
        return f"{res}\n\n> ⏱️ **Response Time:** {end_time - start_time:.2f}s"

    task_plan.status = cl.TaskStatus.RUNNING
    await task_list.send()
    
    with cl.Step(name="Planner", type="llm") as step:
        step.input = contextual_input
        planner_chain = PromptTemplate(template=Config.load_prompt("planner.txt"), input_variables=["input"]) | smart_llm | StrOutputParser()
        plan = await cl.make_async(planner_chain.invoke)({"input": contextual_input})
        step.output = plan
    
    task_plan.status = cl.TaskStatus.DONE
    await task_list.send()

    task_exec.status = cl.TaskStatus.RUNNING
    await task_list.send()

    with cl.Step(name="Executor", type="run") as step:
        step.input = plan
        draft = await execute_complex_react(fast_llm, plan, contextual_input)
        step.output = draft

    task_exec.status = cl.TaskStatus.DONE
    await task_list.send()

    task_refine.status = cl.TaskStatus.RUNNING
    await task_list.send()

    with cl.Step(name="Refiner", type="llm") as step:
        step.input = draft
        refiner_chain = PromptTemplate(template=Config.load_prompt("refiner.txt"), input_variables=["draft_output"]) | smart_llm | StrOutputParser()
        res = await cl.make_async(refiner_chain.invoke)({"draft_output": draft})
        step.output = res
        
        task_refine.status = cl.TaskStatus.DONE
        task_list.status = "Done"
        await task_list.send()
        
        end_time = time.time()
        return f"{res}\n\n> ⏱️ **Response Time:** {end_time - start_time:.2f}s"

@cl.on_chat_start
async def start():
    cl.user_session.set("memory", deque(maxlen=3))
    
    realtime_info = get_realtime_info()
    
    await cl.Message(content="#  Sandwich Agent\n*System Online. Ready for queries.*").send()
    
    side_info = cl.Text(name="Mission Control", content=realtime_info, display="side")
    await cl.Message(content="", elements=[side_info]).send()

@cl.on_message
async def main(message: cl.Message):
    memory = cl.user_session.get("memory")
    
    msg = cl.Message(content="")
    await msg.send()
    
    res = await process_request(message.content, memory)
    
    memory.append((message.content, res))
    
    msg.content = res
    await msg.update()