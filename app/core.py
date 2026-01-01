from typing import Any, List, Optional
from litellm.router import Router
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import Field
from config import Config

def init_router():
    if not Config.GEMINI_KEYS:
        raise ValueError("No GEMINI_KEYS variables found in .env")

    model_list = []

    for key in Config.GEMINI_KEYS:
        for model in Config.SMART_MODELS:
            model_list.append({
                "model_name": "smart-tier",
                "litellm_params": {
                    "model": model,
                    "api_key": key,
                    "temperature": 0.1,
                    "top_p": 0.1,
                    "order": 1
                }
            })

    if Config.GROQ_KEY:
        for model in Config.FAST_MODELS:
            model_list.append({
                "model_name": "fast-tier",
                "litellm_params": {
                    "model": model,
                    "api_key": Config.GROQ_KEY,
                    "temperature": 0.1,
                    "top_p": 0.1,
                    "order": 1
                }
            })
    
    for key in Config.GEMINI_KEYS:
        model_list.append({
            "model_name": "fast-tier",
            "litellm_params": {
                "model": "gemini/gemini-2.5-flash",
                "api_key": key,
                "temperature": 0.1,
                "top_p": 0.1,
                "order": 2
            }
        })

    print(f"--- Initialized Router with {len(model_list)} endpoints ---")

    return Router(
        model_list=model_list,
        routing_strategy="simple-shuffle",
        num_retries=len(model_list),
        allowed_fails=len(model_list),
        timeout=40,
    )

class CustomLLM(BaseChatModel):
    router: Any = Field(...)
    group: str = Field(...)
    
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None) -> ChatResult: #type:ignore
        formatted = [{"role": "user", "content": m.content} for m in messages if isinstance(m, HumanMessage)]
        if not formatted:
            formatted = [{"role": "user", "content": messages[-1].content}]
        
        try:
            response = self.router.completion(
                model=self.group, 
                messages=formatted
            )
            content = response.choices[0].message.content
            
            if content and ("Quota Exceeded" in content or "429" in content):
                raise Exception("RateLimit: Quota Exceeded")

            final = content if content else "Error: Empty response."
        except Exception as e:
            final = f"System Alert: All models failed. Last Error: {str(e)}"
            
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=final))])
    
    @property
    def _llm_type(self) -> str:
        return "hybrid_router"