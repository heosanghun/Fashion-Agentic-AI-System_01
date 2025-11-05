"""
Vector DB 기반 RAG 구현

Pilot 단계에서 사용할 실제 RAG 시스템
Chroma 또는 FAISS를 사용한 벡터 검색
"""

from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("ChromaDB를 사용할 수 없습니다. pip install chromadb 실행 필요")

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("FAISS를 사용할 수 없습니다. pip install faiss-cpu 실행 필요")


class VectorRAG:
    """
    Vector DB 기반 RAG
    
    실제 벡터 데이터베이스를 사용한 지식 검색
    """
    
    def __init__(
        self,
        vector_db_type: str = "chroma",
        persist_directory: Optional[str] = None,
        embedding_model: Optional[str] = None
    ):
        """
        Vector RAG 초기화
        
        Args:
            vector_db_type: "chroma" 또는 "faiss"
            persist_directory: 데이터 영구 저장 디렉토리
            embedding_model: 임베딩 모델 이름 (기본: sentence-transformers)
        """
        self.vector_db_type = vector_db_type
        self.persist_directory = persist_directory or str(Path(__file__).parent.parent / "rag_db")
        self.embedding_model = embedding_model
        
        if vector_db_type == "chroma" and CHROMA_AVAILABLE:
            self._init_chroma()
        elif vector_db_type == "faiss" and FAISS_AVAILABLE:
            self._init_faiss()
        else:
            print("벡터 DB를 사용할 수 없습니다. Mock 모드로 동작합니다.")
            self.vector_db = None
            self.use_vector_db = False
        
        # 임베딩 모델 로딩 (지연 로딩)
        self.embedder = None
    
    def _init_chroma(self):
        """ChromaDB 초기화"""
        try:
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_directory
            ))
            self.collection = self.client.get_or_create_collection(
                name="fashion_knowledge",
                metadata={"description": "패션 지식 베이스"}
            )
            self.use_vector_db = True
            print("ChromaDB 초기화 완료")
        except Exception as e:
            print(f"ChromaDB 초기화 실패: {e}")
            self.use_vector_db = False
    
    def _init_faiss(self):
        """FAISS 초기화"""
        try:
            # FAISS 인덱스 생성 (384차원, L2 거리)
            self.dimension = 384
            self.index = faiss.IndexFlatL2(self.dimension)
            self.texts = []
            self.metadata = []
            self.use_vector_db = True
            print("FAISS 초기화 완료")
        except Exception as e:
            print(f"FAISS 초기화 실패: {e}")
            self.use_vector_db = False
    
    def _get_embedder(self):
        """임베딩 모델 로딩 (지연 로딩)"""
        if self.embedder is None:
            try:
                from sentence_transformers import SentenceTransformer
                model_name = self.embedding_model or "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
                self.embedder = SentenceTransformer(model_name)
                print(f"임베딩 모델 로딩 완료: {model_name}")
            except ImportError:
                print("sentence-transformers를 설치해주세요: pip install sentence-transformers")
                self.embedder = None
        return self.embedder
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """
        문서 추가
        
        Args:
            documents: 문서 텍스트 리스트
            metadatas: 메타데이터 리스트
            ids: 문서 ID 리스트
        """
        if not self.use_vector_db:
            print("벡터 DB가 사용 불가능합니다.")
            return
        
        embedder = self._get_embedder()
        if embedder is None:
            print("임베딩 모델을 사용할 수 없습니다.")
            return
        
        # 임베딩 생성
        embeddings = embedder.encode(documents).tolist()
        
        if self.vector_db_type == "chroma":
            self._add_to_chroma(documents, embeddings, metadatas, ids)
        elif self.vector_db_type == "faiss":
            self._add_to_faiss(documents, embeddings, metadatas, ids)
    
    def _add_to_chroma(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]],
        ids: Optional[List[str]]
    ):
        """ChromaDB에 문서 추가"""
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        if metadatas is None:
            metadatas = [{}] * len(documents)
        
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"ChromaDB에 {len(documents)}개 문서 추가 완료")
    
    def _add_to_faiss(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]],
        ids: Optional[List[str]]
    ):
        """FAISS에 문서 추가"""
        embeddings_array = np.array(embeddings).astype('float32')
        self.index.add(embeddings_array)
        self.texts.extend(documents)
        if metadatas:
            self.metadata.extend(metadatas)
        else:
            self.metadata.extend([{}] * len(documents))
        print(f"FAISS에 {len(documents)}개 문서 추가 완료")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        유사 문서 검색
        
        Args:
            query: 검색 쿼리
            top_k: 상위 k개 결과 반환
            filter_metadata: 메타데이터 필터
            
        Returns:
            검색 결과 리스트
        """
        if not self.use_vector_db:
            return []
        
        embedder = self._get_embedder()
        if embedder is None:
            return []
        
        # 쿼리 임베딩
        query_embedding = embedder.encode([query])[0]
        
        if self.vector_db_type == "chroma":
            return self._search_chroma(query, query_embedding, top_k, filter_metadata)
        elif self.vector_db_type == "faiss":
            return self._search_faiss(query, query_embedding, top_k)
        
        return []
    
    def _search_chroma(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int,
        filter_metadata: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """ChromaDB 검색"""
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=filter_metadata
        )
        
        search_results = []
        if results['documents'] and len(results['documents'][0]) > 0:
            for i in range(len(results['documents'][0])):
                search_results.append({
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else 0.0
                })
        
        return search_results
    
    def _search_faiss(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """FAISS 검색"""
        query_array = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(query_array, min(top_k, len(self.texts)))
        
        search_results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.texts):
                search_results.append({
                    "document": self.texts[idx],
                    "metadata": self.metadata[idx] if idx < len(self.metadata) else {},
                    "distance": float(distances[0][i])
                })
        
        return search_results


# RAG Store와 통합
class VectorRAGStore:
    """Vector RAG Store 래퍼"""
    
    def __init__(self, vector_db_type: str = "chroma"):
        self.vector_rag = VectorRAG(vector_db_type=vector_db_type)
        self.initialized = False
    
    def initialize(self, knowledge_base: Optional[Dict[str, Any]] = None):
        """지식 베이스 초기화"""
        if self.initialized:
            return
        
        # 기본 지식 베이스 추가
        if knowledge_base:
            documents = []
            metadatas = []
            for category, items in knowledge_base.items():
                if isinstance(items, dict):
                    for key, value in items.items():
                        documents.append(f"{category}: {key} - {value}")
                        metadatas.append({"category": category, "key": key})
                elif isinstance(items, list):
                    for item in items:
                        documents.append(f"{category}: {item}")
                        metadatas.append({"category": category})
            
            if documents:
                self.vector_rag.add_documents(documents, metadatas)
        
        self.initialized = True
    
    def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """지식 검색"""
        results = self.vector_rag.search(query, top_k)
        
        return {
            "suggestions": [
                {
                    "document": r["document"],
                    "metadata": r["metadata"],
                    "relevance": 1.0 / (1.0 + r["distance"])
                }
                for r in results
            ],
            "confidence": min(1.0, len(results) / top_k) if results else 0.0
        }
    
    def get_context(self, plan_type: str, user_input: str) -> Dict[str, Any]:
        """RAG 컨텍스트 생성"""
        results = self.retrieve(user_input)
        
        return {
            "rag_suggestions": results.get("suggestions", []),
            "confidence": results.get("confidence", 0.0)
        }

