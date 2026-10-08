# 🎙️ AI Voice Agent

A Python-based **AI Voice Agent** that enables real-time, two-way voice interaction using **Speech-to-Text, Google Gemini, Text-to-Speech, and tool calling**.

The project contains two implementations:

* **`main.py`** — a simple conversational voice agent.
* **`cursor.py`** — an advanced agent that can reason through tasks using `START → PLAN → TOOL → OBSERVE → OUTPUT` steps and call external tools.

---

## ✨ Features

* 🎤 Voice input through microphone
* 📝 Speech-to-Text using `SpeechRecognition`
* 🤖 Google Gemini-powered responses
* 🔊 AI-generated voice responses using Gemini TTS
* 🔁 Continuous voice conversation
* 🌐 Weather information tool
* 💻 System command execution tool
* 🧠 Structured agent workflow
* 📦 Pydantic-based structured output
* 🔐 API key management using `.env`
* 🗣️ Responses designed for natural spoken interaction

---

## 🏗️ Project Architecture

### Basic Voice Agent

```text
              ┌─────────────────┐
              │      User       │
              │   Speaks Voice  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │   Microphone    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ SpeechRecognition│
              │      (STT)      │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Google Gemini  │
              │      LLM        │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Gemini TTS     │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Speaker / Audio │
              └─────────────────┘
```

### Tool-Using Voice Agent

The advanced implementation follows an agent workflow:

```text
User Voice
    │
    ▼
Speech-to-Text
    │
    ▼
START
    │
    ▼
PLAN
    │
    ├───────────────┐
    │               │
    ▼               ▼
Simple Task       TOOL
                    │
                    ▼
                 OBSERVE
                    │
                    ▼
                  PLAN
                    │
                    ▼
                  OUTPUT
                    │
                    ▼
                Gemini TTS
                    │
                    ▼
              Voice Response
```

---

## 📁 Project Structure

```text
AI-Voice-Agent/
│
├── main.py              # Basic conversational voice agent
├── cursor.py            # Tool-using AI voice agent
├── README.md
├── .env                 # API key - do not commit
├── .gitignore
└── .venv/               # Virtual environment
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_NAME>
```

---

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install openai google-genai python-dotenv SpeechRecognition sounddevice soundfile requests pydantic
```

Depending on your operating system, additional audio/microphone configuration may be required.

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
```

The application reads the API key using `python-dotenv`.

**Never commit your `.env` file to GitHub.**

Add the following to `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# ▶️ Running the Project

## Basic Voice Agent

Run:

```bash
python main.py
```

The application will:

1. Listen through your microphone.
2. Convert your speech into text.
3. Send the text to Gemini.
4. Generate an AI response.
5. Convert the response into speech.
6. Play the generated audio.
7. Continue listening for the next interaction.

The implementation uses `gemini-3.6-flash` for the conversational response and `gemini-3.8-flash-tts` for speech generation.

---

# 🧠 Advanced Agent

Run:

```bash
python cursor.py
```

The advanced implementation uses a structured agent workflow.

### Agent Steps

```text
START
  ↓
PLAN
  ↓
TOOL
  ↓
OBSERVE
  ↓
PLAN
  ↓
OUTPUT
```

Not every request requires a tool.

For a simple question:

```text
START
   ↓
PLAN
   ↓
OUTPUT
```

For a task requiring external information:

```text
START
   ↓
PLAN
   ↓
TOOL
   ↓
OBSERVE
   ↓
PLAN
   ↓
