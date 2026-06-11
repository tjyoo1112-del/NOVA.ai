# 에이전트 설계 (Agent Design)

## 1. 개요

NOVA AI는 **멀티 에이전트 시스템**으로 구성되어 있습니다.
Coordinator Agent가 중앙에서 모든 에이전트를 조율합니다.

## 2. 에이전트 아키텍처

```
┌─────────────────────────────────┐
│   Coordinator Agent (중앙)       │
│   - 이벤트 루프 관리             │
│   - 에이전트 조율                │
│   - 오류 처리                    │
└────────┬────────────────────────┘
         │
    ┌────┴────┬───────┬───────┬────────┐
    │          │       │       │        │
    ▼          ▼       ▼       ▼        ▼
┌──────┐  ┌────────┐ ┌────┐ ┌──────┐ ┌────────┐
│Memory│  │ Planner│ │Tool│ │Voice │ │Verifier│
│Agent │  │ Agent  │ │Agent│ │Agent │ │ Agent  │
└──────┘  └────────┘ └────┘ └──────┘ └────────┘
```

## 3. Coordinator Agent 상세

### 3.1 책임

```python
Coordinator 책임:
1. 사용자 입력 처리
   ├─ 음성 입력 수신
   ├─ 텍스트 입력 수신
   └─ 버튼 입력 수신
   
2. 인증 관리
   ├─ 음성 인증
   ├─ 권한 확인
   └─ 보안 레벨 검증
   
3. 다른 에이전트 조율
   ├─ Memory Agent 호출
   ├─ Planner Agent 호출
   ├─ Tool Agent 호출
   └─ Verifier Agent 호출
   
4. 상태 관리
   ├─ 전역 상태 유지
   ├─ 세션 관리
   └─ 이벤트 발행
```

### 3.2 메인 루프 흐름

```python
async def run():
    """
    Coordinator 메인 루프
    """
    while self.is_running:
        # 1단계: 사용자 입력 대기
        user_input = await self.wait_for_input()
        
        if not user_input:
            await asyncio.sleep(0.1)
            continue
        
        try:
            # 2단계: 인증
            authenticated = await self.voice_auth.verify_speaker()
            if not authenticated:
                await self.respond("인증 실패했습니다")
                continue
            
            # 3단계: 의도 분석
            intent = await self.llm_manager.analyze_intent(user_input)
            
            # 4단계: 메모리 조회
            context = await self.memory_agent.recall_memory(
                user_input,
                top_k=5
            )
            
            # 5단계: 작업 계획
            tasks = await self.planner_agent.plan_tasks(
                intent,
                context
            )
            
            # 6단계: 작업 실행
            results = await self.execute_tasks(tasks)
            
            # 7단계: 검증
            verified_results = await self.verifier_agent.verify_results(results)
            
            # 8단계: 응답 생성
            response = await self.generate_response(verified_results)
            await self.respond(response)
            
            # 9단계: 메모리 업데이트
            await self.memory_agent.update_conversation_history(
                user_input,
                response
            )
            
        except Exception as e:
            await self.handle_error(e)
```

### 3.3 상태 머신

```python
Coordinator 상태:

[IDLE]
  ↓ (Wake Word Detected)
[LISTENING]
  ↓ (Audio Captured)
[AUTHENTICATING]
  ↓ (Auth Success)
[PROCESSING]
  ├─ [ANALYZING_INTENT]
  ├─ [PLANNING_TASKS]
  ├─ [EXECUTING_TASKS]
  ├─ [VERIFYING_RESULTS]
  └─ [GENERATING_RESPONSE]
  ↓
[RESPONDING]
  ↓ (Response Delivered)
[IDLE]
```

## 4. Planner Agent 상세

### 4.1 책임

```python
Planner 책임:
1. 의도 분석 결과 수신
2. 작업 분해 (Task Decomposition)
   ├─ 복잡한 요청을 단순 작업으로 분해
   ├─ 각 작업에 필요한 Tool 결정
   └─ 작업 간 의존성 파악
3. 작업 순서 결정
   ├─ 의존성 기반 정렬
   ├─ 병렬 실행 가능 작업 식별
   └─ 우선순위 설정
4. 작업 계획 반환
```

