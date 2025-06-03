"""
Chat service for browser automation using browser-use
"""
import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from browser_use import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ChatSession:
    id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    status: str = "active"  # active, completed, error


class ChatService:
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.active_agents: Dict[str, Agent] = {}
        self.llm_providers = {
            "openai": self._create_openai_llm,
            "anthropic": self._create_anthropic_llm,
            "google": self._create_google_llm,
        }
        
    def _create_openai_llm(self, model: str = "gpt-4o"):
        """Create OpenAI LLM instance"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        return ChatOpenAI(model=model, api_key=api_key)
    
    def _create_anthropic_llm(self, model: str = "claude-3-5-sonnet-20241022"):
        """Create Anthropic LLM instance"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        return ChatAnthropic(model=model, api_key=api_key)
    
    def _create_google_llm(self, model: str = "gemini-1.5-pro"):
        """Create Google LLM instance"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key)
    
    def create_session(self) -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        now = datetime.now()
        
        session = ChatSession(
            id=session_id,
            messages=[],
            created_at=now,
            updated_at=now
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created new chat session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[ChatSession]:
        """List all chat sessions"""
        return list(self.sessions.values())
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Add a message to a chat session"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        message = ChatMessage(
            id=str(uuid.uuid4()),
            role=role,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        session.updated_at = datetime.now()
        
        logger.info(f"Added {role} message to session {session_id}")
        return message
    
    async def process_user_message(
        self, 
        session_id: str, 
        message: str, 
        provider: str = "openai", 
        model: str = None,
        browser_config: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Process a user message and generate browser actions"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Add user message
        user_message = self.add_message(session_id, "user", message)
        
        try:
            # Create LLM instance
            if provider not in self.llm_providers:
                raise ValueError(f"Unsupported LLM provider: {provider}")
            
            llm_creator = self.llm_providers[provider]
            if model:
                llm = llm_creator(model)
            else:
                llm = llm_creator()
            
            # Configure browser settings
            browser_settings = {
                "headless": browser_config.get("headless", False) if browser_config else False,
                "disable_security": browser_config.get("disable_security", True) if browser_config else True,
            }
            
            # Create browser agent
            agent = Agent(
                task=message,
                llm=llm,
                **browser_settings
            )
            
            # Store agent for potential cancellation
            self.active_agents[session_id] = agent
            
            # Execute the task
            logger.info(f"Starting browser automation for session {session_id}")
            result = await agent.run()
            
            # Clean up agent
            self.active_agents.pop(session_id, None)
            
            # Format response
            response_content = self._format_agent_response(result)
            
            # Add assistant response
            assistant_message = self.add_message(
                session_id, 
                "assistant", 
                response_content,
                metadata={
                    "provider": provider,
                    "model": model or "default",
                    "browser_config": browser_settings,
                    "execution_result": result
                }
            )
            
            session.status = "completed"
            logger.info(f"Completed browser automation for session {session_id}")
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error processing message for session {session_id}: {str(e)}")
            
            # Clean up agent
            self.active_agents.pop(session_id, None)
            
            # Add error response
            error_message = self.add_message(
                session_id,
                "assistant",
                f"I encountered an error while processing your request: {str(e)}",
                metadata={"error": str(e), "provider": provider}
            )
            
            session.status = "error"
            return error_message
    
    def _format_agent_response(self, result) -> str:
        """Format the agent execution result into a readable response"""
        if isinstance(result, str):
            return result
        
        if hasattr(result, 'extracted_content') and result.extracted_content:
            return f"Task completed successfully! Here's what I found:\n\n{result.extracted_content}"
        
        if hasattr(result, 'message') and result.message:
            return result.message
        
        # Fallback for complex result objects
        return f"Task completed successfully! Result: {str(result)}"
    
    async def cancel_session(self, session_id: str) -> bool:
        """Cancel an active browser session"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Cancel active agent if exists
        agent = self.active_agents.get(session_id)
        if agent:
            try:
                # Browser-use agents don't have a direct cancel method,
                # but we can remove the reference and let it timeout
                self.active_agents.pop(session_id, None)
                logger.info(f"Cancelled active agent for session {session_id}")
            except Exception as e:
                logger.error(f"Error cancelling agent for session {session_id}: {str(e)}")
        
        session.status = "cancelled"
        session.updated_at = datetime.now()
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session"""
        if session_id not in self.sessions:
            return False
        
        # Cancel first if active
        asyncio.create_task(self.cancel_session(session_id))
        
        # Remove session
        del self.sessions[session_id]
        logger.info(f"Deleted session {session_id}")
        
        return True
    
    def get_available_providers(self) -> Dict[str, List[str]]:
        """Get available LLM providers and their models"""
        return {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
            "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
            "google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
        }
    
    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export a session to JSON format"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session": asdict(session),
            "messages": [asdict(msg) for msg in session.messages]
        }

