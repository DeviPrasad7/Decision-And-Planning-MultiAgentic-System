# 🧠 Hybrid Sandwich Agent: Multi-Tiered Cognitive Architecture

## ⚡ Executive Summary

The **Hybrid Sandwich Agent** is a high-performance, multi-agentic system engineered to solve the **Latency-Accuracy Tradeoff** in Generative AI. By leveraging a **Cost-Based Routing Swarm**, the system dynamically orchestrates requests between ultra-low latency "Fast Tier" models and high-reasoning "Smart Tier" models.

This architecture implements a robust **Sandwich Pattern** (Plan → Execute → Refine), enabling complex Chain-of-Thought (CoT) reasoning for strategic tasks while maintaining **sub-second response times** for direct interaction.

## 🏗️ Architectural Internals

The application is structured around a modular architecture, with each file playing a specific role in the overall system.

### The Neural Core

- **Orchestration Engine:** `LangChain` + `LiteLLM` (Router)
- **Cognitive Layers:**
  - **🧠 Smart Tier (The Prefrontal Cortex):** Google Gemini 2.5 Flash / 2.5 Pro — Handles planning, synthesis, and error correction.
  - **⚡ Fast Tier (The Motor Cortex):** Groq (Llama-3.1-8b / 3.3-70b) — Handles execution, tool usage, and rapid response.
- **Memory Architecture:** Ephemeral Sliding Window (`deque`) with **Context Injection**, ensuring continuous state awareness with zero latency overhead.
- **Self-Healing Network:** Automated retry logic triggers failover protocols (Groq ↔ Gemini Flash) upon rate-limit detection (429 / Quota Exceeded).

### File Descriptions

- **`main.py`**: The entry point for the command-line version of the agent. It initializes the agent and enters a loop to process user input from the console.
- **`app.py`**: The entry point for the Chainlit-based web interface. It uses the `chainlit` library to provide a chat interface for interacting with the agent.
- **`core.py`**: The core of the agent's architecture. It initializes the `litellm` router, which manages a pool of language models. It also defines the `CustomLLM` class, a LangChain-compatible wrapper around the `litellm` router that allows for dynamic model selection based on the task's complexity.
- **`tools.py`**: Defines the tools available to the agent. Currently, it includes a `search_web` function that uses the Tavily or DuckDuckGo API to search the web for information.
- **`config.py`**: Manages the application's configuration. It loads API keys from a `.env` file and loads the prompt templates from the `prompts` directory.
- **`.env.example`**: An example of the `.env` file required to run the application. It lists the environment variables that need to be set, such as API keys for the language models and search tools.
- **`chainlit.md`**: A markdown file that is displayed in the Chainlit UI, providing an overview of the agent and its capabilities.

### The "Sandwich" Pattern: Plan → Execute → Refine

The agent uses a three-step process to handle complex requests:

1.  **Plan:** The "Planner" agent, using a "smart tier" model, creates a high-level plan to address the user's request.
2.  **Execute:** The "Executor" agent, using a "fast tier" model, executes the plan. This may involve using tools like the web search tool to gather information.
3.  **Refine:** The "Refiner" agent, using a "smart tier" model, polishes the output from the Executor to provide a clean and professional response.

This "Sandwich" pattern allows the agent to leverage the strengths of both "smart" and "fast" models, resulting in a system that is both accurate and responsive.

### Prompts

The `prompts` directory contains the prompt templates for each of the agents in the system:

- **`router.txt`**: The prompt for the "Router" agent, which classifies incoming requests as "DIRECT" or "COMPLEX".
- **`planner.txt`**: The prompt for the "Planner" agent, which creates a high-level plan for complex requests.
- **`executor.txt`**: The prompt for the "Executor" agent, which executes the plan and uses tools to gather information.
- **`fast_lane.txt`**: The prompt for "DIRECT" requests that are handled by the "fast tier" model.
- **`refiner.txt`**: The prompt for the "Refiner" agent, which polishes the final output.

## 🛠️ Quick Start & Installation

Setting up the agent is streamlined. Copy the code block below relevant to your OS to create the environment, install dependencies, and launch the neural core.

### 💻 For Windows (PowerShell)

*Copy and paste this entire block into PowerShell:*

```powershell
# 1. Create and Activate Virtual Environment
python -m venv venv
.\venv\Scripts\Activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Enter Application Directory and Launch with Chainlit UI
cd app
chainlit run app.py -w
```

### 🐧 For Linux / MacOS (Bash)

*Copy and paste this entire block into your terminal:*

```bash
# 1. Create and Activate Virtual Environment
python3 -m venv venv && source venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Enter Application Directory and Launch with Chainlit UI
cd app && chainlit run app.py -w
```

> **Note:** Ensure you have your `.env` file configured with `GEMINI_KEY_1` , `GROQ_API_KEY` and `TAVILY_API_KEY` before running.
> (all are free of cost and do not require any credit card details, only google account is enough, do not encourage false websites, i will also add the original links below to get the api keys).
>
> https://aistudio.google.com/api-keys --> gemini api key
>
> https://console.groq.com/keys --> groq api key
>

> https://app.tavily.com/home --> tavily api key

## 💡 Cost & Resource Strategy (Free-Tier Optimized)

This project is intentionally engineered to operate at **zero infrastructure cost**, leveraging **free-tier models** and resources exclusively during the Alpha phase. To achieve reliability, throughput, and fault tolerance under free-tier constraints, the system employs a **multi-key load-balancing** strategy.

**Multiple API keys**—provisioned across separate Google accounts—are rotated and dynamically balanced to distribute request load, mitigate rate limits, and maintain uninterrupted service availability. This approach enables real-world stress testing of agentic orchestration, routing logic, and failover behavior without incurring any paid usage, while closely simulating production-scale traffic patterns.

This design choice reinforces the project’s goals of:

- Cost-efficiency by design
- Resilience under constrained resources
- Realistic LLMOps experimentation without financial overhead

## 🔮 Roadmap & Future Evolution

This project is currently in **Alpha Phase**. The monolithic core is being actively decoupled into a scalable microservices architecture.

- **🌐 API Exposure (FastAPI):** Transitioning project into a high-concurrency RESTful API to serve as a backend for web and mobile clients.
- **☁️ Cloud Native (GCP):** Containerization (Docker) and deployment to Google Cloud Run for serverless auto-scaling and high availability.
- **🖥️ Real-Time Interface (React):** Developing a "Glass Box" UI to visualize the agent's "Thinking Process" (Plan → Execute → Refine) in real time.
- **📚 Long-Term Memory (RAG):** Integration with Vector Databases (Pinecone / Faiss) to persist user context beyond the current session.

## 👨‍💻 Engineering Standards

Engineered with a focus on **High Availability (HA)** and **Large Language Model Operations (LLMOps)**.

- **Pattern:** Agentic Workflow (Router–Solver).
- **Reliability:** Exponential Backoff & Multi-Key Rotation.
- **Observability:** Verbose console logging for "Brain State" tracking.