OUTPUT
```

The workflow and tool definitions are implemented directly in `cursor.py`.

---

# 🛠️ Available Tools

The advanced agent currently has two tools.

## 🌦️ Weather Tool

```python
get_weather(city)
```

This tool requests weather information from `wttr.in`.

Example:

```text
User:
What's the weather in Delhi?
```

The agent can decide to call:

```text
get_weather("delhi")
```

## The tool result is then returned to the agent as an `OBSERVE` step before the final response.

## 💻 Command Execution Tool

```python
run_command(cmd)
```

This tool executes a system command on the local machine.

It is registered as one of the available tools in the advanced agent.

### ⚠️ Security Warning

`run_command()` executes commands directly on the user's machine.

Do **not** expose this functionality to untrusted users without adding proper validation, authorization, sandboxing, and command restrictions.

---

# 🔊 Text-to-Speech

The project uses Google's GenAI client for text-to-speech.

The configured model is:

```text
gemini-3.8-flash-tts
```

The configured voice is:

```text
Kore
```

## The generated audio is read as WAV data and played using `sounddevice`.

# 🧩 Tech Stack

| Technology        | Purpose                         |
| ----------------- | ------------------------------- |
| Python            | Core application                |
| Google Gemini     | AI/LLM responses                |
| Gemini TTS        | Text-to-Speech                  |
| SpeechRecognition | Speech-to-Text                  |
| SoundDevice       | Audio playback                  |
| SoundFile         | Audio processing                |
| OpenAI Python SDK | Gemini OpenAI-compatible API    |
| Pydantic          | Structured output validation    |
| Requests          | Weather API requests            |
| python-dotenv     | Environment variable management |

---

# 📚 What This Project Demonstrates

This project was built to explore the fundamentals of **AI voice agents and tool-using agents**.

### Voice AI

* Speech-to-Text
* LLM integration
* Text-to-Speech
* Microphone input
* Audio playback
* Continuous voice interaction

### AI Agents

* Agent workflows
* Planning
* Tool calling
* Tool observation
* Structured outputs
* Function execution
* Conversation history

### API Integration

* Gemini API
* OpenAI-compatible API interface
* Weather API
* Environment variables

---

# 🔄 Example Interaction

### Basic Agent

```text
You: What is artificial intelligence?

AI: Artificial intelligence is the field of computer science
that focuses on creating systems capable of performing tasks
that normally require human intelligence.

[AI response is converted to speech]
```

### Tool-Using Agent

```text
You: What's the weather in Delhi?

START
   ↓
PLAN
   ↓
TOOL → get_weather("delhi")
   ↓
OBSERVE
   ↓
PLAN
   ↓
OUTPUT

AI: The current weather in Delhi is ...
```

---

# 🆚 `main.py` vs `cursor.py`

| Feature                   | `main.py` | `cursor.py` |
| ------------------------- | :-------: | :---------: |
| Voice Input               |     ✅     |      ✅      |
| Speech-to-Text            |     ✅     |      ✅      |
| Gemini LLM                |     ✅     |      ✅      |
| Text-to-Speech            |     ✅     |      ✅      |
| Continuous Conversation   |     ✅     |      ✅      |
| Tool Calling              |     ❌     |      ✅      |
| Weather Tool              |     ❌     |      ✅      |
| Command Tool              |     ❌     |      ✅      |
| Structured Agent Workflow |     ❌     |      ✅      |
| Pydantic Output Model     |     ❌     |      ✅      |

---

# 🔮 Future Improvements

Some possible improvements for future versions:

* [ ] Wake-word detection
* [ ] Voice Activity Detection (VAD)
* [ ] Streaming Speech-to-Text
* [ ] Streaming Text-to-Speech
* [ ] Conversation memory
* [ ] More external tools
* [ ] Tool permission system
* [ ] Safer command execution
* [ ] Web search tool
* [ ] File interaction tools
* [ ] GUI interface
* [ ] Better interruption handling
* [ ] Persistent conversation history

---

# ⚠️ Limitations

The current version is a learning-focused implementation.

The project currently depends on:

* An active internet connection
* A working microphone
* Audio playback support
* A valid Google Gemini API key
* SpeechRecognition's configured recognition service

The command execution tool should also be treated carefully because it can execute commands on the local system.

---

# 👩‍💻 Author

**Ekta Mishra**

B.Tech CSE | Full-Stack Developer | Generative AI Enthusiast

GitHub: [Ekta25Mishra](https://github.com/Ekta25Mishra)

---

## ⭐ If you found this project useful

Feel free to **star ⭐ the repository** and explore the code.

Built while learning and experimenting with **Voice AI, Gemini, and AI Agents**.
