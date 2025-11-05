"""
Agent Runtime Component - Agent 1
종합 감독 에이전트 (Agent 1)

역할:
- 사용자 요청을 분석하여 큰 그림의 작업 계획 수립
- Agent 2에게 계획 전달 및 결과 수신
- 도구 실행 오케스트레이션
- 자기 수정 루프 관리
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import json

from .f_llm import FLLM, ExecutionPlan
from .memory import MemoryManager, ShortTermMemory
from pydantic import BaseModel


class AbstractPlan(BaseModel):
    """추상적 작업 계획"""
    plan_type: str  # "3d_generation" or "garment_recommendation"
    goal: str
    steps: List[str]  # 추상적 단계 설명
    parameters: Dict[str, Any]
    created_at: str


class AgentRuntime:
    """
    Agent Runtime - Agent 1 (종합 감독 에이전트)
    
    전체 프로세스를 오케스트레이션하는 핵심 엔진
    """
    
    def __init__(
        self,
        agent2: Optional[FLLM] = None,
        memory_manager: Optional[MemoryManager] = None,
        max_retries: int = 1
    ):
        self.agent2 = agent2 or FLLM()
        self.memory_manager = memory_manager or MemoryManager()
        self.max_retries = max_retries
        self.name = "Agent Runtime (Agent 1)"
        self.tools_registry: Dict[str, Callable] = {}
    
    def register_tool(self, tool_name: str, tool_function: Callable):
        """도구 등록"""
        self.tools_registry[tool_name] = tool_function
    
    def process_request(
        self,
        payload: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        사용자 요청 처리
        
        전체 프로세스:
        1. 인식 (Perception): 요청 분석
        2. 판단 (Judgment): 계획 수립
        3. 행동 (Action): 도구 실행
        """
        # 세션 메모리 가져오기
        session_id = session_id or payload.get("session_id", "default")
        memory = self.memory_manager.get_short_term_memory(session_id)
        
        # 1. 인식 (Perception): 요청 분석
        user_intent = self._analyze_user_intent(payload)
        
        # 2. 판단 (Judgment): 추상적 계획 수립 (Agent 1 역할)
        abstract_plan = self._create_abstract_plan(user_intent, payload, memory)
        
        # Agent 2에게 전달하여 구체적 실행 계획 생성
        input_data = payload.get("input_data", {})
        execution_plan = self.agent2.generate_execution_plan(
            abstract_plan.dict(),
            context=input_data,
            rag_context=None,  # PoC에서는 Mock RAG
            user_text=input_data.get("text"),
            image_path=input_data.get("image_path")
        )
        
        # 3. 행동 (Action): 실행 계획에 따라 도구 실행
        execution_result = self._execute_plan(execution_plan, memory)
        
        # 결과 검증 및 재시도 (자기 수정 루프)
        final_result = self._self_correction_loop(
            execution_plan,
            execution_result,
            memory
        )
        
        # 메모리에 대화 기록 저장
        memory.add_conversation(
            user_input=payload.get("input_data", {}).get("text", ""),
            agent_response=final_result.get("message", ""),
            metadata={"plan_id": execution_plan.plan_id}
        )
        
        return final_result
    
    def _analyze_user_intent(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 의도 분석
        
        간단한 규칙 기반 분석 (PoC 단계)
        실제 구현에서는 LLM 사용
        """
        input_data = payload.get("input_data", {})
        text = input_data.get("text", "").lower()
        has_image = input_data.get("has_image", False)
        
        # 의도 추론
        if "입혀줘" in text or "가상 피팅" in text or has_image:
            intent_type = "3d_generation"
        elif "추천" in text or "찾아줘" in text:
            intent_type = "garment_recommendation"
        else:
            intent_type = "3d_generation"  # 기본값
        
        return {
            "type": intent_type,
            "confidence": 0.9,
            "text": text,
            "has_image": has_image
        }
    
    def _create_abstract_plan(
        self,
        user_intent: Dict[str, Any],
        payload: Dict[str, Any],
        memory: ShortTermMemory
    ) -> AbstractPlan:
        """
        추상적 작업 계획 수립 (Agent 1의 핵심 역할)
        
        큰 그림의 작업 계획을 생성
        """
        intent_type = user_intent["type"]
        
        if intent_type == "3d_generation":
            return AbstractPlan(
                plan_type="3d_generation",
                goal="2D 이미지를 3D 가상 피팅으로 변환",
                steps=[
                    "의류 이미지 분석",
                    "3D 패턴 생성",
                    "3D 모델 변환",
                    "렌더링 및 시각화"
                ],
                parameters={
                    "image_path": payload.get("input_data", {}).get("image_path"),
                    "text": payload.get("input_data", {}).get("text")
                },
                created_at=datetime.now().isoformat()
            )
        else:  # garment_recommendation
            return AbstractPlan(
                plan_type="garment_recommendation",
                goal="사용자 요청에 맞는 의상 추천",
                steps=[
                    "상품 검색",
                    "매칭 및 필터링",
                    "추천 결과 반환"
                ],
                parameters={
                    "query": payload.get("input_data", {}).get("text"),
                    "filters": {}
                },
                created_at=datetime.now().isoformat()
            )
    
    def _execute_plan(
        self,
        execution_plan: ExecutionPlan,
        memory: ShortTermMemory
    ) -> Dict[str, Any]:
        """
        실행 계획에 따라 도구 실행
        
        순차적으로 각 단계를 실행하고 결과를 수집
        """
        results = {}
        execution_context = {}
        
        # 단계별 실행 (의존성 고려)
        print(f"[AgentRuntime._execute_plan] 총 {len(execution_plan.steps)}개 단계 실행 시작")
        for step_idx, step in enumerate(execution_plan.steps, 1):
            step_id = step["step_id"]
            tool_name = step["tool"]
            action = step["action"]
            parameters = step.get("parameters", {})
            dependencies = step.get("dependencies", [])
            print(f"[AgentRuntime._execute_plan] 단계 {step_idx}/{len(execution_plan.steps)}: {tool_name}.{action} (step_id={step_id})")
            
            # 의존성 확인
            if dependencies:
                # 의존성 결과를 파라미터에 포함
                for dep_id in dependencies:
                    if dep_id in results:
                        # results[dep_id]는 {"status": "success", "result": {...}, "step_id": ...} 구조
                        # 실제 결과는 "result" 키에 있음
                        dep_result = results[dep_id]
                        if isinstance(dep_result, dict) and "result" in dep_result:
                            parameters["_dependency_result"] = dep_result["result"]
                        else:
                            parameters["_dependency_result"] = dep_result
            
            # 도구 실행
            if tool_name in self.tools_registry:
                try:
                    print(f"[AgentRuntime._execute_plan] 도구 실행 중: {tool_name}.{action}")
                    tool_func = self.tools_registry[tool_name]
                    step_result = tool_func(action, parameters, execution_context)
                    print(f"[AgentRuntime._execute_plan] 도구 실행 완료: {tool_name}.{action}")
                    results[step_id] = {
                        "status": "success",
                        "result": step_result,
                        "step_id": step_id
                    }
                    # 컨텍스트에 실제 결과 저장 (다음 단계에서 사용)
                    execution_context[f"step_{step_id}"] = step_result
                    execution_context[f"step_{step_id}_result"] = step_result
                except Exception as e:
                    print(f"[AgentRuntime._execute_plan] 도구 실행 오류: {tool_name}.{action} - {str(e)}")
                    import traceback
                    traceback.print_exc()
                    results[step_id] = {
                        "status": "error",
                        "error": str(e),
                        "step_id": step_id
                    }
            else:
                results[step_id] = {
                    "status": "error",
                    "error": f"Tool '{tool_name}' not found",
                    "step_id": step_id
                }
        
        # 최종 결과 반환
        final_result_id = max([s["step_id"] for s in execution_plan.steps])
        final_result = results.get(final_result_id, {})
        
        return {
            "status": "completed",
            "plan_id": execution_plan.plan_id,
            "steps": results,
            "final_result": final_result,
            "all_results": results
        }
    
    def _self_correction_loop(
        self,
        execution_plan: ExecutionPlan,
        execution_result: Dict[str, Any],
        memory: ShortTermMemory,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        자기 수정 루프 (Self-Correction Loop)
        
        결과를 평가하고, 실패 시 재시도
        PoC 단계에서는 단순 재시도만 수행
        """
        # 결과 평가
        evaluation = self._evaluate_result(execution_result)
        
        if evaluation["success"]:
            return {
                "status": "success",
                "message": "작업이 성공적으로 완료되었습니다.",
                "data": execution_result,
                "evaluation": evaluation
            }
        
        # 실패 시 재시도
        if retry_count < self.max_retries:
            # 계획 수정 (간단한 재시도)
            retry_result = self._execute_plan(execution_plan, memory)
            return self._self_correction_loop(
                execution_plan,
                retry_result,
                memory,
                retry_count + 1
            )
        else:
            return {
                "status": "failed",
                "message": "최대 재시도 횟수에 도달했습니다.",
                "data": execution_result,
                "evaluation": evaluation
            }
    
    def _evaluate_result(self, execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        결과 평가
        
        PoC 단계에서는 성공/실패만 판단
        """
        all_steps = execution_result.get("all_results", {})
        final_result = execution_result.get("final_result", {})
        
        # 실행 결과 자체의 상태 확인
        execution_status = execution_result.get("status", "unknown")
        
        # 모든 단계가 성공했는지 확인
        failed_steps = []
        for step_id, result in all_steps.items():
            if isinstance(result, dict):
                step_status = result.get("status", "unknown")
                if step_status not in ["success", "completed"]:
                    failed_steps.append(step_id)
            else:
                failed_steps.append(step_id)
        
        # 최종 결과도 확인
        if isinstance(final_result, dict):
            final_status = final_result.get("status", "unknown")
            if final_status not in ["success", "completed"]:
                # 최종 결과가 실패면 전체 실패
                success = False
            else:
                # 모든 단계가 성공이고 실행 상태도 완료면 성공
                success = len(failed_steps) == 0 and execution_status == "completed"
        else:
            # 최종 결과가 없거나 딕셔너리가 아니면 실패
            success = len(failed_steps) == 0 and execution_status == "completed"
        
        return {
            "success": success,
            "failed_steps": failed_steps,
            "total_steps": len(all_steps),
            "successful_steps": len(all_steps) - len(failed_steps),
            "execution_status": execution_status
        }



