# API 설계 (API Design)

## 1. 개요

NOVA AI의 모든 컴포넌트는 **비동기 기반 이벤트 드리블 아키텍처**를 사용합니다.

- **내부 API**: Python async/await 기반
- **Tool API**: 통일된 인터페이스
- **외부 API**: REST API (미래 확장)

## 2. Core Agent API

### 2.1 Coordinator Agent API

#### 초기화

```python
class CoordinatorAgent:
    async def initialize(self) -> bool:
        """
        에이전트 초기화
        
        Returns:
            bool: 초기화 성공 여부
        """
        
    async def shutdown(self) -> None:
        """
        에이전트 종료
        """
        
    async def run(self) -> None:
        """
        메인 이벤트 루프 실행
        """
```

#### 작업 실행

```python
class CoordinatorAgent:
    async def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        사용자 입력 처리
        
        Args:
            user_input: 사용자 입력 텍스트
            
        Returns:
            {
                "status": "success" | "failed",
                "response": str,
                "tasks_executed": List[str],
                "duration": float
            }
        """
        
    async def handle_error(self, error: Exception) -> None:
        """
        오류 처리
        
        Args:
            error: 발생한 예외
        """
```

### 2.2 Planner Agent API

```python
class PlannerAgent:
    async def plan_tasks(
        self,
        intent: str,
        parameters: Dict[str, Any]
    ) -> List[Task]:
        """
        작업 계획 생성
        
        Args:
            intent: 분석된 의도
            parameters: 파라미터
            
        Returns:
            [
                {
                    "id": "task_001",
                    "name": "프로그램 실행",
                    "tool": "system",
                    "action": "launch_program",
                    "params": {"program": "VS Code"},
                    "priority": 1,
                    "dependencies": []
                },
                ...
            ]
        """
```

### 2.3 Memory Agent API

```python
class MemoryAgent:
    async def store_memory(
        self,
        key: str,
        value: Any,
        category: str = "general",
        importance: int = 5
    ) -> bool:
        """
        메모리 저장
        """
        
    async def recall_memory(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        메모리 조회
        
        Args:
            query: 검색 쿼리
            top_k: 상위 결과 개수
            
        Returns:
            [
                {
                    "key": "favorite_program",
                    "value": "VS Code",
                    "similarity": 0.95
                },
                ...
            ]
        """
        
    async def update_memory(self, key: str, value: Any) -> bool:
        """
        메모리 업데이트
        """
```

### 2.4 Tool Agent API

```python
class ToolAgent:
    async def execute_tool(
        self,
        tool_name: str,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        도구 실행
        
        Args:
            tool_name: 도구 이름
            action: 실행할 액션
            **kwargs: 액션 파라미터
            
        Returns:
            {
                "success": True | False,
                "result": Any,
                "error": str | None,
                "duration": float
            }
        """
```

## 3. Tool API 명세

### 3.1 BaseTool 인터페이스

```python
class BaseTool(ABC):
    """
    모든 Tool의 기본 인터페이스
    """
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Tool 실행
        
        Args:
            **kwargs: Tool별 파라미터
            
        Returns:
            {
                "success": bool,
                "result": Any,
                "error": str | None
            }
        """
        
    @abstractmethod
    def validate_parameters(self, **kwargs) -> bool:
        """
        파라미터 검증
        """
```

### 3.2 Browser Tool API

```python
class BrowserTool(BaseTool):
    async def execute(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        지원 액션:
        - navigate: 웹 페이지 이동
        - click: 요소 클릭
        - type: 텍스트 입력
        - search: 검색
        - screenshot: 스크린샷
        - extract_text: 텍스트 추출
        
        Example:
            result = await browser_tool.execute(
                action="navigate",
                url="https://www.google.com"
            )
        """
```

### 3.3 File Tool API

```python
class FileTool(BaseTool):
    async def execute(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        지원 액션:
        - create: 파일 생성
        - delete: 파일 삭제 (권한 필요)
        - copy: 파일 복사
        - move: 파일 이동
        - list: 디렉토리 목록
        - search: 파일 검색
        
        Example:
            result = await file_tool.execute(
                action="search",
                query="*.pdf",
                path="C:/Downloads"
            )
        """
```

### 3.4 System Tool API

```python
class SystemTool(BaseTool):
    async def execute(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        지원 액션:
        - launch_program: 프로그램 실행
        - close_program: 프로그램 종료
        - list_programs: 실행 중인 프로그램 목록
        - get_process_info: 프로세스 정보
        - kill_process: 프로세스 종료 (권한 필요)
        
        Example:
            result = await system_tool.execute(
                action="launch_program",
                program_name="notepad"
            )
        """
```

### 3.5 Vision Tool API

```python
class VisionTool(BaseTool):
    async def execute(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        지원 액션:
        - screenshot: 스크린샷 캡처
        - ocr: OCR 텍스트 추출
        - detect_ui_elements: UI 요소 감지
        - analyze_screen: 화면 분석
        - find_button: 버튼 찾기
        - read_text: 모든 텍스트 읽기
        
        Example:
            result = await vision_tool.execute(
                action="find_button",
                button_name="확인"
            )
        """
```

### 3.6 Voice Tool API

