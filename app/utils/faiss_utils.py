import numpy as np
import faiss

def build_faiss_index_from_summary(summary: str):
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer('all-mpnet-base-v2')
    sentences = [s.strip() for s in summary.split('.') if s.strip()]
    if not sentences:
        return None, {}
    embeddings = embedding_model.encode(sentences)
    embeddings = np.array(embeddings).astype("float32")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    mapping = {i: sentence for i, sentence in enumerate(sentences)}
    return index, mapping
