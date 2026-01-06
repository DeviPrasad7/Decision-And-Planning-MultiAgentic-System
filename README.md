# 🧠 Hybrid Sandwich Agent: Multi-Tiered Cognitive Architecture

![Status](https://img.shields.io/badge/Status-Under_Development-orange?style=for-the-badge\&logo=statuspage)
![Architecture](https://img.shields.io/badge/Architecture-Hybrid_Sandwich_Pattern-purple?style=for-the-badge\&logo=moleculer)
![Latency](https://img.shields.io/badge/Latency_Target-0.75s_--_35s-success?style=for-the-badge\&logo=speedtest)
![Stack](https://img.shields.io/badge/Tech_Stack-LangChain_|_LiteLLM_|_GoogleAI_|_Groq-blue?style=for-the-badge\&logo=python)

---

## ⚡ Executive Summary

The **Hybrid Sandwich Agent** is a high-performance, multi-agentic system engineered to solve the **Latency-Accuracy Tradeoff** in Generative AI. By leveraging a **Cost-Based Routing Swarm**, the system dynamically orchestrates requests between ultra-low latency "Fast Tier" models and high-reasoning "Smart Tier" models. Hosted on Google cloud run , allowing high serverless scalability and robust performance.

This architecture implements a robust **Sandwich Pattern** (Plan → Execute → Refine), enabling complex Chain-of-Thought (CoT) reasoning for strategic tasks while maintaining **sub-second response times** for direct interaction.

---

### 🚀 Performance Metrics

| Metric                   | Benchmark        | Description                                                |
| :----------------------- | :--------------- | :--------------------------------------------------------- |
| **Direct Path Latency**  | **~0.75s (P99)** | Instant routing via Llama-3-8b for high-speed interaction. |
| **Complex Path Latency** | **~45.0s (Avg)** | Full "Plan-Execute-Refine" cycle with deep reasoning (Can be more based on query)     |
| **Throughput**           | **Auto-Scaling** | Dynamic load balancing across multiple models and API keys on all free tier models.           |

---

## 🏗️ Architectural Internals

### The Neural Core

* **Orchestration Engine:** `LangChain` + `LiteLLM` (Router)
* **Cognitive Layers:**

  * **🧠 Smart Tier (The Prefrontal Cortex):** Google Gemini 2.5 Flash / 2.5 Pro — Handles planning, synthesis, and error correction.
  * **⚡ Fast Tier (The Motor Cortex):** Groq (Llama-3.1-8b / 3.3-70b) — Handles execution, tool usage, and rapid response.
* **Memory Architecture:** Ephemeral Sliding Window (`deque`) with **Context Injection**, ensuring continuous state awareness with zero latency overhead.
* **Self-Healing Network:** Automated retry logic triggers failover protocols (Groq ↔ Gemini Flash) upon rate-limit detection (429 / Quota Exceeded).

---

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

# 3. Enter Application Directory and Launch
cd app
chainlit run app.py -w
```

---

### 🐧 For Linux / MacOS (Bash)

*Copy and paste this entire block into your terminal:*

```bash
# 1. Create and Activate Virtual Environment
python3 -m venv venv && source venv/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Enter Application Directory and Launch
cd app && chainlit run app.py -w
```

> **Note:** Ensure you have your `.env` file configured with `GEMINI_KEY_1` , `GROQ_API_KEY` and `TAVILY_API_KEY` before running.
> 
>  (all are free of cost and do not require any credit card details, only google account is enough, do not encourage false websites, i will also add the original links below to get the api keys).
>
> https://aistudio.google.com/api-keys   --> gemini api key
> 
> https://console.groq.com/keys  --> groq api key
> 
> https://app.tavily.com/home --> tavily api key

---

## 💡 Cost & Resource Strategy (Free-Tier Optimized)

This project is intentionally engineered to operate at **zero infrastructure cost**, leveraging **free-tier models** and resources exclusively during the Alpha phase. To achieve reliability, throughput, and fault tolerance under free-tier constraints, the system employs a **multi-key load-balancing** strategy.

**Multiple API keys**—provisioned across separate Google accounts—are rotated and dynamically balanced to distribute request load, mitigate rate limits, and maintain uninterrupted service availability. This approach enables real-world stress testing of agentic orchestration, routing logic, and failover behavior without incurring any paid usage, while closely simulating production-scale traffic patterns.

This design choice reinforces the project’s goals of:

* Cost-efficiency by design

* Resilience under constrained resources

* Realistic LLMOps experimentation without financial overhead

## 👨‍💻 Engineering Standards

Engineered with a focus on **High Availability (HA)** and **Large Language Model Operations (LLMOps)**.

* **Pattern:** Agentic Workflow (Router–Solver).
* **Reliability:** Exponential Backoff & Multi-Key Rotation.
* **Observability:** Verbose console logging for "Brain State" tracking.
