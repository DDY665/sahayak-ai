from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)


class SessionStoreMixin:
    """Per-user/per-chat FAISS vector store management."""

    def _session_store_dir(self, user_id: str, chat_id: str) -> Path:
        path = self._base_vector_db_dir / user_id / chat_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _load_session_store(self, user_id: str, chat_id: str) -> Optional[FAISS]:
        store_dir = self._session_store_dir(user_id, chat_id)
        faiss_file = store_dir / "index.faiss"
        pkl_file = store_dir / "index.pkl"
        if not (faiss_file.exists() and pkl_file.exists()):
            return None
        try:
            return FAISS.load_local(
                str(store_dir),
                embeddings=self.embedding_model,
                allow_dangerous_deserialization=True,
            )
        except Exception as e:
            logger.warning(f"[STORE] Failed to load session store {user_id}/{chat_id}: {e}")
            return None

    def _save_session_store(self, user_id: str, chat_id: str, store: FAISS) -> None:
        store_dir = self._session_store_dir(user_id, chat_id)
        store.save_local(str(store_dir))

    def _get_or_load_session_store(self, user_id: str, chat_id: str) -> Optional[FAISS]:
        key = f"{user_id}/{chat_id}"
        if key not in self._session_stores or self._session_stores.get(key) is None:
            self._session_stores[key] = self._load_session_store(user_id, chat_id)

        # Fallback: check default or any other subfolders for this user
        if self._session_stores.get(key) is None and user_id:
            if chat_id != "default":
                default_store = self._load_session_store(user_id, "default")
                if default_store is not None:
                    return default_store
            user_base = self._base_vector_db_dir / user_id
            if user_base.exists() and user_base.is_dir():
                for sub in user_base.iterdir():
                    if sub.is_dir() and sub.name != chat_id and (sub / "index.faiss").exists():
                        sub_store = self._load_session_store(user_id, sub.name)
                        if sub_store is not None:
                            return sub_store

        return self._session_stores.get(key)

    def _set_session_store(self, user_id: str, chat_id: str, store: Optional[FAISS]) -> None:
        self._session_stores[f"{user_id}/{chat_id}"] = store

    def _all_documents_for_session(self, user_id: str, chat_id: str) -> list[Document]:
        store = self._get_or_load_session_store(user_id, chat_id)
        if store is None:
            return []
        doc_dict = getattr(store.docstore, "_dict", {})
        return [doc for doc in doc_dict.values() if isinstance(doc, Document)]

    def list_documents_for_session(self, user_id: str, chat_id: str) -> list[dict]:
        from collections import Counter
        counts: Counter[str] = Counter()
        for doc in self._all_documents_for_session(user_id, chat_id):
            source = str(doc.metadata.get("source", "unknown"))
            counts[source] += 1
        return [
            {"filename": filename, "chunks": chunks}
            for filename, chunks in sorted(counts.items(), key=lambda item: item[0].lower())
        ]

    def delete_document_for_session(self, user_id: str, chat_id: str, filename: str) -> int:
        docs = self._all_documents_for_session(user_id, chat_id)
        if not docs:
            return 0
        remaining = [doc for doc in docs if doc.metadata.get("source") != filename]
        removed_count = len(docs) - len(remaining)
        if removed_count == 0:
            return 0
        store_dir = self._session_store_dir(user_id, chat_id)
        if not remaining:
            self._set_session_store(user_id, chat_id, None)
            for file_name in ("index.faiss", "index.pkl"):
                path = store_dir / file_name
                if path.exists():
                    path.unlink()
            return removed_count
        new_store = FAISS.from_documents(remaining, self.embedding_model)
        self._save_session_store(user_id, chat_id, new_store)
        self._set_session_store(user_id, chat_id, new_store)
        return removed_count

    def ingest_file_for_session(self, file_path: str, user_id: str, chat_id: str) -> int:
        docs = self._load_documents(file_path)
        filename = Path(file_path).name
        for doc in docs:
            doc.metadata["source"] = filename
        chunks = self.splitter.split_documents(docs)
        if not chunks:
            logger.warning(f"[STORE] No chunks extracted from {file_path}")
            return 0
        store = self._get_or_load_session_store(user_id, chat_id)
        if store is None:
            store = FAISS.from_documents(chunks, self.embedding_model)
        else:
            store.add_documents(chunks)
        self._save_session_store(user_id, chat_id, store)
        self._set_session_store(user_id, chat_id, store)
        logger.info(f"[STORE] Ingested {len(chunks)} chunks for session {user_id}/{chat_id}, file={filename}")
        return len(chunks)
