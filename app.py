"""
ResumeGuide: Multi-Agent Resume System
Streamlit App for Hands-On session
Built with Google ADK (Agent Development Kit) + Vertex AI
"""

import streamlit as st
from utils import Agent, print_box

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ResumeGuide | Multi-Agent System",
    page_icon="🤖",
    layout="wide"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #4285F4, #EA4335, #FBBC04, #34A853);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<h1 class="main-header">🤖 ResumeGuide</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">A 3-Agent System for B.Tech Resume Guidance | Built with Google ADK + Vertex AI</p>', unsafe_allow_html=True)

# --- SHARED STATE ---
if "student_data" not in st.session_state:
    st.session_state.student_data = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {"profile": [], "reviewer": [], "coach": []}

# --- TOOL DEFINITIONS ---
def save_branch(branch: str) -> str:
    """Save the student's engineering branch."""
    st.session_state.student_data['branch'] = branch
    return f"✅ Branch saved: {branch}"

def save_skills(skills: str) -> str:
    """Save technical skills as comma-separated string."""
    st.session_state.student_data['skills'] = [s.strip() for s in skills.split(',')]
    return f"✅ Skills saved: {st.session_state.student_data['skills']}"

def save_project(title: str, description: str) -> str:
    """Save a project with title and description."""
    if 'projects' not in st.session_state.student_data:
        st.session_state.student_data['projects'] = []
    st.session_state.student_data['projects'].append({'title': title, 'desc': description})
    return f"✅ Project added: {title}"

def get_profile() -> str:
    """Get current student profile."""
    return str(st.session_state.student_data) if st.session_state.student_data else "No data yet."

def check_skill_demand(skill: str) -> str:
    """Check if a skill is in demand."""
    HOT_SKILLS = ["python", "react", "machine learning", "aws", "docker", "kubernetes", "typescript", "golang"]
    if skill.lower() in HOT_SKILLS:
        return f"🔥 '{skill}' is HIGH DEMAND in 2024-25!"
    return f"'{skill}' is useful but consider adding trending skills like Python, React, or AWS."

def analyze_project(title: str, description: str) -> str:
    """Analyze project description quality."""
    issues = []
    if len(description) < 20:
        issues.append("Too short - add more details")
    if not any(word in description.lower() for word in ["built", "developed", "created", "implemented", "designed"]):
        issues.append("Use action verbs (built, developed, created)")
    if not any(char.isdigit() for char in description):
        issues.append("Add metrics/numbers (e.g., '50% faster', '1000 users')")
    
    if issues:
        return f"⚠️ Improvements needed: {', '.join(issues)}"
    return "✅ Project description looks strong!"

def get_industry_trends(branch: str) -> str:
    """Get industry trends for engineering branch."""
    TRENDS = {
        "cse": "🚀 AI/ML, Cloud Computing, Cybersecurity are hot. Remote work is common. Focus on DSA + System Design.",
        "ece": "📡 IoT, Embedded Systems, 5G. Hardware + Software hybrid roles are growing. Learn Python for automation.",
        "mechanical": "⚡ EV industry is booming. CAD/CAM + Python automation highly valued. Consider robotics.",
        "civil": "🏗️ Sustainable construction, BIM software. Green building certifications help stand out.",
        "electrical": "🔋 Renewable energy, Power Electronics, Smart Grid. Python + MATLAB are useful."
    }
    return TRENDS.get(branch.lower(), "Focus on interdisciplinary skills + coding basics. Python is universal.")

def suggest_certifications(skills: str) -> str:
    """Suggest certifications based on skills."""
    certs = []
    skills_lower = skills.lower()
    if "python" in skills_lower: certs.append("Google Professional ML Engineer")
    if "cloud" in skills_lower or "aws" in skills_lower: certs.append("AWS Solutions Architect")
    if "react" in skills_lower or "frontend" in skills_lower: certs.append("Meta Front-End Developer")
    if "data" in skills_lower: certs.append("Google Data Analytics Certificate")
    if not certs: certs.append("Google IT Support Certificate (good starting point)")
    return f"📜 Recommended: {', '.join(certs)}"

# --- INITIALIZE AGENTS (cached) ---
@st.cache_resource
def get_agents():
    """Initialize all 3 agents using Google ADK."""
    profile_bot = Agent(
        name="ProfileBot",
        instruction="""You are ProfileBot, a friendly assistant that collects student info for resumes.
        Ask about: Branch, Skills, Projects. Use tools to SAVE each piece.
        Be conversational. One question at a time. Keep responses short.""",
        tools=[save_branch, save_skills, save_project, get_profile]
    )
    
    reviewer_bot = Agent(
        name="ReviewerBot", 
        instruction="""You are ReviewerBot, a resume expert. Your job:
        1. Check skill demand using check_skill_demand tool
        2. Analyze projects using analyze_project tool
        Give specific, actionable feedback. Be encouraging but honest.""",
        tools=[check_skill_demand, analyze_project]
    )
    
    coach_bot = Agent(
        name="CoachBot",
        instruction="""You are CoachBot, a career advisor for B.Tech students.
        Use get_industry_trends for branch-specific advice.
        Use suggest_certifications for cert recommendations.
        Be motivating and give specific actionable advice.""",
        tools=[get_industry_trends, suggest_certifications]
    )
    
    return profile_bot, reviewer_bot, coach_bot

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🧑‍💼 ProfileBot", "📝 ReviewerBot", "🎯 CoachBot", "📊 Dashboard"])

