# 👁️ Visionary: Autonomous AI Workplace Safety Monitor

**Visionary** is an intelligent, real-time computer vision system that autonomously monitors workplace environments for safety compliance. It uses **Retrieval-Augmented Generation (RAG)** to dynamically learn safety policies from PDF manuals and enforces them using a **Vision-Language Model (VLM)**.

> 🚀 **Key Differentiator**: Unlike traditional CV systems that are hardcoded for specific objects (e.g., "detect hard hat"), Visionary reads a policy document (e.g., "Construction Site Safety Manual.pdf") and *understands* what to look for, adapting its behavior instantly without retraining.

---

## 🏗️ Architecture

The system is built with a modular, scalable architecture designed for maintainability and performance.

```mermaid
graph TD
    A[Camera Agent] -->|Resize & Stream 0.1FPS| B(Backend API)
    B -->|Ingest PDF| C[RAG Engine]
    C -->|Generate Persona| D[System Prompt]
    B -->|Frame + Prompt| E[LLaVA-phi3 Model]
    E -->|Verdict| F{Violation?}
    F -->|Yes| G[Evidence Vault]
    F -->|Yes| H[Telegram Alert]
    F -->|Log Event| I[(SQLite DB)]
    J[Streamlit Dashboard] <-->|Sync State| B
    J <-->|Read Logs| I
```

---

## ✨ Key Features

### 1. 📚 Dynamic Policy Learning (RAG)
- **Upload any PDF manual**: The system embeds the text into a Vector Database (ChromaDB).
- **Auto-Prompting**: It generates a custom "System Persona" (e.g., *"You are a Safety Officer..."*) tailored to the specific rules in the document.
- **Strict Adherence**: The AI strictly follows the generated persona, ignoring generic behaviors.

### 2. 👁️ Real-Time Visual Intelligence
- **Model**: Powered by `llava-phi3`, a state-of-the-art quantized Vision-Language Model running locally via Ollama.
- **Performance**: Optimized for 0.1 FPS analysis to balance latency and resource usage.
- **Privacy**: All processing happens locally on-device.

### 3. 📸 Forensic Evidence Vault
- **Auto-Capture**: When a violation is detected (e.g., "No safety goggles"), the exact video frame is saved to the `backend/evidence/` vault.
- **Dashboard Integration**: Review logs in the dashboard and see the actual photo evidence side-by-side with the AI's verdict.

### 4. 🛡️ Enterprise-Grade Controls
- **Backend-Enforced State**: The "Start/Stop" buttons physically gate the backend's processing pipeline.
- **Connection Resilience**: Dashboard includes auto-retry logic for 60s during system startup (e.g., while models are loading).
- **Alerts**: Real-time notifications via Telegram bot integration.

---

## 🛠️ Technology Stack

- **Core**: Python 3.10+
- **AI/ML**: Ollama, LangChain, ChromaDB
- **Backend**: FastAPI, SQLite
- **Frontend**: Streamlit
- **Vision**: OpenCV
- **DevOps**: Modular file structure, Environment Config (.env)

---

## 📂 Project Structure

The project follows a clean, modular structure:

```text
Visionary/
├── backend/
│   ├── backend.py       # API Gateway & Orchestrator
│   ├── database.py      # SQLite Connection & Logging Logic
│   ├── alerts.py        # Telegram Notification Logic
│   ├── rag.py           # RAG Engine (Ingest & Prompt Gen)
│   ├── evidence/        # Storage for violation snapshots
│   └── system_prompt.txt # Dynamically generated AI persona
├── frontend/
│   ├── dash.py          # Main Dashboard Entry Point
│   ├── components.py    # Reusable UI Widgets
│   ├── styles.py        # CSS & Theming
│   └── camera.py        # IoT Camera Agent
├── run.py               # Master startup script
└── requirements.txt     # Dependencies
```

---

## 🚀 Getting Started

### Prerequisites
1.  **Python 3.10+** installed.
2.  **Ollama** installed and running (`ollama serve`).
3.  **Model**: Pull the vision model: `ollama pull llava-phi3` & embed model: `ollama pull nomic-embed-text`.

### Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  (Optional) Setup Telegram Alerts:
    - Create a `.env` file in `backend/` with:
        ```env
        TELEGRAM_TOKEN=your_token
        TELEGRAM_CHAT_ID=your_chat_id
        ```

### Usage

Run the entire system with a single command:

```bash
python run.py
```

This will launch:
1.  **Backend Server** (Port 8000)
2.  **Dashboard** (Port 8501)
3.  **Camera Agent** (Active immediately)

### Workflow
1.  Open the Dashboard (`http://localhost:8501`).
2.  **Upload a Safety Policy PDF**.
3.  Click **"Ingest Policy"** to train the agent.
4.  Click **"🚀 Start Operation"**.
5.  Monitor the feed for alerts!

---

## 🔮 Future Roadmap
- [ ] Multi-camera support with RTSP streams.
- [ ] Email/SMS alerts via SMTP/Twilio.
- [ ] Historical trend analysis & reporting.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
*Built with ❤️ by Sahil Bhavesh Choudhary*