### 4.2 작업 계획 구조

```python
@dataclass
class Task:
    id: str                      # 작업 ID
    name: str                    # 작업 이름
    description: str             # 작업 설명
    tool: str                    # 사용할 Tool
    action: str                  # Tool 액션
    parameters: Dict[str, Any]   # 파라미터
    priority: int                # 우선순위 (1-10)
    dependencies: List[str]      # 선행 작업
    security_level: int          # 보안 레벨
    estimated_time: float        # 예상 소요시간
    timeout: float               # 타임아웃
    retry_count: int             # 최대 재시도 횟수
```

### 4.3 LLM 기반 계획 생성

```python
async def plan_tasks(
    intent: str,
    parameters: Dict,
    context: List[Dict]
) -> List[Task]:
    """
    LLM을 사용한 작업 계획 생성
    """
    prompt = f"""
    사용자 의도: {intent}
    파라미터: {parameters}
    컨텍스트: {context}
    
    다음 작업을 계획하세요:
    1. 필요한 도구 식별
    2. 도구별 액션 결정
    3. 파라미터 설정
    4. 작업 간 의존성 분석
    5. 우선순위 설정
    
    JSON 형식으로 반환:
    [{"id": "task_001", "name": "...", ...}, ...]
    """
    
    # LLM으로부터 계획 수신
    plan_json = await self.llm_manager.generate_response(prompt)
    
    # JSON 파싱 및 Task 객체 생성
    tasks = self.parse_plan(plan_json)
    
    # 의존성 검증
    self.validate_dependencies(tasks)
    
    # 보안 레벨 자동 설정
    self.assign_security_levels(tasks)
    
    return tasks
```

## 5. Memory Agent 상세

### 5.1 메모리 계층

```python
Memory 계층 구조:

1. Immediate Memory (즉각적 메모리)
   ├─ 현재 대화 내용
   ├─ 현재 작업 상태
   └─ TTL: ~5분
   
2. Short-term Memory (단기 메모리)
   ├─ 최근 세션 정보
   ├─ 최근 작업 결과
   └─ TTL: ~1시간
   
3. Long-term Memory (장기 메모리)
   ├─ 사용자 선호도
   ├─ 사용자 습관
   ├─ 프로젝트 정보
   └─ 영구 저장 (또는 Vector DB)
```

### 5.2 의미 검색 (Semantic Search)

```python
async def recall_memory(
    query: str,
    top_k: int = 5,
    similarity_threshold: float = 0.5
) -> List[Dict[str, Any]]:
    """
    의미론적 메모리 검색
    
    Process:
    1. 쿼리를 벡터로 변환
    2. ChromaDB에서 유사 메모리 검색
    3. 신뢰도 필터링
    4. 결과 정렬 및 반환
    """
    # 쿼리 임베딩
    query_embedding = await self.embeddings.embed(query)
    
    # ChromaDB 검색
    results = self.chroma_db.query(
        embeddings=[query_embedding],
        n_results=top_k
    )
    
    # 유사도 필터링
    filtered = [
        r for r in results
        if r['distance'] >= similarity_threshold
    ]
    
    return filtered
```

### 5.3 메모리 학습

```python
메모리 학습 과정:

1. 작업 완료 후
   ├─ 결과 분석
   ├─ 사용자 피드백 수집
   └─ 성공/실패 기록
   
2. 패턴 인식
   ├─ 자주 사용되는 프로그램
   ├─ 반복되는 작업
   └─ 선호하는 방식
   
3. 메모리 업데이트
   ├─ 새로운 정보 저장
   ├─ 기존 정보 업데이트
   └─ 관련성 점수 조정
   
4. 메모리 최적화
   ├─ 오래된 정보 정리
   ├─ 중복 제거
   └─ 신뢰도 검증
```

## 6. Tool Agent 상세

### 6.1 책임

