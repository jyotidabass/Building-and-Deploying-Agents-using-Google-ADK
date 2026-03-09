# 🤖 ResumeGuide — Multi-Agent Resume System

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![Google ADK](https://img.shields.io/badge/Google%20ADK-Agent%20Dev%20Kit-4285F4?style=flat-square&logo=google&logoColor=white)
![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Google%20Cloud-34A853?style=flat-square&logo=googlecloud&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini%202.0%20Flash-AI%20Model-EA4335?style=flat-square&logo=google&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)

> **Built with Google ADK (Agent Development Kit) + Vertex AI + Gemini 2.0 Flash**

---

## 📖 Read the Full Tutorial

[![Read on Medium](https://img.shields.io/badge/Medium-Read%20Full%20Tutorial-black?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@jyotidabass/building-ai-agents-with-google-adk-6275aaf5155d?sk=3fd9d2ec66fb7353f55b37b799646f3c)

This repo is accompanied by a **complete step-by-step Medium blog** that explains every line of code in simple terms — no prior AI experience needed.

The blog covers:
- 🤖 What AI agents are and why multi-agent systems beat single agents
- 🛠️ How `utils.py` works under the hood (auth, sessions, tool calling)
- 🧩 What tools are and why docstrings matter
- 🧠 How ADK manages memory automatically via sessions
- 🛡️ How guardrails are implemented in plain English
- 📊 How to evaluate agents using LLM-as-a-Judge
- 🖥️ How the Streamlit app is structured and deployed

> 💡 **Tip:** Read the blog first, then run the notebooks in order for the best learning experience.

---

A hands-on project that teaches you how to build and deploy AI agents. The end result is a smart **Resume Assistant** made of 3 AI agents that help B.Tech students write better resumes — each agent has its own job, its own tools, and its own personality.

---

## 🧠 What is This Project?

Instead of one big AI doing everything, this project uses **3 smaller AI agents**, each focused on one task:

| Agent | What it does | Tools it uses |
|---|---|---|
| 🧑‍💼 **ProfileBot** | Asks you questions and saves your info | `save_branch`, `save_skills`, `save_project`, `get_profile` |
| 📝 **ReviewerBot** | Reviews your skills and project descriptions | `check_skill_demand`, `analyze_project` |
| 🎯 **CoachBot** | Gives career advice based on your branch | `get_industry_trends`, `suggest_certifications` |

**Why 3 agents instead of 1?**
- Each agent is small and focused → easier to fix if something breaks
- You can improve one agent without touching the others
- Shorter instructions = better AI responses

---

## 📁 What's Inside This Repo

```
📦 ResumeGuide/
│
├── 📓 Part 1 - Agents & Tools.ipynb        ← Build ProfileBot & ReviewerBot
├── 📓 Part 2 - Memory & Guardrails.ipynb   ← Build CoachBot + safety rules
├── 📓 Part 3 - Evaluations.ipynb           ← Test if your agents work correctly
├── 📓 Part 4 - The Complete Campus Assistant.ipynb  ← Full demo, all agents together
│
├── 🐍 app.py          ← Streamlit web app (chat UI for all 3 agents)
├── 🐍 utils.py        ← The Agent class (the engine that powers everything)
└── 📄 requirements.txt ← Python packages to install
```

---

## ⚙️ How It All Works (Simple Explanation)

### The Flow

```
You type a message
       ↓
   Agent receives it
       ↓
   Gemini 2.0 Flash (the AI brain) decides what to do
       ↓
   If needed → calls a Tool (a Python function)
       ↓
   Tool returns a result
       ↓
   Agent sends you a reply
```

### What is a "Tool"?

A tool is just a **regular Python function** that the AI can call on its own. You don't call it manually. You give it to the agent, and the agent figures out when to use it.

```python
# This is a tool — just a normal Python function
def save_branch(branch: str) -> str:
    """Save the student's engineering branch."""
    STUDENT_PROFILE['branch'] = branch
    return f"✅ Branch saved: {branch}"

# Give it to an agent — the agent will call it automatically when needed
profile_bot = Agent(
    name="ProfileBot",
    instruction="Collect student info for their resume. Use tools to save data.",
    tools=[save_branch]  # ← hand over the tool here
)
```

### What is a "Session"?

A session is the **memory** of a conversation. ADK stores the entire chat history in memory so the agent remembers what you said earlier in the same conversation. Each agent has its own session.

---

## 🚀 Setup Guide (Step by Step)

### Step 1 — Get a Google Cloud Account

Go to [console.cloud.google.com](https://console.cloud.google.com) and either create a new project or use an existing one.

### Step 2 — Enable Vertex AI

In Google Cloud Console:
1. Search for **"Vertex AI"** in the top search bar
2. Click **Enable API**

### Step 3 — Create a Service Account (your "key" to use the API)

1. In the Console, go to **IAM & Admin → Service Accounts**
2. Click **Create Service Account**
3. Give it any name (e.g., `resumeguide-bot`)
4. Assign the role: **Vertex AI User**
5. Click **Done**
6. Open the service account → go to **Keys** tab → **Add Key → JSON**
7. A `.json` file will download — this is your credential file

> ⚠️ Keep this file private. Never upload it to GitHub.

### Step 4 — Place the JSON File in the Project Folder

Rename the downloaded file to something recognizable (e.g., `my-project-credentials.json`) and place it in the **same folder** as `utils.py`.

The code auto-detects any `.json` file in the folder that contains `"type": "service_account"` — so you don't need to configure anything else.

### Step 5 — Install Dependencies

```bash
pip install google-adk google-cloud-aiplatform python-dotenv requests pandas streamlit nest_asyncio
```

Or using the requirements file:

```bash
pip install -r requirements.txt
```

### Step 6 — Run the Notebooks (in order)

Open Jupyter and run the notebooks one by one:

```
Part 1 → Part 2 → Part 3 → Part 4
```

Or run the full web app:

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

---

## 🧩 Understanding `utils.py` — The Core Engine

This file contains the `Agent` class that wraps Google ADK into something simple to use. Here's what it does:

### Authentication (auto)
```python
def _setup_vertex_auth():
    # Finds your .json file in the folder
    # Sets the right environment variables for Vertex AI
    # You don't need to call this — Agent() does it automatically
```

### Creating an Agent
```python
bot = Agent(
    name="ProfileBot",          # A unique name
    model="gemini-2.0-flash",   # Which Gemini model to use (default)
    instruction="Your role...", # The system prompt / personality
    tools=[my_function]         # Optional list of Python functions
)
```

### Chatting with an Agent
```python
response = bot.chat("Hello! I want to build my resume.")
print(response)
```

### Clearing Memory
```python
bot.clear_memory()  # Starts a fresh conversation (new session)
```

### Pretty Printing
```python
from utils import print_box
print_box("ProfileBot", response)  # Prints response in a nice box
```

---

## 📓 Notebook Breakdown

### Part 1 — Agents & Tools
- Learn what an agent is and why multi-agent systems are better
- Build **ProfileBot**: collects branch, skills, projects
- Build **ReviewerBot**: checks skill demand, reviews project descriptions
- See how tools (Python functions) are called automatically by the AI

### Part 2 — Memory & Guardrails
- Build **CoachBot**: gives career advice based on engineering branch
- Understand how ADK keeps conversation memory automatically
- Add **Guardrails** — rules that prevent the AI from helping students lie on resumes (e.g., refusing to fabricate fake internships)
- Guardrails are implemented as instructions in the system prompt

### Part 3 — Evaluations
- Learn why you need to test your agents
- Use **LLM-as-a-Judge**: another AI model reads your agent's responses and scores them
- Test cases check:
  - Does ReviewerBot correctly identify in-demand skills?
  - Does CoachBot give branch-specific advice?
  - Does the safe bot refuse to fabricate experience?

### Part 4 — The Complete Campus Assistant
- All 3 agents working together
- Full end-to-end demo: from collecting info → reviewing → coaching

---

## 🖥️ The Streamlit Web App (`app.py`)

This is a browser-based chat interface with 4 tabs:

| Tab | What it does |
|---|---|
| 🧑‍💼 ProfileBot | Chat to enter your details; profile is shown live on the right |
| 📝 ReviewerBot | Chat to get resume feedback; quick skill-check buttons included |
| 🎯 CoachBot | Chat for career advice; select your branch for instant industry trends |
| 📊 Dashboard | See your full profile summary + agent architecture diagram |

The app uses `st.cache_resource` so agents are only created once (not re-created on every message).

---

## 🛠️ Tools Reference

### ProfileBot Tools

| Tool | Input | What it does |
|---|---|---|
| `save_branch(branch)` | e.g., `"CSE"` | Saves your engineering branch |
| `save_skills(skills)` | e.g., `"Python, React, SQL"` | Saves comma-separated skills |
| `save_project(title, description)` | title + description | Saves a project to your profile |
| `get_profile()` | none | Returns all saved data so far |

### ReviewerBot Tools

| Tool | Input | What it does |
|---|---|---|
| `check_skill_demand(skill)` | e.g., `"Python"` | Tells if the skill is hot in 2024-25 |
| `analyze_project(title, description)` | title + description | Checks for issues: too short, no action verbs, no metrics |

### CoachBot Tools

| Tool | Input | What it does |
|---|---|---|
| `get_industry_trends(branch)` | e.g., `"CSE"` | Returns job market trends for that branch |
| `suggest_certifications(skills)` | e.g., `"Python, AWS"` | Recommends relevant certifications |

---

## 🧱 Tech Stack

| Technology | Role |
|---|---|
| **Google ADK** | Framework for building AI agents with tool calling and session management |
| **Gemini 2.0 Flash** | The AI brain — fast, capable language model |
| **Vertex AI** | Google's cloud platform to run AI models securely |
| **Streamlit** | Turns Python code into a web app with chat interface |
| **nest_asyncio** | Lets async code run inside Jupyter notebooks |

---

## ❓ Common Issues & Fixes

**"No service account JSON found"**
→ Make sure your `.json` credentials file is in the same folder as `utils.py`. The file must contain `"type": "service_account"`.

**"Vertex AI API not enabled"**
→ Go to [Google Cloud Console](https://console.cloud.google.com), search "Vertex AI", and click Enable.

**"Permission denied" or "403 error"**
→ Your service account doesn't have the right role. Go to IAM, find your service account, and add the **Vertex AI User** role.

**"nest_asyncio error" in Jupyter**
→ Run `pip install nest_asyncio` and restart the kernel.

**Agent responds but doesn't call tools**
→ Make sure your tool functions have **docstrings** (the `"""description"""` part). ADK uses docstrings to understand what each tool does.

---

## 💡 Key Concepts Summary

| Concept | Simple Explanation |
|---|---|
| **Agent** | An AI with a specific role, instructions, and tools |
| **Tool** | A Python function the agent can call on its own |
| **Session** | The memory of a conversation (auto-managed by ADK) |
| **Guardrail** | A rule written in the system prompt to prevent bad behavior |
| **LLM-as-a-Judge** | Using one AI to evaluate another AI's response |
| **Vertex AI** | Google Cloud's secure platform to run Gemini models |

---

## 📌 Quick Start (3 Lines)

```python
from utils import Agent, print_box

bot = Agent(name="MyBot", instruction="You help students with resumes.")
print_box("Bot", bot.chat("Hi! I need help improving my resume."))
```

That's it. The Agent class handles authentication, sessions, and tool calling automatically.

---

*Built for hands-on learning. Powered by Google ADK + Vertex AI.*
