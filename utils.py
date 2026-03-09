"""
ResumeGuide Utils - Google ADK Edition
Agent wrapper for Google Agent Development Kit (ADK) with Vertex AI
"""

import os
import glob
import json
import asyncio
from typing import List, Callable, Optional

from google.adk.agents import Agent as ADKAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.models import Gemini
from google.genai import types

# --- AUTO-DETECT PROJECT ID FROM SERVICE ACCOUNT JSON ---
def _get_project_id():
    """Get project ID from service account JSON in current directory."""
    json_files = glob.glob("*.json")
    for f in json_files:
        try:
            with open(f) as fp:
                data = json.load(fp)
                if data.get("type") == "service_account":
                    return data.get("project_id"), f
        except:
            continue
    return None, None


def _setup_vertex_auth():
    """Setup Vertex AI authentication using service account."""
    project_id, sa_file = _get_project_id()
    
    if not project_id:
        raise ValueError("⚠️ No service account JSON found! Place your GCP JSON in this folder.")
    
    # Set the credentials path for ADC
    if sa_file:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = sa_file
    
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    
    # Set environment variables for ADK to use Vertex AI
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"  # Tell genai to use Vertex AI
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    os.environ["GOOGLE_CLOUD_LOCATION"] = location
    
    print(f"🔌 Connecting to Vertex AI (Project: {project_id}, Loc: {location})...")
    print(f"🔑 Using credentials: {sa_file}")
    
    return project_id, location


class Agent:
    """
    A robust Agent wrapper for Google ADK (Agent Development Kit).
    Uses Vertex AI with Application Default Credentials (ADC) for authentication.
    
    Setup: Place your service account JSON in this folder!
    """
    
    # Shared session service for all agents
    _session_service = None
    _app_name = "resume_guide"
    
    def __init__(
        self, 
        name: str, 
        model: str = "gemini-2.0-flash",
        instruction: str = "",
        tools: List[Callable] = None
    ):
        self.name = name
        self.model_name = model
        self.system_instruction = instruction
        self.tools = tools or []
        self._session_created = False
        
        # Setup Vertex AI auth
        project_id, location = _setup_vertex_auth()
        
        # Initialize shared session service (singleton pattern)
        if Agent._session_service is None:
            Agent._session_service = InMemorySessionService()
        
        # Create unique session ID for this agent instance
        self._user_id = f"user_{name}"
        self._session_id = f"session_{name}_{id(self)}"
        
        # Create the Gemini model instance for ADK
        # This properly configures the model for use with Vertex AI
        gemini_model = Gemini(model=model)
        
        # Create the ADK Agent with the Gemini model instance
        # Note: ADK requires tools to be a list (not None)
        self._agent = ADKAgent(
            name=name,
            model=gemini_model,
            instruction=instruction,
            tools=self.tools if self.tools else [],
        )
        
        # Create Runner for this agent
        self._runner = Runner(
            agent=self._agent,
            app_name=Agent._app_name,
            session_service=Agent._session_service,
        )
    
    async def _ensure_session_async(self):
        """Ensure a session exists for this agent (async version)."""
        if self._session_created:
            return
            
        try:
            session = await Agent._session_service.get_session(
                app_name=Agent._app_name,
                user_id=self._user_id,
                session_id=self._session_id
            )
            if session is None:
                await Agent._session_service.create_session(
                    app_name=Agent._app_name,
                    user_id=self._user_id,
                    session_id=self._session_id
                )
        except Exception:
            # Session doesn't exist, create it
            await Agent._session_service.create_session(
                app_name=Agent._app_name,
                user_id=self._user_id,
                session_id=self._session_id
            )
        
        self._session_created = True

    def chat(self, message: str, image_path: str = None) -> str:
        """Sends a message to the agent and returns the response."""
        
        print(f"⏳ {self.name} is thinking...")
        
        # Handle image attachment (if provided)
        if image_path:
            try:
                with open(image_path, "rb") as f:
                    image_bytes = f.read()
                mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
                print(f"📸 [Attached Image: {image_path}]")
            except Exception as e:
                print(f"❌ Error loading image: {e}")
        
        # Run the agent using asyncio
        try:
            # Try to get existing event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running (e.g., in Jupyter), use nest_asyncio
                try:
                    import nest_asyncio
                    nest_asyncio.apply()
                except ImportError:
                    pass
                response_text = loop.run_until_complete(self._run_agent(message))
            else:
                response_text = loop.run_until_complete(self._run_agent(message))
            return response_text
        except RuntimeError:
            # If no event loop exists, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response_text = loop.run_until_complete(self._run_agent(message))
                return response_text
            finally:
                pass  # Keep loop for reuse
    
    async def _run_agent(self, message: str) -> str:
        """Run the agent asynchronously and collect response."""
        
        # Ensure session exists
        await self._ensure_session_async()
        
        final_response = ""
        
        # Use the runner to process the message
        async for event in self._runner.run_async(
            user_id=self._user_id,
            session_id=self._session_id,
            new_message=types.Content(
                role="user",
                parts=[types.Part(text=message)]
            )
        ):
            # Process events from the agent
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        # Check for function calls (tool usage)
                        if hasattr(part, 'function_call') and part.function_call:
                            fc = part.function_call
                            print(f"🛠️ [Tool Call]: {fc.name}({fc.args})")
                        # Check for text response
                        elif hasattr(part, 'text') and part.text:
                            final_response = part.text
            
            # Handle different event types
            if hasattr(event, 'actions'):
                for action in event.actions or []:
                    if hasattr(action, 'function_calls'):
                        for fc in action.function_calls or []:
                            print(f"🛠️ [Tool Call]: {fc.name}")
        
        return final_response if final_response else "No response generated."

    def clear_memory(self):
        """Clear the conversation history for this agent."""
        # Create a new session to clear history
        self._session_id = f"session_{self.name}_{id(self)}_{hash(str(id(self)))}"
        self._session_created = False
        print(f"🧹 Memory cleared for {self.name}.")


def print_box(title: str, content: str):
    """Pretty prints output in a box format."""
    print(f"\n{'='*10} {title} {'='*10}")
    print(content)
    print("="*30 + "\n")