```python
Tool Agent 책임:
1. Tool 등록/관리
   ├─ 사용 가능한 Tool 목록 유지
   ├─ Tool 메타정보 관리
   └─ Tool 상태 모니터링
   
2. Tool 실행 조율
   ├─ 올바른 Tool 선택
   ├─ 파라미터 검증
   └─ 실행 권한 확인
   
3. 에러 처리
   ├─ Tool 오류 포착
   ├─ 자동 재시도
   └─ 대체 Tool 제안
   
4. 결과 반환
   ├─ Tool 결과 수집
   ├─ 형식 정규화
   └─ 메타정보 추가
```

### 6.2 Tool 라우팅

```python
async def execute_tool(
    tool_name: str,
    action: str,
    parameters: Dict[str, Any],
    security_level: int
) -> Dict[str, Any]:
    """
    Tool 실행 라우팅
    """
    # 1. Tool 검증
    if tool_name not in self.tools:
        raise ToolNotFoundError(f"Tool {tool_name} not found")
    
    # 2. 권한 확인
    required_level = self.get_security_level(tool_name, action)
    if security_level < required_level:
        raise AuthorizationError("Insufficient security level")
    
    # 3. 파라미터 검증
    if not self.validate_parameters(tool_name, action, parameters):
        raise ParameterError("Invalid parameters")
    
    # 4. Tool 실행
    tool = self.tools[tool_name]
    result = await tool.run(action=action, **parameters)
    
    # 5. 결과 처리
    processed = self.process_result(result)
    
    return processed
```

## 7. Voice Agent 상세

### 7.1 음성 처리 파이프라인

```python
음성 처리 단계:

1. 음성 캡처 (Voice Capture)
   ├─ 마이크 입력
   ├─ 노이즈 제거
   └─ VAD (음성 활동 감지)
   
2. 음성 인식 (STT)
   ├─ Whisper 모델
   ├─ 한영 다중언어
   └─ 신뢰도 계산
   
3. 텍스트 정규화
   ├─ 띄어쓰기
   ├─ 특수문자 처리
   └─ 문맥 보정
   
4. 응답 생성
   ├─ LLM 응답 생성
   └─ 응답 검증
   
5. 음성 합성 (TTS)
   ├─ pyttsx3 또는 Coqui
   ├─ 음성 속도 조절
   └─ 자연스러운 발음
```

### 7.2 호출어 감지

```python
async def detect_wake_word() -> bool:
    """
    호출어 감지 루프
    
    호출어: "헤이 노바", "노바", "Hey Nova"
    """
    while True:
        # 음성 캡처
        audio = await self.capture_audio(duration=3)
        
        # STT
        text = await self.recognize_speech(audio)
        
        # 호출어 매칭
        if self.match_wake_word(text):
            return True
            
        await asyncio.sleep(0.5)
```

## 8. Verifier Agent 상세

### 8.1 책임

```python
Verifier 책임:
1. 작업 완료 확인
   ├─ 성공 여부 판단
   ├─ 결과 유효성 검증
   └─ 예상 결과와 비교
   
2. 오류 감지
   ├─ 예상 외의 동작 감지
   ├─ 부분 실패 감지
   └─ 부작용 감지
   
3. 재시도 결정
   ├─ 재시도 필요성 판단
   ├─ 재시도 방식 결정
   └─ 최대 재시도 횟수 확인
   
4. 사용자 피드백 요청
   ├─ 불확실한 결과 처리
   ├─ 사용자 승인 요청
   └─ 문제점 보고
```

### 8.2 검증 로직

```python
async def verify_task(
    task: Task,
    result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    작업 결과 검증
    """
    # 1. 성공 여부 확인
    if not result.get('success', False):
        return {
            "verified": False,
            "reason": "Task failed",
            "should_retry": True,
            "retry_count": 0
        }
    
    # 2. 결과 형식 검증
    if not self.validate_result_format(task, result):
        return {
            "verified": False,
            "reason": "Invalid result format",
            "should_retry": False
        }
    
    # 3. 예상 결과 비교
    if not self.matches_expectation(task, result):
        return {
            "verified": False,
            "reason": "Result doesn't match expectation",
            "should_retry": True,
            "retry_count": 0
        }
    
    # 4. 부작용 확인
    side_effects = await self.detect_side_effects(result)
    if side_effects:
        return {
            "verified": False,
            "reason": "Unintended side effects detected",
            "side_effects": side_effects,
            "should_retry": False
        }
    
    return {"verified": True}
```

