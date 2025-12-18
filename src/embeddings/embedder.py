from sentence_transformers import SentenceTransformer

def load_embedder(model_name: str) -> SentenceTransformer:
    print(f"Loading embedding model: {model_name}...")
    return SentenceTransformer(model_name)

def embed_texts(model: SentenceTransformer, texts: list) -> list:
    return model.encode(texts, show_progress_bar=True).astype("float32")
