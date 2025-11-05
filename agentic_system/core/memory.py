"""
Memory Management Component
메모리 관리 컴포넌트 (단기/장기 메모리)
PoC 단계에서는 단기 메모리(Session-based)만 사용
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque


class Memory:
    """메모리 기본 클래스"""
    
    def __init__(self):
        self.storage: Dict[str, Any] = {}
    
    def store(self, key: str, value: Any):
        """값 저장"""
        self.storage[key] = value
    
    def retrieve(self, key: str) -> Optional[Any]:
        """값 조회"""
        return self.storage.get(key)
    
    def clear(self):
        """모든 값 삭제"""
        self.storage.clear()


class ShortTermMemory(Memory):
    """
    단기 메모리 (Session-based)
    
    PoC 단계에서 사용하는 메모리로, 현재 세션의 컨텍스트만 유지
    """
    
    def __init__(self, session_id: str, max_size: int = 10):
        super().__init__()
        self.session_id = session_id
        self.max_size = max_size
        self.conversation_history: deque = deque(maxlen=max_size)
        self.context: Dict[str, Any] = {}
    
    def add_conversation(
        self, 
        user_input: str, 
        agent_response: str, 
        metadata: Optional[Dict] = None
    ):
        """대화 기록 추가"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "agent_response": agent_response,
            "metadata": metadata or {}
        }
        self.conversation_history.append(conversation)
    
    def get_conversation_history(self) -> List[Dict]:
        """대화 기록 조회"""
        return list(self.conversation_history)
    
    def update_context(self, key: str, value: Any):
        """컨пас 업데이트"""
        self.context[key] = value
    
    def get_context(self, key: Optional[str] = None) -> Any:
        """컨텍스트 조회"""
        if key:
            return self.context.get(key)
        return self.context
    
    def clear_context(self):
        """컨텍스트 초기화"""
        self.context.clear()


class LongTermMemory(Memory):
    """
    장기 메모리
    
    Pilot 단계에서 구현 예정
    사용자의 과거 대화 및 선호도 기억
    """
    
    def __init__(self, user_id: str):
        super().__init__()
        self.user_id = user_id
        self.preferences: Dict[str, Any] = {}
        self.history: List[Dict] = []
    
    def save_preference(self, key: str, value: Any):
        """선호도 저장"""
        self.preferences[key] = value
    
    def get_preference(self, key: str) -> Optional[Any]:
        """선호도 조회"""
        return self.preferences.get(key)
    
    def add_to_history(self, event: Dict):
        """히스토리에 이벤트 추가"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            **event
        })
    
    # Pilot 단계에서 구현 예정
    pass


class MemoryManager:
    """메모리 관리자"""
    
    def __init__(self):
        self.short_term_memories: Dict[str, ShortTermMemory] = {}
        self.long_term_memories: Dict[str, LongTermMemory] = {}
    
    def get_short_term_memory(self, session_id: str) -> ShortTermMemory:
        """단기 메모리 조회 또는 생성"""
        if session_id not in self.short_term_memories:
            self.short_term_memories[session_id] = ShortTermMemory(session_id)
        return self.short_term_memories[session_id]
    
    def get_long_term_memory(self, user_id: str) -> LongTermMemory:
        """장기 메모리 조회 또는 생성"""
        if user_id not in self.long_term_memories:
            self.long_term_memories[user_id] = LongTermMemory(user_id)
        return self.long_term_memories[user_id]
    
    def clear_session(self, session_id: str):
        """세션 메모리 삭제"""
        if session_id in self.short_term_memories:
            del self.short_term_memories[session_id]

