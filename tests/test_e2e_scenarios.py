"""End-to-End scenario tests"""

import pytest
import asyncio
from src.core.coordinator import Coordinator
from src.core.event_bus import EventBus

class TestE2EScenarios:
    """End-to-End integration scenario tests"""
    
    @pytest.fixture
    async def coordinator(self):
        """Setup coordinator for E2E tests"""
        coordinator = Coordinator()
        await coordinator.initialize()
        yield coordinator
        await coordinator.shutdown()
    
    @pytest.mark.asyncio
    async def test_scenario_program_launch(self, coordinator):
        """
        시나리오: 사용자가 프로그램을 실행해달라고 요청
        
        흐름:
        1. 음성 입력: "VS Code 실행해줘"
        2. STT: "VS Code 실행해줘" (텍스트)
        3. 의도 분석: "program_launch"
        4. 작업 계획: System Tool로 VS Code 실행
        5. 실행: VS Code 프로세스 시작
        6. 검증: 프로세스 확인
        7. 응답: "VS Code를 실행했습니다"
        """
        result = await coordinator.execute_user_request(
            user_input="VS Code 실행해줘",
            input_type="voice"
        )
        
        assert result["success"] is True
        assert "VS Code" in result["response"] or "실행" in result["response"]
        assert result["tasks_executed"] > 0
    
    @pytest.mark.asyncio
    async def test_scenario_file_search(self, coordinator):
        """
        시나리오: 파일 검색
        
        흐름:
        1. 음성 입력: "다운로드 폴더에서 PDF 파일 찾아줘"
        2. STT: 음성을 텍스트로 변환
        3. 의도 분석: "file_search"
        4. 메모리 조회: "다운로드 폴더" 기본 경로 확인
        5. 작업 계획: File Tool로 검색
        6. 실행: *.pdf 파일 검색
        7. 검증: 검색 결과 확인
        8. 응답: "3개의 PDF 파일을 찾았습니다"
        """
        result = await coordinator.execute_user_request(
            user_input="다운로드 폴더에서 PDF 파일 찾아줘",
            input_type="voice"
        )
        
        assert result["success"] is True
        assert "PDF" in result["response"] or "파일" in result["response"]
    
    @pytest.mark.asyncio
    async def test_scenario_web_automation(self, coordinator):
        """
        시나리오: 웹 자동화
        
        흐름:
        1. 음성 입력: "Google에서 배틀필드 최적화 검색해줘"
        2. STT: 음성을 텍스트로 변환
        3. 의도 분석: "web_search"
        4. 작업 계획:
           - Browser Tool로 Google 이동
           - 검색어 입력
           - 검색 실행
        5. 실행: 브라우저 자동화
        6. 검증: 검색 결과 페이지 로드 확인
        7. 응답: "검색을 완료했습니다"
        """
        result = await coordinator.execute_user_request(
            user_input="Google에서 배틀필드 검색해줘",
            input_type="voice"
        )
        
        assert result["success"] is True
        assert result["tasks_executed"] >= 2
    
    @pytest.mark.asyncio
    async def test_scenario_multi_step_task(self, coordinator):
        """
        시나리오: 복잡한 다단계 작업
        
        흐름:
        1. 요청: "Chrome 실행하고 YouTube 접속한 다음 스크린샷 찍어줘"
        2. 작업 분해:
           - Task 1: Chrome 실행 (System Tool)
           - Task 2: YouTube 접속 (Browser Tool, Task 1 의존)
           - Task 3: 스크린샷 (Vision Tool, Task 2 의존)
        3. 의존성 분석 후 순차 실행
        4. 각 단계마다 검증
        5. 최종 응답
        """
        result = await coordinator.execute_user_request(
            user_input="Chrome 실행하고 YouTube 접속한 다음 스크린샷 찍어줘",
            input_type="voice"
        )
        
        assert result["success"] is True
        # Should have executed multiple tasks
        assert result["tasks_executed"] >= 2
    
    @pytest.mark.asyncio
    async def test_scenario_with_memory(self, coordinator):
        """
        시나리오: 메모리를 활용한 개인화된 작업
        
        흐름:
        1. 첫 번째 요청: "좋아하는 프로그램 저장: VS Code"
           - Memory Agent에 저장
        
        2. 두 번째 요청: "내가 좋아하는 프로그램 실행해줘"
           - Memory Agent에서 검색
           - "VS Code" 찾음
           - System Tool로 실행
        
        3. 응답: "VS Code를 실행했습니다"
        """
        # Store preference
        store_result = await coordinator.execute_user_request(
            user_input="좋아하는 프로그램 저장: VS Code",
            input_type="voice"
        )
        assert store_result["success"] is True
        
        # Retrieve and use preference
        retrieve_result = await coordinator.execute_user_request(
            user_input="내가 좋아하는 프로그램 실행해줘",
            input_type="voice"
        )
        assert retrieve_result["success"] is True
        assert "VS Code" in retrieve_result["response"] or "실행" in retrieve_result["response"]
    
    @pytest.mark.asyncio
    async def test_scenario_error_recovery(self, coordinator):
        """
        시나리오: 오류 복구
        
        흐름:
        1. 요청: "존재하지 않는 프로그램 실행해줘"
        2. System Tool 실패
        3. Verifier Agent 감지
        4. 자동 재시도 (최대 3회)
        5. 사용자에게 오류 알림
        """
        result = await coordinator.execute_user_request(
            user_input="존재하지_않는_프로그램_12345 실행해줘",
            input_type="voice"
        )
        
        assert result["success"] is False
        assert "error" in result or "실패" in result["response"]
    
    @pytest.mark.asyncio
    async def test_scenario_with_confirmation(self, coordinator):
        """
        시나리오: 위험한 작업의 확인 절차
        
        흐름:
        1. 요청: "Downloads 폴더 전체 삭제해줘" (Security Level 3)
        2. Security Check: 사용자 확인 필요
        3. 음성 확인: "네, 진행해줘" 또는 "취소해줘"
        4. 확인 후 실행 또는 취소
        """
        # This test requires user interaction, so we'll mock it
        result = await coordinator.execute_user_request(
            user_input="Downloads 폴더 비우기",
            input_type="voice",
            security_level=2  # Requires confirmation
        )
        
        # Should ask for confirmation
        assert "confirmation" in result or "확인" in str(result)

class TestPerformance:
    """Performance tests for E2E scenarios"""
    
    @pytest.mark.asyncio
    async def test_response_time(self, coordinator):
        """
        성능 테스트: 응답 시간
        
        목표:
        - 호출어 감지: < 100ms
        - 음성 인식: < 2s
        - 의도 분석: < 500ms
        - 작업 계획: < 1s
        - 작업 실행: 가변
        - 검증: < 500ms
        - 음성 응답: < 1s
        
        총 응답 시간: < 6s
        """
        import time
        start_time = time.time()
        
        result = await coordinator.execute_user_request(
            user_input="VS Code 실행해줘",
            input_type="text"  # Use text to avoid STT delay
        )
        
        elapsed_time = time.time() - start_time
        
        assert result["success"] is True
        assert elapsed_time < 6.0  # Total response time should be < 6 seconds
        assert "duration" in result

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
