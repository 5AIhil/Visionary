# 👁️ Visionary: Autonomous AI Workplace Safety Monitor

**Visionary** is an intelligent, real-time computer vision system that autonomously monitors workplace environments for safety compliance. It uses **Retrieval-Augmented Generation (RAG)** to dynamically learn safety policies from PDF manuals and enforces them using a **Vision-Language Model (VLM)**.

> 🚀 **Key Differentiator**: Unlike traditional CV systems that are hardcoded for specific objects (e.g., "detect hard hat"), Visionary reads a policy document (e.g., "Construction Site Safety Manual.pdf") and *understands* what to look for, adapting its behavior instantly without retraining.

---

## 🏗️ Architecture

The system is built with a modular, scalable architecture designed for maintainability and performance.

```mermaid
graph TD
    %% Global Styling
    classDef frontend fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff;
    classDef backend fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef storage fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff;
    classDef ai fill:#8b5cf6,stroke:#5b21b6,stroke-width:2px,color:#fff;

    %% -----------------------------------------------------------------
    %% 1. KNOWLEDGE INGESTION SUBGRAPH
    %% -----------------------------------------------------------------
    subgraph Data_Ingestion ["🧠 1. Knowledge Ingestion Pipeline"]
        direction TB
        Upload[Upload Safety PDF] -->|PyPDFLoader| Split[Text Chunking]
        Split -->|nomic-embed-text| ChromaDB[(Chroma Vector DB)]:::storage
        ChromaDB -->|Retrieve Rules| PromptGen[LLM Prompt Synthesizer]:::ai
        PromptGen -->|Save Persona| SystemPrompt(system_prompt.txt):::storage
    end

    %% -----------------------------------------------------------------
    %% 2. EDGE VISION CAPTURE SUBGRAPH
    %% -----------------------------------------------------------------
    subgraph Edge_Vision ["👁️ 2. IoT Edge Capture (camera.py)"]
        direction LR
        Webcam((Camera Agent)) -->|Capture 4K| Resize[Resize 640x480]
        Resize -->|Base64 Encode| Throttle{Wait 10s}
        Throttle -->|HTTP POST| APIGateway
    end

    %% -----------------------------------------------------------------
    %% 3. BACKEND ORCHESTRATOR SUBGRAPH
    %% -----------------------------------------------------------------
    subgraph Core_Backend ["⚙️ 3. Backend Orchestration (backend.py)"]
        direction TB
        APIGateway(FastAPI Gateway):::backend
        
        APIGateway -->|Read Frame + Prompt| VLM[LLaVA-phi3 Processor]:::ai
        VLM -->|Generate Description| SceneDesc[/Scene Output/]
        
        SceneDesc -->|Semantic Search| ChromaDB
        ChromaDB -.->|Inject Context| VLMJudge[LLaVA-phi3 Judge]:::ai
        
        VLMJudge -->|Produce| Verdict{Is Violation?}
    end

    %% -----------------------------------------------------------------
    %% 4. STORAGE & ALERTS SUBGRAPH
    %% -----------------------------------------------------------------
    subgraph Alerts_Storage ["🛡️ 4. Action & Auditing"]
        direction TB
        Verdict -->|Yes: Create| Evidence[Save Frame to /evidence]:::storage
        Verdict -->|Yes: Send| Telegram[[Telegram Bot API]]
        
        Verdict -->|Always: Write| DBWrite[Insert to SQLite]
        DBWrite --> SQLite[(visionary.db)]:::storage
    end

    %% -----------------------------------------------------------------
    %% 5. DASHBOARD SUBGRAPH
    %% -----------------------------------------------------------------
    subgraph UI ["💻 5. User Interface (dash.py)"]
        direction LR
        Dashboard(Streamlit App):::frontend
        Dashboard <-->|Toggle Switch| APIGateway
        Dashboard <-->|SELECT logs| SQLite
        Dashboard <-->|Load Images| Evidence
    end

    %% Connect the Subgraphs sequentially
    Edge_Vision -.->|Payload| Core_Backend
    SystemPrompt -.->|Loaded by| Core_Backend
```

---

## 🚀 Why Visionary Replaces Traditional CV (YOLO)

Traditional surveillance systems rely on object-detection models (like YOLO or RetinaNet). While fast, they fail catastrophically when introduced to complex business logic. **Visionary** uses a radically different architecture (Retrieval-Augmented Generation + Multimodal VLMs) that solves the three biggest scaling blockers in the industry:

| Feature | Legacy Systems (YOLO / OpenCV) | **Visionary (VLM + RAG)** |
| :--- | :--- | :--- |
| **Logic Updates** | **Months of Work**. Requires collecting 10,000+ images of the new object, manually drawing bounding boxes, and retraining the ML model locally. | **3 Minutes**. Zero-shot learning. Upload a new PDF text manual to the dashboard. The AI instantly reads the text and updates its behavior. |
| **Semantic Understanding** | **Brittle**. A YOLO model sees a hard hat. It does not understand if the hard hat is correctly on a worker's head, or just resting idly on a table. | **Intelligent**. The LLM semantically *understands* the scene ("The worker's head is unprotected, the hat is on the table") and applies logical reasoning. |
| **Auditing & Explainability** | **Black Box**. Spits out a rigid array of coordinates and confidence scores: `[HardHat: 0.95]`. You do not know *why* an alert fired. | **Human-Readable Audit**. Logs exact natural language scene descriptions and an explicit explanation (e.g., "Violation: Goggles are on forehead, not eyes"). |
| **Enterprise Privacy** | Historically required streaming immense high-res footage to cloud endpoints (OpenAI/AWS), posing huge IP risks. | **100% Offline Edge Compute**. By using heavily quantized small-language models (`llava-phi3`), the "Cloud Brain" runs entirely locally. |

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
1. **Python 3.10+** installed.
2. **Ollama** installed:
   - **macOS/Linux**: `curl -fsSL https://ollama.com/install.sh | sh` or `brew install ollama`
   - **Windows**: Download from [ollama.com](https://ollama.com/download)
3. **Start Ollama** (if not running in background):
   ```bash
   ollama serve
   ```
4. **Pull Required AI Models**:
   The system requires a Vision model (`llava-phi3`) and an Embedding model (`nomic-embed-text`). Run these commands in your terminal:
   ```bash
   ollama pull llava-phi3
   ollama pull nomic-embed-text
   ```

### Installation

1. Clone the repository and navigate to the project directory:
    ```bash
    git clone https://github.com/yourusername/Visionary.git
    cd Visionary
    ```
2. Set up a Python Virtual Environment:
    - **macOS/Linux**:
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```
    - **Windows**:
      ```cmd
      python -m venv venv
      venv\Scripts\activate
      ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
### Setup Telegram Alerts (Optional)
To receive real-time notifications on your phone:
1. **Get Bot Token**: Open Telegram, search and start `@BotFather`. Send `/newbot`, choose a name and username ending in `bot`. Copy the `TELEGRAM_TOKEN` provided.
2. **Get Chat ID**: Search and start `@userinfobot` to get your `Id`. Copy this as your `TELEGRAM_CHAT_ID`.
3. **Activate Bot**: Search for your bot's username and click **Start** (mandatory to allow messages).
4. **Configure Project**: Create a `.env` file in the `backend/` directory:
   ```env
   TELEGRAM_TOKEN=your_copied_token
   TELEGRAM_CHAT_ID=your_copied_chat_id
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
