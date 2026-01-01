import time
from collections import deque
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import Config
from core import init_router, CustomLLM
from tools import search_web

GLOBAL_ROUTER = init_router()

SHORT_TERM_MEMORY = deque(maxlen=3)

def get_contextual_input(user_input):
    if not SHORT_TERM_MEMORY:
        return user_input
    
    history_str = "\n".join([f"User: {q}\nAI: {a}" for q, a in SHORT_TERM_MEMORY])
    
    return f"""PREVIOUS CONVERSATION HISTORY:
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

def execute_complex_react(llm, plan, context, max_steps=4):
    history = ""
    executor_tmpl = Config.load_prompt("executor.txt")
    searched = set()

    for i in range(max_steps):
        prompt = executor_tmpl.format(plan=plan, context=context, history=history)
        
        response = llm.invoke(prompt).content.strip()

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
                
                print(f"   [Step {i+1} (Groq): Searching '{query}'...]")
                searched.add(query)
                res = search_web(query)

                history += f"\nAgent: {response}\nSystem: {res}\n"
            except:
                history += f"\nSystem Error: Invalid Action Format.\n"
        else:
            history += f"\nAgent: {response}\n"
            if "Action:" not in response: return response

    return f"Context from Search Tools (Synthesize this): {history}"

def process_request(query: str):
    fast_llm = CustomLLM(router=GLOBAL_ROUTER, group="fast-tier")   
    smart_llm = CustomLLM(router=GLOBAL_ROUTER, group="smart-tier") 

    decision = get_brain_decision(query, fast_llm)
    
    if decision == "DIRECT":
        print(f"   [Brain: DIRECT -> Routing to Groq]")
        chain = PromptTemplate(template=Config.load_prompt("fast_lane.txt"), input_variables=["input"]) | fast_llm | StrOutputParser()
        return chain.invoke({"input": query})

    print(f"   [Brain: COMPLEX -> Routing to Sandwich Agent]")
    
    print(">> 1. Planning (Gemini)...")
    planner_chain = PromptTemplate(template=Config.load_prompt("planner.txt"), input_variables=["input"]) | smart_llm | StrOutputParser()
    plan = planner_chain.invoke({"input": query})
    print(f"   Plan: {plan}")

    print(">> 2. Executing (Groq)...")
    draft = execute_complex_react(fast_llm, plan, query)

    print(">> 3. Refining (Gemini)...")
    refiner_chain = PromptTemplate(template=Config.load_prompt("refiner.txt"), input_variables=["draft_output"]) | smart_llm | StrOutputParser()
    return refiner_chain.invoke({"draft_output": draft})

def start():
    print(f"--- Hybrid Sandwich Agent Ready (With Memory) ---")
    print("--- Type 'q' to quit ---")
    while True:
        try:
            u_in = input("\n>> ").strip()
            if u_in.lower() in ["q", "quit", "exit"]: break
            if not u_in: continue
            
            contextual_input = get_contextual_input(u_in)

            start_t = time.time()
            res = process_request(contextual_input)
            end_t = time.time()
            
            SHORT_TERM_MEMORY.append((u_in, res))
            
            print(f"\n{res}\n[Time: {end_t-start_t:.2f}s]")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start()