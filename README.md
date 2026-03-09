# ResumeGuide: Multi-Agent Resume System 

A 3-agent system to help B.Tech students craft better resumes, built with **Google ADK (Agent Development Kit)** and **Vertex AI**.

## The 3 Agents

| Agent | Job | Tools |
|-------|-----|-------|
| **ProfileBot** | Collects student info | save_branch, save_skills, save_project |
| **ReviewerBot** | Analyzes resume quality | check_skill_demand, analyze_project |
| **CoachBot** | Gives career advice | get_industry_trends, suggest_certifications |

## Setup

### 1. Get GCP Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use existing)
3. Enable **Vertex AI API**
4. Create a Service Account with "Vertex AI User" role
5. Download the JSON key file
6. Rename it to `service_account.json` and place in this folder

### 2. Install Dependencies

```bash
pip install google-adk google-cloud-aiplatform python-dotenv requests pandas streamlit
```

### 3. Run the Notebooks

Open in order:
1. `Part 1 - Agents & Tools.ipynb` - Build ProfileBot & ReviewerBot
2. `Part 2 - Memory & Guardrails.ipynb` - Build CoachBot + safety
3. `Part 3 - Evaluations.ipynb` - Test your agents
4. `Part 4 - The Complete Campus Assistant.ipynb` - Full demo

### 4. Run the Streamlit App

```bash
streamlit run app.py
```

## Quick Start

```python
from utils import Agent, print_box

# Create an agent using Google ADK
bot = Agent(
    name="MyBot",
    instruction="You help students with resumes.",
    tools=[my_function]  # Optional - plain Python functions work!
)

# Chat
response = bot.chat("Hi! I need help with my resume.")
print_box("Bot", response)
```

## Tech Stack

- **Google ADK** - Agent Development Kit for building AI agents
- **Gemini 2.0 Flash** - Fast and capable LLM
- **Vertex AI** - Enterprise-grade AI infrastructure
- **Streamlit** - Interactive web UI

## Workshop by GDG Amity Bengaluru 🎓
