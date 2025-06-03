# Browser Chat Interface

This feature adds an AI-powered chat interface to workflow-use that allows you to control browser automation through natural language conversations.

## Features

🤖 **AI-Powered Browser Control**: Chat with AI to automate any browser task
🌐 **Multiple LLM Providers**: Support for OpenAI, Anthropic, and Google models
💬 **Session Management**: Create, manage, and export chat sessions
⚙️ **Configurable Browser**: Choose between headless and visible browser modes
📱 **Real-time Interface**: Live chat with immediate browser action feedback
📊 **Export Capabilities**: Download chat sessions as JSON files

## Setup

### 1. Install Dependencies

The required dependencies are already included in `pyproject.toml`:
- `browser-use>=0.2.4` - Browser automation library
- `langchain-openai>=0.2.0` - OpenAI integration
- `langchain-anthropic>=0.2.0` - Anthropic integration  
- `langchain-google-genai>=2.0.0` - Google integration

### 2. Configure API Keys

Copy the environment file and add your API keys:

```bash
cp workflows/.env.example workflows/.env
```

Edit `workflows/.env` and add at least one API key:

```env
# Required: At least one LLM provider API key
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Browser configuration
BROWSER_HEADLESS=false
BROWSER_DISABLE_SECURITY=true
```

### 3. Start the Services

Start the backend API server:

```bash
cd workflows
python -m backend.api
```

Start the UI development server:

```bash
cd ui
npm run dev
```

## Usage

### Opening the Chat Interface

1. Open the workflow-use UI in your browser (typically `http://localhost:5173`)
2. Click the **chat icon** (💬) in the top-right corner of the interface
3. The chat interface will open as a modal overlay

### Creating a Chat Session

1. Click **"New Chat Session"** to create a new conversation
2. The session will appear in the sidebar with a unique ID
3. You can have multiple sessions and switch between them

### Chatting with the AI

1. Type your browser automation request in the message box
2. Examples of what you can ask:
   - "Go to Google and search for 'workflow automation'"
   - "Navigate to GitHub and find the trending repositories"
   - "Open Amazon and add the first laptop to cart"
   - "Fill out a contact form on example.com"
   - "Take a screenshot of the current page"

3. Press **Enter** or click **Send** to submit your message
4. The AI will process your request and control the browser accordingly
5. You'll see the results and any extracted information in the chat

### Configuration Options

Click the **settings icon** (⚙️) to configure:

- **LLM Provider**: Choose between OpenAI, Anthropic, or Google
- **Model**: Select specific models (GPT-4, Claude, Gemini, etc.)
- **Show Browser**: Toggle between headless and visible browser mode

### Session Management

- **Switch Sessions**: Click on any session in the sidebar to switch to it
- **Cancel Session**: Click the stop button (⏹️) to cancel an active automation
- **Download Session**: Click the download button (📥) to export as JSON
- **Delete Session**: Click the trash button (🗑️) to permanently delete

## API Endpoints

The chat interface adds the following API endpoints:

### Sessions
- `POST /api/chat/sessions` - Create new chat session
- `GET /api/chat/sessions` - List all sessions
- `GET /api/chat/sessions/{id}` - Get specific session
- `DELETE /api/chat/sessions/{id}` - Delete session
- `POST /api/chat/sessions/{id}/cancel` - Cancel active session

### Messages
- `POST /api/chat/sessions/{id}/messages` - Send message and get AI response

### Configuration
- `GET /api/chat/providers` - Get available LLM providers and models

### Export
- `GET /api/chat/sessions/{id}/export` - Export session as JSON
- `GET /api/chat/sessions/{id}/download` - Download session file

## Example Requests

### Send a Chat Message

```bash
curl -X POST "http://localhost:8000/api/chat/sessions/{session_id}/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Go to Google and search for workflow automation",
    "provider": "openai",
    "model": "gpt-4o",
    "browser_config": {
      "headless": false,
      "disable_security": true
    }
  }'
```

### Create New Session

```bash
curl -X POST "http://localhost:8000/api/chat/sessions"
```

### List Available Providers

```bash
curl "http://localhost:8000/api/chat/providers"
```

## Troubleshooting

### Common Issues

1. **"API key not found" error**
   - Make sure you've set the appropriate environment variable
   - Check that your `.env` file is in the `workflows/` directory
   - Restart the backend server after adding API keys

2. **Browser automation fails**
   - Ensure you have the required browser dependencies installed
   - Try running with `headless: false` to see what's happening
   - Check the browser console for JavaScript errors

3. **Chat interface doesn't load**
   - Make sure both backend and frontend servers are running
   - Check that the API endpoints are accessible at `http://localhost:8000`
   - Verify CORS settings in the backend configuration

4. **Session not found errors**
   - Sessions are stored in memory and will be lost when the server restarts
   - Make sure you're using the correct session ID
   - Create a new session if the old one is no longer available

### Browser Dependencies

If you encounter browser-related issues, you may need to install additional dependencies:

```bash
# Install Playwright browsers
playwright install

# Or install specific browser
playwright install chromium
```

## Security Considerations

- API keys are stored as environment variables and should never be committed to version control
- The browser runs with security features disabled by default for automation purposes
- Sessions are stored in memory and are not persisted between server restarts
- Consider implementing authentication for production deployments

## Contributing

To extend the chat interface:

1. **Add new LLM providers**: Extend the `ChatService` class in `chat_service.py`
2. **Add new browser capabilities**: Modify the browser configuration options
3. **Enhance the UI**: Update the React components in `ui/src/components/`
4. **Add persistence**: Implement database storage for sessions and messages

## License

This chat interface is part of the workflow-use project and follows the same license terms.

