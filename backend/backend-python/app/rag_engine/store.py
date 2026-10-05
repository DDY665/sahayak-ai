from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app.llm_factory import build_llm_from_env
from app.rag_engine.session_store import SessionStoreMixin
from app.rag_engine.ocr import extract_ocr_from_pdf, extract_ocr_from_image

load_dotenv()
logger = logging.getLogger(__name__)

# Adaptive offline loading: on Windows default to offline to avoid hub timeouts, but respect environment override
hf_offline = os.getenv("HF_HUB_OFFLINE", "1" if os.name == "nt" else "0")
if hf_offline == "1":
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    local_files_only = True
else:
    local_files_only = False


class RAGStoreMixin(SessionStoreMixin):
    def __init__(self) -> None:
        self._base_vector_db_dir = Path(os.getenv("VECTOR_DB_DIR", "./vectorstore"))
        self._base_vector_db_dir.mkdir(parents=True, exist_ok=True)
        self._session_stores: Dict[str, Optional[FAISS]] = {}

        self.embedding_model = HuggingFaceEmbeddings(
            model_name=os.getenv(
                "EMBEDDING_MODEL",
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            ),
            model_kwargs={"device": "cpu", "local_files_only": local_files_only},
            encode_kwargs={"normalize_embeddings": True},
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=900, chunk_overlap=150, separators=["\n\n", "\n", " ", ""],
        )
        self.summary_llm = build_llm_from_env(purpose="summary")
        self.chat_llm = build_llm_from_env(purpose="chat")
        self.prompt = ChatPromptTemplate.from_template(
            """You are SahayakAI, an intelligent, empathetic, and expert document assistant.
Your job is to explain document contents in simple, clear language and have natural, helpful conversations about the document.
You handle technical papers, medical reports, government schemes, financial/bank documents, and general documents.

Conversation History:
{history_context}

Document Context:
{context}

Current User Input: {question}

Instructions:
1. Conversational Continuity & Context:
   - Pay close attention to the Conversation History.
   - If you previously asked the user a question, gave a quiz, or presented options (e.g., A, B, C, D) and the user responds with their answer (e.g., "A", "B", "option 2", "yes", "no"), evaluate their response, state whether they are correct or incorrect, and clearly explain why using the document context.
   - If the user provides a short or vague follow-up (e.g., "why?", "explain that", "what do you mean?", "tell me more", "how?"), understand it in relation to the previous discussion and the document context, and provide a clear, helpful explanation.
   - If the user asks for a quiz or test (e.g., "test me", "quiz me"), generate an engaging question with options based on the document.

2. Document Grounding:
   - Base your factual statements on the Document Context provided.
   - If the user asks about a specific fact, policy, or detail that is genuinely not mentioned anywhere in the document context and cannot be inferred, politely let them know that this specific detail is not mentioned in the document.
   - Do NOT say "I could not find this information in the document" when the user is simply chatting, answering a quiz question, saying hello/thank you, or asking a follow-up about prior statements.

3. Tone and Formatting:
   - Always respond in {language}.
   - Use simple language that a non-technical person can easily understand. Explain any technical jargon.
   - Format responses clearly using markdown (bold text, bullet points, numbered lists, or tables where appropriate).
   - Each context block includes a source label like [filename]. Reference or cite [filename] when mentioning specific facts from the document.

Helpful Answer:"""
        )

    def _resolve_session_db_dir(self, user_id: str, chat_id: str) -> Path:
        session_dir = self._base_vector_db_dir / user_id / chat_id
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir

    def _load_documents(self, file_path: str) -> List[Document]:
        ext = Path(file_path).suffix.lower()
        if ext == ".pdf":
            docs: List[Document] = []
            try:
                docs = PyPDFLoader(file_path).load()
            except Exception as exc:
                logger.warning(f"[STORE] PyPDFLoader failed on {file_path}: {exc}")

            total_text = "".join(doc.page_content for doc in docs).strip()
            if len(total_text) < 50:
                logger.info(
                    f"[STORE] PDF {file_path} has minimal digital text ({len(total_text)} chars). "
                    "Running Vision OCR fallback..."
                )
                ocr_docs = extract_ocr_from_pdf(file_path)
                if ocr_docs:
                    return ocr_docs
            return docs

        if ext == ".docx":
            return Docx2txtLoader(file_path).load()
        if ext in {".txt", ".md"}:
            return TextLoader(file_path, encoding="utf-8").load()
        if ext in {".png", ".jpg", ".jpeg", ".webp"}:
            return extract_ocr_from_image(file_path)
        raise ValueError(f"Unsupported file type: {ext}")

    def ingest_file(self, file_path: str) -> int:
        return self.ingest_file_for_session(file_path, "anonymous", "default")

    def get_indexed_documents(self) -> List[dict]:
        return []

    def delete_document(self, filename: str) -> bool:
        return False

    def reindex_document(self, filename: str) -> bool:
        return False
