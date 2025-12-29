import os
import uuid
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from config import PINECONE_API_KEY, INDEX_NAME

# Init Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(INDEX_NAME)

# 1024-dim embedding model
embed_model = SentenceTransformer("BAAI/bge-large-en-v1.5")


def ingest_pdfs(file_paths, user_id="default"):
    docs = []

    for path in file_paths:
        loader = PyPDFLoader(path)
        pdf_docs = loader.load()

        for d in pdf_docs:
            d.metadata["pdf_name"] = os.path.basename(path)
            d.metadata["user_id"] = user_id

        docs.extend(pdf_docs)

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    texts = [c.page_content for c in chunks]
    embeddings = embed_model.encode(texts).tolist()

    vectors = []
    for emb, c in zip(embeddings, chunks):
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": emb,
            "metadata": {
                "pdf_name": c.metadata.get("pdf_name"),
                "user_id": c.metadata.get("user_id"),
                "page": c.metadata.get("page"),
                "text": c.page_content
            }
        })

    index.upsert(vectors=vectors)
