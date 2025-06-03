# Browser-Use Web-UI Integration

This integration provides seamless access to the official [browser-use web-ui](https://github.com/browser-use/web-ui) alongside workflow-use functionality. Instead of creating redundant interfaces, we leverage the mature, feature-complete browser-use web-ui.

## Why Use the Official Web-UI?

The browser-use web-ui offers:
- 🎨 **Mature Gradio Interface**: Professional, tested UI with excellent UX
- 🌐 **Multi-LLM Support**: OpenAI, Anthropic, Google, Azure, DeepSeek, Ollama, and more
- 🔧 **Advanced Features**: Custom browser support, persistent sessions, HD recording
- 📱 **Mobile Friendly**: Responsive design that works on all devices
- 🔄 **Active Development**: Regular updates and community support
- 🐳 **Docker Support**: Easy containerized deployment with VNC access

## Quick Start

### Option 1: PowerShell (Windows)

```powershell
# Basic launch - sets up and starts web-ui
.\launch-browser-use-webui.ps1

# With workflow backend integration
.\launch-browser-use-webui.ps1 -LaunchWorkflowBackend

# Docker deployment with persistent browser
.\launch-browser-use-webui.ps1 -UseDocker -PersistentBrowser

# Custom configuration
.\launch-browser-use-webui.ps1 -WebUIPort 8080 -WorkflowPort 9000
```

### Option 2: Python (Cross-platform)

```bash
# Basic launch
python launch-integrated-suite.py

# With workflow backend and auto-open browser
python launch-integrated-suite.py --launch-workflow --open-browser

# Custom ports
python launch-integrated-suite.py --webui-port 8080 --workflow-port 9000
```

### Option 3: Bash (Unix/Linux/macOS)

```bash
# Basic launch
./launch-browser-use-webui.sh

# With workflow backend
./launch-browser-use-webui.sh --launch-workflow

# Docker deployment
./launch-browser-use-webui.sh --use-docker --persistent-browser
```

## Features

### 🚀 One-Click Setup
- Automatically clones the official browser-use web-ui
- Sets up Python virtual environment
- Installs all dependencies including Playwright browsers
- Configures environment files

### 🔧 Workflow Integration
- Optional workflow-use backend launch
- Seamless integration between services
- Shared configuration management
- Process lifecycle management

### 🐳 Docker Support
- Full Docker Compose setup
- VNC access for browser viewing
- Persistent browser sessions
- Easy scaling and deployment

### ⚙️ Configuration Options
- Multiple deployment modes (local/Docker)
- Configurable ports and IP addresses
- Browser persistence settings
- Environment file management

## Configuration

### Environment Setup

The launchers automatically create a `.env` file from the example. You need to add at least one API key:

```env
# Required: At least one LLM provider API key
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional: Browser configuration
BROWSER_HEADLESS=false
BROWSER_DISABLE_SECURITY=true

# Optional: Custom browser (advanced)
BROWSER_PATH="/path/to/your/browser"
BROWSER_USER_DATA="/path/to/browser/profile"
```

### Advanced Configuration

For custom browser setup (using your own Chrome profile):

1. **Windows:**
   ```env
   BROWSER_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
   BROWSER_USER_DATA="C:\Users\YourUsername\AppData\Local\Google\Chrome\User Data"
   ```

2. **macOS:**
   ```env
   BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
   BROWSER_USER_DATA="/Users/YourUsername/Library/Application Support/Google/Chrome"
   ```

3. **Linux:**
   ```env
   BROWSER_PATH="/usr/bin/google-chrome"
   BROWSER_USER_DATA="/home/yourusername/.config/google-chrome"
   ```

## Usage Examples

### Basic Browser Automation

1. Launch the web-ui using any of the methods above
2. Open `http://127.0.0.1:7788` in your browser
3. Select your preferred LLM provider and model
4. Enter natural language commands like:
   - "Go to Google and search for 'AI automation'"
   - "Navigate to GitHub and find trending repositories"
   - "Open Amazon and add the first laptop to cart"
   - "Take a screenshot of the current page"

### With Workflow Integration

When launching with workflow backend (`--launch-workflow` or `-LaunchWorkflowBackend`):

1. **Web-UI**: `http://127.0.0.1:7788` - Browser automation interface
2. **Workflow API**: `http://127.0.0.1:8000` - Workflow management API
3. **Workflow UI**: `http://127.0.0.1:5173` - Workflow visual editor (if available)

### Docker Deployment

Docker mode provides additional features:

- **Web Interface**: `http://localhost:7788`
- **VNC Viewer**: `http://localhost:6080/vnc.html` (password: "youvncpassword")
- **Persistent Sessions**: Browser state maintained between tasks
- **Isolated Environment**: Clean, reproducible deployments

## API Integration

The browser-use web-ui exposes a Gradio API that can be integrated with workflow-use:

```python
from gradio_client import Client

# Connect to the web-ui API
client = Client("http://127.0.0.1:7788")

# Send automation command
result = client.predict(
    "Go to Google and search for 'workflow automation'",
    "openai",  # provider
    "gpt-4o",  # model
    api_name="/chat"
)
```

## Troubleshooting

### Common Issues

1. **"API key not found" error**
   - Ensure you've added at least one API key to the `.env` file
   - Restart the web-ui after adding keys

2. **Browser automation fails**
   - Install Playwright browsers: `playwright install --with-deps`
   - Try running with visible browser (set `BROWSER_HEADLESS=false`)

3. **Port conflicts**
   - Change ports using `--webui-port` or `--workflow-port` parameters
   - Check if ports are already in use: `netstat -an | grep :7788`

4. **Docker issues**
   - Ensure Docker Desktop is running
   - For ARM64 systems: `TARGETPLATFORM=linux/arm64 docker compose up --build`

5. **Permission errors (Unix/Linux)**
   - Make bash script executable: `chmod +x launch-browser-use-webui.sh`
   - Check Python virtual environment permissions

### Browser Dependencies

If you encounter browser-related issues:

```bash
# Install all browsers
playwright install --with-deps

# Install specific browser
playwright install chromium --with-deps

# Check browser installation
playwright install --help
```

## Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Workflow-Use      │    │   Browser-Use       │    │   Browser           │
│   Backend           │◄──►│   Web-UI            │◄──►│   Automation        │
│   (Optional)        │    │   (Gradio)          │    │   (Playwright)      │
│   Port: 8000        │    │   Port: 7788        │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         ▲                           ▲                           ▲
         │                           │                           │
         ▼                           ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Workflow UI       │    │   User Interface    │    │   Target Websites   │
│   (React)           │    │   (Web Browser)     │    │   (Any Site)        │
│   Port: 5173        │    │   http://localhost  │    │                     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Contributing

To extend the integration:

1. **Add new launcher features**: Modify the PowerShell, Python, or Bash scripts
2. **Enhance configuration**: Update environment file templates
3. **Improve Docker setup**: Modify docker-compose configurations
4. **Add monitoring**: Implement health checks and logging
5. **Create plugins**: Develop workflow-use specific extensions

## License

This integration follows the same license terms as workflow-use. The browser-use web-ui is licensed under MIT license.

## Resources

- **Browser-Use Web-UI**: https://github.com/browser-use/web-ui
- **Browser-Use Core**: https://github.com/browser-use/browser-use
- **Documentation**: https://docs.browser-use.com
- **Discord Community**: https://link.browser-use.com/discord

## Comparison with Custom Implementation

| Feature | Official Web-UI | Custom Implementation |
|---------|-----------------|----------------------|
| **Maturity** | ✅ Production-ready | ❌ Prototype |
| **LLM Support** | ✅ 8+ providers | ❌ 3 providers |
| **UI Quality** | ✅ Professional Gradio | ❌ Basic React |
| **Browser Features** | ✅ Advanced (custom browser, recording) | ❌ Basic |
| **Community** | ✅ Active development | ❌ Single developer |
| **Documentation** | ✅ Comprehensive | ❌ Minimal |
| **Mobile Support** | ✅ Responsive | ❌ Desktop only |
| **Docker Support** | ✅ Full VNC setup | ❌ Basic |
| **Maintenance** | ✅ Community maintained | ❌ Custom maintenance |

**Conclusion**: The official browser-use web-ui provides significantly more value with less maintenance overhead.

