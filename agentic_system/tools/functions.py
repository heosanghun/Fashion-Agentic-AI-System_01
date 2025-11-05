"""
Functions Tool - 상품 검색 및 매칭 도구

PoC 단계에서는 Mock 구현
"""

from typing import Dict, Any, List, Optional


class ProductSearchFunction:
    """
    Function Tool - 상품 검색 및 매칭
    
    PoC 단계에서는 Mock 데이터 사용
    """
    
    def __init__(self):
        self.name = "function_product_search"
        self.mock_database = self._init_mock_database()
    
    def _init_mock_database(self) -> List[Dict[str, Any]]:
        """Mock 데이터베이스 초기화"""
        return [
            {
                "id": "prod_001",
                "name": "오버사이즈 후드티",
                "category": "상의",
                "style": "스트리트",
                "color": "검정색",
                "price": 89000,
                "brand": "StreetWear",
                "available": True
            },
            {
                "id": "prod_002",
                "name": "슬림핏 후드티",
                "category": "상의",
                "style": "캐주얼",
                "color": "회색",
                "price": 69000,
                "brand": "CasualWear",
                "available": True
            },
            {
                "id": "prod_003",
                "name": "데님 재킷",
                "category": "아우터",
                "style": "캐주얼",
                "color": "청색",
                "price": 129000,
                "brand": "DenimCo",
                "available": True
            }
        ]
    
    def execute(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        도구 실행
        
        Args:
            action: 실행할 액션 (search_products, match_recommendations)
            parameters: 액션에 필요한 파라미터
            context: 실행 컨텍스트
            
        Returns:
            Dict: 실행 결과
        """
        print(f"[ProductSearchFunction] execute 호출: action={action}")
        
        try:
            if action == "search_products":
                print("[ProductSearchFunction] search_products 시작...")
                result = self._search_products(parameters, context)
                print(f"[ProductSearchFunction] search_products 완료: status={result.get('status')}")
                return result
            elif action == "match_recommendations":
                print("[ProductSearchFunction] match_recommendations 시작...")
                result = self._match_recommendations(parameters, context)
                print(f"[ProductSearchFunction] match_recommendations 완료: status={result.get('status')}")
                return result
            else:
                raise ValueError(f"Unknown action: {action}")
        except Exception as e:
            print(f"[ProductSearchFunction] execute 오류: action={action}, error={str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _search_products(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        상품 검색
        
        쿼리와 필터를 기반으로 상품 검색
        """
        print(f"[ProductSearchFunction._search_products] 시작: parameters={list(parameters.keys())}")
        query = parameters.get("query", "").lower()
        filters = parameters.get("filters", {})
        print(f"[ProductSearchFunction._search_products] query={query}, filters={filters}")
        
        # 간단한 키워드 매칭
        results = []
        for product in self.mock_database:
            match = False
            
            # 쿼리 매칭
            if query:
                if (query in product["name"].lower() or 
                    query in product["category"].lower() or
                    query in product["style"].lower()):
                    match = True
            else:
                match = True
            
            # 필터 적용
            if filters:
                for key, value in filters.items():
                    if key in product and product[key] != value:
                        match = False
                        break
            
            if match and product["available"]:
                results.append(product)
        
        return {
            "status": "success",
            "products": results,
            "count": len(results),
            "query": query,
            "message": f"{len(results)}개의 상품을 찾았습니다."
        }
    
    def _match_recommendations(
        self, 
        parameters: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        추천 매칭
        
        이전 검색 결과를 기반으로 추천
        """
        # 이전 단계 결과 사용
        search_result = parameters.get("_dependency_result") or context.get("step_1")
        
        if not search_result:
            raise ValueError("상품 검색 결과가 필요합니다.")
        
        products = search_result.get("products", [])
        
        # 간단한 추천 알고리즘 (가격순 정렬)
        recommended = sorted(products, key=lambda x: x["price"])[:3]
        
        return {
            "status": "success",
            "recommendations": recommended,
            "count": len(recommended),
            "message": f"{len(recommended)}개의 추천 상품이 준비되었습니다."
        }


# 도구 함수로 사용하기 위한 래퍼
def product_search_function_tool(action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """도구 함수 래퍼"""
    tool = ProductSearchFunction()
    return tool.execute(action, parameters, context)

