# SHL Assessment Recommender System

A **Retrieval-Augmented Generation (RAG)** application designed to intelligently recommend **SHL assessments** based on user queries. The system combines **semantic vector search** with **Google’s Gemini LLM** to deliver context-aware, accurate, and explainable assessment recommendations.

This project is built with a production-oriented mindset, focusing on clean architecture, evaluation, and fallback reliability.

---

## 🚀 Features

* **Intelligent Semantic Search**
  Uses **SentenceTransformers (all-MiniLM-L6-v2)** to understand user intent beyond simple keyword matching.

* **AI-Powered Recommendations**
  Integrates **Google Gemini 1.5 Flash** to generate natural-language explanations for why specific assessments are recommended.

* **Robust Data Pipeline**

  * Supports **JSON, CSV, and Excel** input formats
  * Automatically normalizes column names
  * Extracts metadata (e.g., duration) from unstructured text using regex

* **Hybrid Output System**

  * **Human-readable** formatted summaries for end users
  * **Machine-readable** structured JSON output for API or downstream integration

* **Evaluation Module**
  Built-in tools to calculate **Recall@K** metrics for validating retrieval accuracy using a known-item search methodology.

* **Resilient Design**
  Includes a fallback mechanism that returns structured semantic search results even if the LLM is unavailable or rate-limited.

---

## 🧠 System Architecture (High-Level)

1. **Ingestion Layer**
   Loads and cleans the SHL product catalog and creates a combined text field for embedding.

2. **Embedding & Vector Store**
   Converts assessment text into dense vectors using SentenceTransformers and stores them in **FAISS** for fast similarity search.

3. **RAG Engine**
   Retrieves the most relevant assessments and enriches the prompt before sending it to the Gemini LLM for final response generation.

4. **Evaluation Module**
   Measures retrieval quality using Recall@K and exports evaluation results.

---

## 📁 Project Structure

```
shl/
├── data/                   # Data storage
│   ├── shl_products.json   # Source assessment catalog
│   └── faiss_index/        # FAISS vector index
├── outputs/                # Generated outputs (JSON / CSV)
├── src/                    # Source code
│   ├── config.py           # Global configuration
│   ├── embeddings/         # Embedding logic
│   ├── evaluation/         # Recall@K evaluation scripts
│   ├── ingestion/          # Data loading and cleaning
│   └── rag/                # Core RAG engine
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (API keys)
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yashmishra1234567890/SHL.git
cd SHL
```

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv .venv
```

**Windows**

```bash
.venv\Scripts\activate
```

**Mac / Linux**

```bash
source .venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_api_key_here
```

---

## ▶️ Usage

### 🔹 Run the Recommendation Engine

To test the RAG pipeline with a sample query:

```bash
python src/rag/rag_engine.py
```

This executes a test query defined in the `__main__` block and outputs:

* A human-readable recommendation summary
* A structured JSON response

---

### 🔹 Run Retrieval Evaluation (Recall@K)

To evaluate semantic search performance:

```bash
python src/evaluation/run_eval.py
```

Evaluation results will be saved to:

```
outputs/evaluation_results.csv
```

---

## ⚙️ Configuration

Key configuration options can be modified in `src/config.py`:

* `CATALOG_PATH` – Path to the SHL catalog file
* `TOP_K` – Number of assessments to retrieve (default: 10)
* `EMBEDDING_MODEL` – SentenceTransformer model name
* `GEMINI_MODEL` – Gemini LLM version used for generation

---

## 🧪 Evaluation Methodology

The system uses **Recall@K** to evaluate retrieval accuracy:

* Measures whether the correct assessment appears in the top **K** retrieved results
* Suitable for known-item and recommendation-style search systems
* Helps validate embedding quality and retrieval logic

---

## 🛠 Tech Stack

* **Language:** Python 3.12
* **Orchestration:** LangChain
* **Vector Database:** FAISS
* **LLM:** Google Gemini 1.5 Flash
* **Embeddings:** SentenceTransformers (HuggingFace)
* **Data Processing:** Pandas

---

## 📌 Use Cases

* Automated SHL assessment recommendation from job descriptions
* HR-tech and recruitment platforms
* Skill-based assessment discovery systems
* GenAI-powered search and recommendation demos


*Live Demo:- https://jclg3riyas8cdlxmcdfcxs.streamlit.app/