# --- TAB 1: PROFILEBOT ---
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🧑‍💼 ProfileBot - Collect Your Info")
        st.caption("Tell me about yourself and I'll save it for your resume!")
        
        # Chat interface
        for msg in st.session_state.chat_history["profile"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
        
        if prompt := st.chat_input("Tell ProfileBot about yourself...", key="profile_input"):
            # Add user message
            st.session_state.chat_history["profile"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("ProfileBot is thinking..."):
                    try:
                        profile_bot, _, _ = get_agents()
                        response = profile_bot.chat(prompt)
                        st.write(response)
                        st.session_state.chat_history["profile"].append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Error: {e}")
    
    with col2:
        st.subheader("📋 Your Profile")
        if st.session_state.student_data:
            st.json(st.session_state.student_data)
        else:
            st.info("No data yet. Start chatting!")
        
        if st.button("🗑️ Clear Profile", key="clear_profile"):
            st.session_state.student_data = {}
            st.session_state.chat_history["profile"] = []
            st.rerun()

# --- TAB 2: REVIEWERBOT ---
with tab2:
    st.subheader("📝 ReviewerBot - Analyze Your Resume")
    st.caption("Get feedback on your skills and project descriptions!")
    
    # Chat interface
    for msg in st.session_state.chat_history["reviewer"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Ask ReviewerBot to analyze skills or projects...", key="reviewer_input"):
        st.session_state.chat_history["reviewer"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("ReviewerBot is analyzing..."):
                try:
                    _, reviewer_bot, _ = get_agents()
                    response = reviewer_bot.chat(prompt)
                    st.write(response)
                    st.session_state.chat_history["reviewer"].append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Quick actions
    st.divider()
    st.subheader("⚡ Quick Skill Check")
    col1, col2, col3 = st.columns(3)
    skills_to_check = ["Python", "React", "Java", "Machine Learning", "Docker", "SQL"]
    
    for i, skill in enumerate(skills_to_check):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(f"Check: {skill}", key=f"skill_{skill}"):
                result = check_skill_demand(skill)
                st.info(result)

# --- TAB 3: COACHBOT ---
with tab3:
    st.subheader("🎯 CoachBot - Career Guidance")
    st.caption("Get industry-specific advice for your engineering branch!")
    
    # Chat interface
    for msg in st.session_state.chat_history["coach"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    if prompt := st.chat_input("Ask CoachBot for career advice...", key="coach_input"):
        st.session_state.chat_history["coach"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("CoachBot is thinking..."):
                try:
                    _, _, coach_bot = get_agents()
                    response = coach_bot.chat(prompt)
                    st.write(response)
                    st.session_state.chat_history["coach"].append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Quick branch selector
    st.divider()
    st.subheader("🎓 Quick Industry Trends")
    branch = st.selectbox("Select your branch:", ["CSE", "ECE", "Mechanical", "Civil", "Electrical"])
    if st.button("Get Trends", key="get_trends"):
        result = get_industry_trends(branch)
        st.success(result)

# --- TAB 4: DASHBOARD ---
with tab4:
    st.subheader("📊 Resume Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Your Profile Summary")
        if st.session_state.student_data:
            if 'branch' in st.session_state.student_data:
                st.metric("Branch", st.session_state.student_data['branch'])
            if 'skills' in st.session_state.student_data:
                st.write("**Skills:**", ", ".join(st.session_state.student_data['skills']))
            if 'projects' in st.session_state.student_data:
                st.write(f"**Projects:** {len(st.session_state.student_data['projects'])}")
                for p in st.session_state.student_data['projects']:
                    st.write(f"  • {p['title']}")
        else:
            st.info("Start with ProfileBot to build your profile!")
    
    with col2:
        st.markdown("### 🤖 Agent Architecture")
        st.code("""
Student Input
     │
     ▼
┌─────────────┐
│  ProfileBot │ ← Collects Info (Google ADK)
└─────────────┘
     │
     ▼
┌─────────────┐
│ ReviewerBot │ ← Analyzes Quality (Google ADK)
└─────────────┘
     │
     ▼
┌─────────────┐
│  CoachBot   │ ← Gives Advice (Google ADK)
└─────────────┘
     │
     ▼
Resume Ready! 🎉
        """)
    
    st.divider()
    
    # Clear all button
    if st.button("🗑️ Reset Everything", type="secondary"):
        st.session_state.student_data = {}
        st.session_state.chat_history = {"profile": [], "reviewer": [], "coach": []}
        st.cache_resource.clear()
        st.rerun()

# --- FOOTER ---
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    Built with ❤️ for knowledge | Powered by Google ADK + Vertex AI
</div>
""", unsafe_allow_html=True)