## 9. 에이전트 간 통신 프로토콜

### 9.1 메시지 구조

```python
@dataclass
class Message:
    sender: str              # 발신 에이전트
    receiver: str            # 수신 에이전트
    message_type: str        # 요청, 응답, 이벤트
    payload: Dict[str, Any]  # 메시지 내용
    timestamp: str           # ISO 8601 형식
    message_id: str          # 메시지 추적 ID
    priority: int            # 우선순위 (1-10)
```

### 9.2 통신 흐름

```python
메시지 흐름:

1. 요청 (Request)
   Coordinator → Planner
   {
       "message_type": "request",
       "payload": {
           "action": "plan_tasks",
           "intent": "program_launch",
           "parameters": {...}
       }
   }
   
2. 응답 (Response)
   Planner → Coordinator
   {
       "message_type": "response",
       "payload": {
           "tasks": [...],
           "success": true
       }
   }
   
3. 이벤트 (Event)
   Coordinator → All
   {
       "message_type": "event",
       "payload": {
           "event_type": "task_completed",
           "data": {...}
       }
   }
```

## 10. 에이전트 협력 시나리오

### 10.1 프로그램 실행 시나리오

```
사용자: "배틀필드 실행해줘"

1. Coordinator
   └─ 음성 인증 ✓
   
2. Memory Agent
   └─ "배틀필드" 관련 메모리 조회
   └─ (Steam에서 실행해야 함)
   
3. LLM
   └─ 의도 분석: "프로그램 실행"
   
4. Planner Agent
   └─ 작업 계획:
      Task 1: Steam 실행 (System Tool)
      Task 2: 배틀필드 실행 (System Tool)
   
5. Tool Agent
   ├─ Task 1 실행: Steam 실행
   └─ Task 2 실행: 배틀필드 실행
   
6. Verifier Agent
   └─ Steam 및 배틀필드 프로세스 확인
   
7. Voice Agent
   └─ "배틀필드를 실행했습니다" (TTS)
   
8. Memory Agent
   └─ 작업 이력 저장
```

### 10.2 파일 검색 시나리오

```
사용자: "다운로드 폴더에서 PDF 파일 찾아줘"

1. Coordinator
   └─ 음성 인증 ✓
   
2. Memory Agent
   └─ "다운로드 폴더" 경로 조회
   
3. LLM
   └─ 의도 분석: "파일 검색"
   
4. Planner Agent
   └─ 작업 계획:
      Task 1: PDF 파일 검색 (File Tool)
   
5. Tool Agent
   └─ 파일 검색 실행
   └─ 결과: [file1.pdf, file2.pdf, ...]
   
6. Verifier Agent
   └─ 검색 결과 유효성 확인
   
7. Vision Agent
   └─ 파일 목록을 화면에 표시
   
8. Voice Agent
   └─ "3개의 PDF 파일을 찾았습니다" (TTS)
   
9. Memory Agent
   └─ 검색 이력 저장
```

## 11. 성능 최적화

### 11.1 병렬 처리

```python
병렬 처리 전략:

1. 독립적 작업 병렬화
   ├─ 의존성 없는 작업 동시 실행
   └─ asyncio.gather() 사용
   
2. 에이전트 캐싱
   ├─ LLM 응답 캐시
   ├─ 메모리 검색 결과 캐시
   └─ 자주 사용되는 계획 캐시
   
3. 리소스 풀 관리
   ├─ 브라우저 탭 풀
   ├─ 네트워크 연결 풀
   └─ 마이크 리소스 풀
```

### 11.2 응답 시간 최적화

```
응답 시간 목표:

- 호출어 감지: < 100ms
- 음성 인식: < 2s
- 의도 분석: < 500ms
- 작업 계획: < 1s
- 작업 실행: 가변
- 검증: < 500ms
- 음성 응답: < 1s

총 평균: < 6s
```
