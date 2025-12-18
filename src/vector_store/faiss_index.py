import faiss
import numpy as np

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))
    return index

def search_index(index, query_vec, top_k):
    scores, idx = index.search(query_vec.astype("float32"), top_k)
    return idx[0]
