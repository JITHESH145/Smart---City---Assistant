# Smart City Information Assistant

This project is a Smart City Information Assistant that allows users to ask questions about city services, regulations, and general information. It features a Streamlit frontend, a FastAPI backend, and a RAG (Retrieval Augmented Generation) pipeline using the Llama2 model via Ollama and ChromaDB as the vector store.

## Features

*   **Conversational Interface**: Ask questions in natural language through a Streamlit web UI.
*   **RAG Pipeline**: Utilizes a Retrieval Augmented Generation pipeline to provide answers based on a knowledge base.
*   **FastAPI Backend**: Exposes API endpoints for querying the system.
*   **Ollama Integration**: Leverges local LLMs (Llama2) through Ollama for language understanding and generation.
*   **Vector Database**: Uses ChromaDB for efficient similarity search over the knowledge base embeddings.
*   **Customizable Knowledge Base**: Works with a `knowledge.json` file.
*   **Real-time Answers**: Provides answers by querying the knowledge base and generating responses on the fly.
*   **Source Display**: Shows the source of information for transparency.

## Architecture Overview

The system consists of the following main components:

1.  **Streamlit Frontend (`app.py`)**: Provides the user interface for asking questions and displaying answers.
2.  **FastAPI Backend (`backend.py`)**: Handles incoming queries from the frontend. It orchestrates the RAG pipeline.
3.  **Vectorization & Storage (`vector.py`)**: 
    *   Loads data from `knowledge.json`.
    *   Generates embeddings for the knowledge base content using an Ollama embedding model (e.g., `mxbai-embed-large`).
    *   Stores these embeddings in a ChromaDB vector database for persistent storage (`./chroma_city_knowledge_db`).
4.  **RAG Pipeline (in `backend.py` & `vector.py`)**: 
    *   When a query is received, `vector.py` searches ChromaDB for relevant document chunks.
    *   These chunks are passed as context to the Llama2 model (via Ollama) along with the user's question.
    *   The LLM generates an answer based on the provided context.
5.  **Ollama**: Serves the Llama2 LLM and the embedding model.

## Prerequisites

*   **Python**: Version 3.9+ recommended.
*   **Ollama**: 
    *   Must be installed and running. Download from [ollama.com](https://ollama.com/).
    *   Ensure you have pulled the required models:
        ```bash
        ollama pull llama2
        ollama pull mxbai-embed-large 
        ```
        (The embedding model name `mxbai-embed-large` is specified in `vector.py`. If you change it there, pull that model instead).
*   **Git**: For cloning the repository.

## Setup and Installation

1.  **Clone the repository (if applicable, otherwise navigate to your project folder):**
    ```bash
    # git clone <your-repository-url>
    # cd <your-repository-name>
    cd "C:\Users\jithe\OneDrive\Desktop\codes\smart city agent -3" 
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```
    *   On Windows:
        ```bash
        venv\Scripts\activate
        ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Knowledge Base (`knowledge.json`):**
    *   Ensure the `knowledge.json` file is present in the project root directory: `C:\Users\jithe\OneDrive\Desktop\codes\smart city agent -3\knowledge.json`.
    *   The path to this file is currently hardcoded in `vector.py`. For better portability if sharing or moving the project, consider changing this to a relative path (e.g., `KNOWLEDGE_BASE_PATH = "knowledge.json"`) if `knowledge.json` is always in the root.

5.  **Background Image (UI Customization):**
    *   The Streamlit app (`app.py`) uses a background image referenced as `/static/266536.jpg` in its CSS.
    *   Make sure you have a `static` folder in your project root (`C:\Users\jithe\OneDrive\Desktop\codes\smart city agent -3\static\`) and the image `266536.jpg` is placed inside it.

6.  **Ollama Configuration:**
    *   The application expects the Ollama API to be available at `http://localhost:11434` by default.
    *   If your Ollama server is running on a different URL, set the `OLLAMA_BASE_URL` environment variable before starting `backend.py`.
      For example, in PowerShell:
      `$env:OLLAMA_BASE_URL="http://your-ollama-host:port"`
      Or in Bash:
      `export OLLAMA_BASE_URL="http://your-ollama-host:port"`

## Running the Application

You need to run the backend and frontend in separate terminals.

1.  **Start the Backend Server (`backend.py`):**
    *   Open a terminal, navigate to the project root (`C:\Users\jithe\OneDrive\Desktop\codes\smart city agent -3`), and activate your virtual environment if you created one.
    *   Run:
        ```bash
        python backend.py
        ```
    *   The FastAPI backend will start, typically on `http://localhost:8000`. Wait for messages indicating the LLM and RAG chain have initialized.

2.  **Start the Frontend Application (`app.py`):**
    *   Open a *new* terminal, navigate to the project root, and activate your virtual environment.
    *   Run:
        ```bash
        streamlit run app.py
        ```
    *   The Streamlit application should automatically open in your web browser (usually at `http://localhost:8501`).

## API Documentation

Once the FastAPI backend is running, interactive API documentation is automatically available at:

*   **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
*   **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

You can use these interfaces to explore and test the API endpoints directly.

## Project Structure

```
. (smart city agent -3)
├── app.py                  # Streamlit frontend application
├── backend.py              # FastAPI backend server (RAG logic)
├── vector.py               # Knowledge base processing, embedding, ChromaDB interaction
├── knowledge.json          # Your city-specific knowledge base data
├── requirements.txt        # Python dependencies
├── static/
│   └── 266536.jpg          # Background image for the UI
├── chroma_city_knowledge_db/ # Directory for persistent ChromaDB data (created by vector.py)
└── README.md               # This file
```

## Knowledge Base Usage

(Refer to your separate "Knowledge Base Usage Report" for details on how `knowledge.json` is processed and utilized by the RAG pipeline.) 
