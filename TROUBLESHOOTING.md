markdown
# 🔧 Vireo Troubleshooting Guide

This guide helps you resolve common issues when running Vireo.

---

## 1. Windows SmartScreen Blocks start_vireo.bat

**Problem:** When running `start_vireo.bat`, Windows shows:
Intelligent Application Control blocked a file that may be unsafe

text

**Solution:**

### Option 1: Unblock the file

1. Right-click on `start_vireo.bat` → **Properties**
2. Under the **General** tab, find the message:
   > "This file came from another computer and might be blocked"
3. Check the box: **Unblock**
4. Click **Apply** → **OK**

### Option 2: Run manually

```bash
cd path/to/vireo-ai-communicator-3
python api_server.py
Option 3: Create a new batch file
Create a new run.bat with:

batch
@echo off
cd /d "C:\Users\Startklar\Desktop\vireo-ai-communicator-3"
python api_server.py
pause
2. Port 5000 is already in use
Problem: When starting the server, you see:

text
OSError: [Errno 98] Address already in use
Solution:

bash
# Find the process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with the actual number)
taskkill /F /PID XXXXX
Or use a different port:

python
# In api_server.py, change:
app.run(host='0.0.0.0', port=5001, debug=True)
3. Flask is not installed
Problem: When running python api_server.py, you see:

text
ModuleNotFoundError: No module named 'flask'
Solution:

bash
pip install flask flask-cors cryptography
Or install all dependencies:

bash
pip install -r requirements.txt
4. Ollama is not running
Problem: When using Ollama provider, you see:

text
ConnectionError: Ollama not running
Solution:

bash
# Start Ollama
ollama serve

# Pull the recommended model
ollama pull qwen2.5-coder:latest
5. API key not set (Gemini, Claude, OpenAI, Mistral)
Problem: When using a paid provider, you see:

text
Error: ANTHROPIC_API_KEY not set
Solution:

Create a .env file in the project root

Add your API keys:

env
# Claude (Anthropic)
ANTHROPIC_API_KEY=sk-ant-...

# OpenAI
OPENAI_API_KEY=sk-...

# Google Gemini
GOOGLE_API_KEY=...

# Mistral
MISTRAL_API_KEY=...
For Ollama, no API key is needed (free and local)

6. Web interface not loading
Problem: http://localhost:5000/web shows nothing or an error

Solution:

Make sure the server is running:

bash
python api_server.py
Check if web_interface.html exists in the project folder

Try accessing:

http://localhost:5000 — API status

http://localhost:5000/docs — Documentation

http://localhost:5000/web — Web interface

Check the console for errors

7. Tensor operations not working
Problem: Tensor operations return text instead of real values

Solution:

Make sure you are using Vireo v1.4.2 or later. In older versions, tensor operations were emulated.

Correct output:

text
Tensor(shape=[5])
Instead of:

text
Tensor operation
8. Agent registration fails
Problem: When registering an agent, you see:

text
"Protocol module not available"
Solution:

Make sure you're using the latest api_server.py

The protocol module is now built-in, no external installation needed

Restart the server after updating

9. Still having issues?
Check the logs: Look at the console output for error messages

Update the project:

bash
git pull origin main
Reinstall dependencies:

bash
pip install -r requirements.txt --upgrade
Open an issue: https://github.com/serhohro/vireo-ai-communicator-api/issues

📚 Additional Resources
README.md — Project overview and quick start

PROTOCOL.md — Full AI-to-AI protocol specification

CONTRIBUTING.md — How to contribute

🌿 Vireo — A Language Designed for AI-to-AI Communication