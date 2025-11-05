"""
RAG (Retrieval-Augmented Generation) Store

PoC 단계에서는 Mock RAG 구현
Pilot 단계에서 실제 Vector DB 기반 RAG로 확장 예정
"""

from typing import Dict, List, Optional, Any
import json


class MockRAG:
    """
    Mock RAG Store
    
    PoC 단계에서 사용하는 단순한 규칙/데이터 기반 RAG
    실제 RAG 파이프라인 대신 JSON 데이터 사용
    """
    
    def __init__(self):
        self.knowledge_base = self._init_knowledge_base()
        self.name = "MockRAG"
    
    def _init_knowledge_base(self) -> Dict[str, Any]:
        """Mock 지식 베이스 초기화"""
        return {
            "garment_types": {
                "상의": ["후드티", "티셔츠", "셔츠", "블라우스"],
                "하의": ["바지", "청바지", "스커트", "반바지"],
                "아우터": ["재킷", "코트", "패딩", "바람막이"]
            },
            "styles": {
                "스트리트": "오버사이즈, 힙합, 그래피티 스타일",
                "캐주얼": "편안한 일상 복장, 데일리 룩",
                "포멀": "정장, 비즈니스 캐주얼",
                "스포츠": "운동복, 활동적인 스타일"
            },
            "materials": {
                "면": "통기성 좋음, 세탁 쉬움",
                "폴리에스터": "구김 적음, 빠른 건조",
                "데님": "내구성 좋음, 캐주얼 스타일"
            },
            "color_guidelines": {
                "검정색": "모든 스타일과 어울림, 슬림하게 보임",
                "흰색": "깔끔한 느낌, 여름에 적합",
                "회색": "중성적, 다양한 색상과 매칭 가능"
            }
        }
    
    def retrieve(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        지식 검색
        
        Args:
            query: 검색 쿼리
            context: 추가 컨텍스트
            
        Returns:
            Dict: 검색된 지식 정보
        """
        query_lower = query.lower()
        results = {
            "suggestions": [],
            "relevant_info": {},
            "confidence": 0.0
        }
        
        # 간단한 키워드 매칭
        for category, data in self.knowledge_base.items():
            if isinstance(data, dict):
                for key, value in data.items():
                    if query_lower in key.lower() or query_lower in str(value).lower():
                        results["suggestions"].append({
                            "category": category,
                            "key": key,
                            "value": value
                        })
                        results["relevant_info"][category] = data
        
        # 신뢰도 계산
        if results["suggestions"]:
            results["confidence"] = min(1.0, len(results["suggestions"]) / 5.0)
        
        return results
    
    def get_rag_context(self, plan_type: str, user_input: str) -> Dict[str, Any]:
        """
        RAG 컨텍스트 생성
        
        Agent 2에게 전달할 RAG 컨텍스트 생성
        """
        if plan_type == "3d_generation":
            # 3D 생성에 필요한 정보
            results = self.retrieve(user_input)
            return {
                "rag_suggestions": results.get("suggestions", []),
                "garment_info": results.get("relevant_info", {}),
                "confidence": results.get("confidence", 0.0)
            }
        elif plan_type == "garment_recommendation":
            # 추천에 필요한 정보
            results = self.retrieve(user_input)
            return {
                "rag_suggestions": results.get("suggestions", []),
                "style_info": results.get("relevant_info", {}).get("styles", {}),
                "confidence": results.get("confidence", 0.0)
            }
        else:
            return {
                "rag_suggestions": [],
                "confidence": 0.0
            }


class RAGStore:
    """
    RAG Store (향후 확장용)
    
    Pilot 단계에서 Vector DB 기반 RAG로 확장
    """
    
    def __init__(self, vector_db_type: str = "chroma"):
        self.vector_db_type = vector_db_type
        self.rag = MockRAG()  # PoC 단계에서는 Mock 사용
    
    def retrieve(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """지식 검색"""
        return self.rag.retrieve(query)
    
    def get_context(self, plan_type: str, user_input: str) -> Dict[str, Any]:
        """RAG 컨텍스트 생성"""
        return self.rag.get_rag_context(plan_type, user_input)

