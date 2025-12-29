from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from config import PINECONE_API_KEY, INDEX_NAME, GROQ_API_KEY

# Init Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# Embedding model (1024 dims)
embed_model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# Groq LLM
llm = ChatGroq(
    model="llama-3.1-8b-instant",  # correct model name
    api_key=GROQ_API_KEY,
    temperature=0
)

def get_answer(query: str, user_id: str = "default") -> str:
    # Encode query
    query_vec = embed_model.encode([query]).tolist()[0]

    # Search Pinecone
    res = index.query(
        vector=query_vec,
        top_k=5,
        include_metadata=True,
        filter={"user_id": user_id}
    )

    matches = res.get("matches", [])
    if not matches:
        return "No relevant content found."

    # Build context from stored chunks
    context = "\n\n".join(m["metadata"].get("text", "") for m in matches)

    prompt = f"""
Answer using only the context below.

Context:
{context}

Question: {query}
"""

    # Generate answer
    return llm.invoke(prompt).content


