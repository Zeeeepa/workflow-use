"""
FastAPI routers for chat functionality
"""
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import json

from .chat_service import ChatService
from .chat_views import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatSessionCreateResponse,
    ChatSessionListResponse,
    ChatProvidersResponse,
    ChatSessionDeleteResponse,
    ChatSessionCancelResponse,
    ChatSessionExportResponse,
)

logger = logging.getLogger(__name__)

chat_router = APIRouter(prefix='/api/chat')

# Global chat service instance
chat_service = ChatService()


def get_chat_service() -> ChatService:
    return chat_service


@chat_router.post('/sessions', response_model=ChatSessionCreateResponse)
async def create_chat_session():
    """Create a new chat session"""
    try:
        service = get_chat_service()
        session_id = service.create_session()
        return ChatSessionCreateResponse(
            session_id=session_id,
            message=f"Chat session {session_id} created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")


@chat_router.get('/sessions', response_model=ChatSessionListResponse)
async def list_chat_sessions():
    """List all chat sessions"""
    try:
        service = get_chat_service()
        sessions = service.list_sessions()
        
        session_responses = []
        for session in sessions:
            message_responses = [
                ChatMessageResponse(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    metadata=msg.metadata
                )
                for msg in session.messages
            ]
            
            session_responses.append(ChatSessionResponse(
                id=session.id,
                messages=message_responses,
                created_at=session.created_at,
                updated_at=session.updated_at,
                status=session.status
            ))
        
        return ChatSessionListResponse(sessions=session_responses)
    except Exception as e:
        logger.error(f"Error listing chat sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list chat sessions: {str(e)}")


@chat_router.get('/sessions/{session_id}', response_model=ChatSessionResponse)
async def get_chat_session(session_id: str):
    """Get a specific chat session"""
    try:
        service = get_chat_service()
        session = service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        
        message_responses = [
            ChatMessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                timestamp=msg.timestamp,
                metadata=msg.metadata
            )
            for msg in session.messages
        ]
        
        return ChatSessionResponse(
            id=session.id,
            messages=message_responses,
            created_at=session.created_at,
            updated_at=session.updated_at,
            status=session.status
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get chat session: {str(e)}")


@chat_router.post('/sessions/{session_id}/messages', response_model=ChatMessageResponse)
async def send_chat_message(session_id: str, request: ChatMessageRequest, background_tasks: BackgroundTasks):
    """Send a message to a chat session and get browser automation response"""
    try:
        service = get_chat_service()
        session = service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        
        # Process the message with browser automation
        response_message = await service.process_user_message(
            session_id=session_id,
            message=request.message,
            provider=request.provider,
            model=request.model,
            browser_config=request.browser_config
        )
        
        return ChatMessageResponse(
            id=response_message.id,
            role=response_message.role,
            content=response_message.content,
            timestamp=response_message.timestamp,
            metadata=response_message.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing message for session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")


@chat_router.post('/sessions/{session_id}/cancel', response_model=ChatSessionCancelResponse)
async def cancel_chat_session(session_id: str):
    """Cancel an active chat session"""
    try:
        service = get_chat_service()
        success = await service.cancel_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        
        return ChatSessionCancelResponse(
            success=True,
            message=f"Chat session {session_id} cancelled successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel chat session: {str(e)}")


@chat_router.delete('/sessions/{session_id}', response_model=ChatSessionDeleteResponse)
async def delete_chat_session(session_id: str):
    """Delete a chat session"""
    try:
        service = get_chat_service()
        success = service.delete_session(session_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        
        return ChatSessionDeleteResponse(
            success=True,
            message=f"Chat session {session_id} deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete chat session: {str(e)}")


@chat_router.get('/providers', response_model=ChatProvidersResponse)
async def get_chat_providers():
    """Get available LLM providers and models"""
    try:
        service = get_chat_service()
        providers = service.get_available_providers()
        return ChatProvidersResponse(providers=providers)
    except Exception as e:
        logger.error(f"Error getting chat providers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {str(e)}")


@chat_router.get('/sessions/{session_id}/export', response_model=ChatSessionExportResponse)
async def export_chat_session(session_id: str):
    """Export a chat session to JSON"""
    try:
        service = get_chat_service()
        session_data = service.export_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        
        return ChatSessionExportResponse(
            session_data=session_data,
            success=True,
            message=f"Chat session {session_id} exported successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export chat session: {str(e)}")


@chat_router.get('/sessions/{session_id}/download')
async def download_chat_session(session_id: str):
    """Download a chat session as JSON file"""
    try:
        service = get_chat_service()
        session_data = service.export_session(session_id)
        
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Chat session {session_id} not found")
        
        def generate_json():
            yield json.dumps(session_data, indent=2, default=str)
        
        return StreamingResponse(
            generate_json(),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=chat_session_{session_id}.json"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading chat session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download chat session: {str(e)}")

