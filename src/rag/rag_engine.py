import sys
import os
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Add project root to sys.path if running directly
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.embeddings import Embeddings

from src.embeddings.embedder import load_embedder
from src.ingestion.load_catalog import load_catalog
from src.config import EMBEDDING_MODEL, GEMINI_MODEL, CATALOG_PATH, TOP_K

load_dotenv()


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name):
        self.model = load_embedder(model_name)

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode([text])[0].tolist()
    
    def __call__(self, text):
        return self.embed_query(text)


class AssessmentRecommendationEngine:
    def __init__(self, index_path="data/faiss_index"):
        self.embeddings = SentenceTransformerEmbeddings(EMBEDDING_MODEL)
        
        # Load or build the FAISS index
        if os.path.exists(index_path):
            try:
                self.vector_store = FAISS.load_local(
                    index_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print(f"Loaded FAISS index from {index_path}")
            except Exception as e:
                print(f"Error loading FAISS index: {e}")
                raise
        else:
            print(f"Index not found at {index_path}. Building new index...")
            df = load_catalog(CATALOG_PATH)
            texts = df["combined_text"].tolist()
            
            # Convert DataFrame rows to metadata dicts
            # Handle NaN values in metadata which FAISS/LangChain might dislike
            df_meta = df.fillna("")
            metadatas = df_meta.to_dict(orient="records")
            
            self.vector_store = FAISS.from_texts(
                texts, 
                self.embeddings, 
                metadatas=metadatas
            )
            self.vector_store.save_local(index_path)
            print(f"Created and saved FAISS index to {index_path}")

        # Initialize LLM (Gemini)
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.llm = ChatGoogleGenerativeAI(
                model=GEMINI_MODEL,
                google_api_key=api_key,
                temperature=0.3
            )
        else:
            print("Warning: GEMINI_API_KEY not found. LLM features will be disabled.")
            self.llm = None

    def search(self, query, k=3):
        docs = self.vector_store.similarity_search(query, k=k)
        return docs

    def _save_to_files(self, data):
        try:
            output_dir = Path("outputs")
            output_dir.mkdir(exist_ok=True)
            
            # Save JSON
            with open(output_dir / "output.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            # Save CSV
            df = pd.DataFrame(data)
            df.to_csv(output_dir / "output.csv", index=False)
            print(f"Saved results to {output_dir}/output.json and {output_dir}/output.csv")
        except Exception as e:
            print(f"Error saving outputs: {e}")

    def recommend(self, query):
        # 1. Retrieve relevant documents
        retrieved_docs = self.search(query, k=TOP_K)

        if not retrieved_docs:
            return "I couldn't find any relevant assessments for your request."

        # Construct context from metadata to ensure all fields are available to the LLM
        context_entries = []
        for doc in retrieved_docs:
            meta = doc.metadata
            entry = (
                f"Name: {meta.get('name', 'N/A')}\n"
                f"Test Type: {meta.get('test_type', 'N/A')}\n"
                f"Description: {meta.get('description', 'N/A')}\n"
                f"Remote Testing: {meta.get('remote_support', 'N/A')}\n"
                f"Adaptive/IRT: {meta.get('adaptive_support', 'N/A')}\n"
                f"Duration: {meta.get('duration', 'N/A')}\n"
            )
            context_entries.append(entry)
        
        context_text = "\n---\n".join(context_entries)

        # 2. If LLM is available, generate a response
        if self.llm:
            prompt_template = """
            You are an expert consultant for SHL, a global leader in talent acquisition and management.
            Your goal is to recommend the best assessments based on the user's needs.

            Use the following context (details about SHL assessments) to answer the user's request.
            
            Context:
            {context}

            User Request: {query}

            Please provide recommendations in the following format for each assessment:

            Recommended Assessments
            [Number]. [Assessment Name]
            Test Type: [Test Type]

            Description:
            [Description]

            Remote Testing: [Yes/No]

            Adaptive/IRT: [Yes/No]

            Duration: [Duration]

            If the answer is not in the context, say you don't have enough information.
            """

            prompt = PromptTemplate(
                template=prompt_template,
                input_variables=["context", "query"]
            )

            # Using LCEL (LangChain Expression Language)
            try:
                chain = prompt | self.llm | StrOutputParser()
                response = chain.invoke({"context": context_text, "query": query})
                return response
            except Exception as e:
                print(f"LLM generation failed (likely rate limit): {e}")
                print("Falling back to raw search results.")
                # Fallback to raw results logic below...
        
        # 3. Fallback (or if LLM failed): Return raw search results formatted nicely
        results = "I couldn't generate a summarized recommendation due to high server load, but here are the most relevant assessments I found:\n\n"
        results += "Recommended Assessments\n"
        
        recommendations_list = []
        
        for i, doc in enumerate(retrieved_docs, 1):
            meta = doc.metadata
            
            # Format duration nicely
            duration = meta.get('duration', 'N/A')
            if duration and duration != 'N/A' and 'minute' not in str(duration).lower():
                duration_display = f"{duration} minutes"
            else:
                duration_display = duration

            # Build text output
            results += f"{i}. {meta.get('name', 'Unknown Title')}\n"
            results += f"Test Type: {meta.get('test_type', 'N/A')}\n\n"
            results += f"Description:\n{meta.get('description', 'No description available.')}\n\n"
            results += f"Remote Testing: {meta.get('remote_support', 'N/A')}\n"
            results += f"Adaptive/IRT: {meta.get('adaptive_support', 'N/A')}\n"
            results += f"Duration: {duration_display}\n\n"
            
            # Construct structured data for JSON/CSV
            json_data = {
                "name": meta.get('name', 'N/A'),
                "url": meta.get('url', 'N/A'),
                "description": meta.get('description', 'N/A'),
                "test_type": [t.strip() for t in str(meta.get('test_type', '')).split(',')] if meta.get('test_type') else [],
                "remote_support": meta.get('remote_support', 'N/A'),
                "adaptive_support": meta.get('adaptive_support', 'N/A'),
                "duration": duration_display
            }
            recommendations_list.append(json_data)
            
            results += "🧩 Backend JSON (API response example)\n"
            results += json.dumps(json_data, indent=2) + "\n\n"
        
        self._save_to_files(recommendations_list)
        return results


if __name__ == "__main__":
    # Test the engine
    engine = AssessmentRecommendationEngine()
    test_query = "Data Warehousing Concepts"
    print(f"Query: {test_query}")
    print("-" * 50)
    try:
        recommendation = engine.recommend(test_query)
        print(recommendation)
    except Exception as e:
        print(f"Error during recommendation: {e}")