```python
class VoiceTool(BaseTool):
    async def execute(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        지원 액션:
        - recognize_speech: 음성 인식
        - synthesize_speech: 텍스트 음성 변환
        - detect_wake_word: 호출어 감지
        - record_audio: 음성 녹음
        - play_audio: 음성 재생
        
        Example:
            result = await voice_tool.execute(
                action="synthesize_speech",
                text="안녕하세요",
                speed=1.0
            )
        """
```

### 3.7 Network Tool API

```python
class NetworkTool(BaseTool):
    async def execute(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        지원 액션:
        - http_get: GET 요청
        - http_post: POST 요청
        - download_file: 파일 다운로드
        - check_connection: 연결 확인
        
        Example:
            result = await network_tool.execute(
                action="http_get",
                url="https://api.example.com/data"
            )
        """
```

## 4. LLM API

### 4.1 LLM Manager API

```python
class LLMManager:
    async def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        model: str = "openai"
    ) -> str:
        """
        LLM 응답 생성
        
        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            temperature: 응답 다양성 (0-1)
            model: 사용할 모델 ('openai', 'claude', 'gemini')
            
        Returns:
            str: 생성된 응답
        """
        
    async def analyze_intent(
        self,
        user_input: str
    ) -> Dict[str, Any]:
        """
        사용자 의도 분석
        
        Returns:
            {
                "intent": "program_launch",
                "action": "launch_program",
                "parameters": {"program_name": "VS Code"},
                "confidence": 0.95,
                "requires_confirmation": False
            }
        """
        
    async def plan_tasks(
        self,
        user_request: str
    ) -> List[Dict[str, Any]]:
        """
        작업 계획 생성
        
        Returns:
            [
                {
                    "step": 1,
                    "task": "Steam 실행",
                    "tool": "system",
                    "parameters": {"program": "Steam"},
                    "dependencies": []
                },
                ...
            ]
        """
```

## 5. 보안 API

### 5.1 Voice Authenticator API

```python
class VoiceAuthenticator:
    async def register_user(self, username: str) -> bool:
        """
        사용자 음성 등록
        
        음성 샘플 수집:
        - 한국어 문장 (1분)
        - 영어 문장 (1분)
        - 자유로운 대화 (1분)
        """
        
    async def verify_speaker(self) -> Tuple[bool, Optional[str]]:
        """
        현재 사용자 음성 인증
        
        Returns:
            (인증 성공 여부, 사용자명)
        """
        
    async def authenticate(
        self,
        security_level: SecurityLevel
    ) -> bool:
        """
        보안 레벨에 따른 인증
        
        Level 1: 인증 불필요
        Level 2: 음성 인증
        Level 3: 음성 인증 + 사용자 승인
        Level 4: 음성 인증 + 비밀번호
        """
```

## 6. 이벤트 시스템

### 6.1 이벤트 타입

```python
class EventType(Enum):
    # 음성 이벤트
    WAKE_WORD_DETECTED = "wake_word_detected"
    SPEECH_RECOGNIZED = "speech_recognized"
    SPEECH_SYNTHESIS_COMPLETE = "speech_synthesis_complete"
    
    # 작업 이벤트
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    
    # 인증 이벤트
    AUTHENTICATION_SUCCESS = "authentication_success"
    AUTHENTICATION_FAILED = "authentication_failed"
    
    # 시스템 이벤트
    ERROR_OCCURRED = "error_occurred"
    SYSTEM_SHUTDOWN = "system_shutdown"
```

### 6.2 이벤트 발행

```python
class EventBus:
    async def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any]
    ) -> None:
        """
        이벤트 발행
        
        Example:
            await event_bus.emit(
                EventType.TASK_COMPLETED,
                {"task_id": "task_001", "status": "success"}
            )
        """
        
    async def subscribe(
        self,
        event_type: EventType,
        handler: Callable
    ) -> None:
        """
        이벤트 구독
        
        Example:
            async def on_task_completed(data):
                print(f"Task completed: {data}")
                
            await event_bus.subscribe(
                EventType.TASK_COMPLETED,
                on_task_completed
            )
        """
```

## 7. 에러 응답 형식

### 7.1 표준 에러 응답

```python
{
    "success": False,
    "error": {
        "code": "AUTHENTICATION_FAILED",
        "message": "음성 인증 실패",
        "details": {
            "expected_confidence": 0.85,
            "actual_confidence": 0.72
        }
    },
    "timestamp": "2026-06-11T10:00:00Z"
}
```

### 7.2 에러 코드

```
AUTHENTICATION_FAILED - 인증 실패
AUTHORIZATION_DENIED - 권한 거부
TOOL_NOT_FOUND - 도구를 찾을 수 없음
INVALID_PARAMETERS - 잘못된 파라미터
TOOL_EXECUTION_FAILED - 도구 실행 실패
NETWORK_ERROR - 네트워크 오류
TIMEOUT - 타임아웃
INTERNAL_ERROR - 내부 오류
```

## 8. 레이트 리미팅

```python
RateLimiter:
    - API 호출: 1000/분
    - 음성 인식: 10/분
    - LLM 호출: 100/분
```

## 9. 캐싱 전략

```python
Cache:
    - LLM 응답: 1시간
    - 메모리 검색: 5분
    - 도구 결과: 30분
    - 음성 특징: 무제한
```
