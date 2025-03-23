import numpy as np
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from app.config import db
from app.models import ChatQuery
from app.utils.faiss_utils import build_faiss_index_from_summary
from app.utils.gemini_utils import gemini_inference

router = APIRouter()

@router.post("/rag_chat")
async def rag_chat_endpoint(request: ChatQuery) -> JSONResponse:
    query = request.query
    try:
        docs = db.collection("transcription_summaries").order_by("timestamp", direction="DESCENDING").limit(1).stream()
        summary = None
        for doc in docs:
            summary = doc.to_dict().get("summary")
        if not summary:
            return JSONResponse(content={"response": "No transcription summary available. Please transcribe first."})
    except Exception as e:
        return JSONResponse(content={"response": f"Error retrieving summary from Firestore: {e}"})
        
    index, mapping = build_faiss_index_from_summary(summary)
    if index is None:
        return JSONResponse(content={"response": "Unable to build FAISS index from summary."})
    
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer('all-mpnet-base-v2')
    query_embedding = embedding_model.encode(query)
    query_embedding = np.array([query_embedding]).astype("float32")
    k = 5
    distances, indices = index.search(query_embedding, k)
    retrieved_context = [mapping.get(idx, "") for idx in indices[0]]
    context_text = "\n".join(retrieved_context)
    
    llm_prompt = (
        "You are a helpful and empathetic AI medical assistant. Answer the following question based on the provided meeting summary context.\n\n"
        "Example 1:\n"
        "Context: The patient reported chest pain and shortness of breath, and the doctor noted possible ischemia. Nitroglycerin was prescribed.\n"
        "Question: What did the doctor say about my chest pain?\n"
        "Answer: The doctor observed that you experienced chest pain and shortness of breath, suggesting possible ischemia, and prescribed nitroglycerin.\n\n"
        "Example 2:\n"
        "Context: The patient's blood pressure was high, and lifestyle changes were recommended along with a follow-up in three months.\n"
        "Question: What should I do about my blood pressure?\n"
        "Answer: The doctor advised you to adopt lifestyle changes, such as a low-sodium diet and regular exercise, with a follow-up appointment in three months.\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )
    response_text = gemini_inference(llm_prompt)
    return JSONResponse(content={"response": response_text, "retrieved_context": retrieved_context})
