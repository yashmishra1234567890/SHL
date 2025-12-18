# SHL Assessment Recommender System

A Retrieval-Augmented Generation (RAG) application designed to intelligently recommend SHL assessments based on user queries. This system combines semantic vector search with Google's Gemini LLM to provide context-aware, accurate recommendations.

## Features

*   **Intelligent Search**: Uses `SentenceTransformers` (`all-MiniLM-L6-v2`) for semantic search, understanding user intent beyond simple keywords.
*   **AI-Powered Recommendations**: Integrates **Google Gemini 1.5 Flash** to generate natural language explanations for recommendations.
*   **Robust Data Pipeline**: Handles JSON/CSV/Excel inputs, normalizes data, and extracts metadata (like duration) from unstructured text.
*   **Hybrid Output**: Provides both human-readable text summaries and structured JSON for API integration.
*   **Evaluation Module**: Includes tools to calculate **Recall@K** metrics to verify retrieval accuracy.
*   **Resilience**: Features a fallback mechanism to return structured results even if the LLM is unavailable.

## Project Structure

```
shl/
├── data/                   # Data storage
│   ├── shl_products.json   # Source catalog
│   └── faiss_index/        # Vector database index
├── outputs/                # Generated results (JSON/CSV)
├── src/                    # Source code
│   ├── config.py           # Configuration settings
│   ├── embeddings/         # Embedding model logic
│   ├── evaluation/         # Recall@K evaluation scripts
│   ├── ingestion/          # Data loading and cleaning
│   └── rag/                # Main RAG engine
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (API keys)
```

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yashmishra1234567890/SHL.git
    cd SHL
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your Google Gemini API key:
    ```env
    GEMINI_API_KEY=your_api_key_here
    ```

## Usage

### Running the Recommendation Engine
To test the recommendation engine directly:

```bash
python src/rag/rag_engine.py
```
*This will run a test query defined in the `__main__` block of the file.*

### Running Evaluations
To evaluate the retrieval performance (Recall@K):

```bash
python src/evaluation/run_eval.py
```
*Results will be saved to `outputs/evaluation_results.csv`.*

## Configuration

Key settings can be modified in `src/config.py`:

*   `CATALOG_PATH`: Path to the input data file.
*   `TOP_K`: Number of assessments to retrieve (default: 10).
*   `EMBEDDING_MODEL`: Model used for vectorization.
*   `GEMINI_MODEL`: LLM version used for generation.

## Tech Stack

*   **Language**: Python 3.12
*   **Orchestration**: LangChain
*   **Vector Store**: FAISS
*   **LLM**: Google Gemini 1.5 Flash
*   **Embeddings**: SentenceTransformers (HuggingFace)
*   **Data Processing**: Pandas
