# 시스템 아키텍처 (System Architecture)

## 1. 개요

NOVA AI는 **멀티 에이전트 기반의 마이크로서비스 아키텍처**를 채택합니다.
각 에이전트는 독립적으로 동작하며, Coordinator Agent가 중앙에서 조율합니다.

## 2. 전체 시스템 흐름

```
사용자 음성 입력
     ↓
[Wake Word Detection] - "헤이 노바" 감지
     ↓
[Speaker Verification] - 음성 인증
     ↓
[Speech Recognition] - Whisper로 음성→텍스트
     ↓
[Coordinator Agent] - 중앙 조율
     ├─→ [LLM] - 의도 분석
     ├─→ [Planner Agent] - 작업 계획
     ├─→ [Memory Agent] - 사용자 메모리 조회
     └─→ [Tool Agent] - 도구 실행
          ├─→ [Browser Tool] - 웹 자동화
          ├─→ [File Tool] - 파일 관리
          ├─→ [System Tool] - 시스템 제어
          ├─→ [Vision Tool] - 화면 분석
          ├─→ [Voice Tool] - 음성 I/O
          └─→ [Network Tool] - API 호출
     ↓
[Verifier Agent] - 결과 검증
     ↓
[Voice Response] - TTS로 응답
     ↓
사용자 음성 출력
```

## 3. 핵심 컴포넌트

### 3.1 Coordinator Agent
**역할**: 모든 작업의 중앙 조율자

```
Coordinator Agent
├─ 상태 관리
├─ 이벤트 루프 제어
├─ 다른 에이전트 조율
└─ 오류 처리 및 복구
```

### 3.2 Planner Agent
**역할**: 복잡한 명령을 단계별 작업으로 분해

```
Planner Agent
├─ 의도 분석 결과 수신
├─ 작업 분해 (Task Decomposition)
├─ 의존성 분석
├─ 우선순위 설정
└─ 실행 계획 생성
```

### 3.3 Memory Agent
**역할**: 사용자 메모리 및 컨텍스트 관리

```
Memory Agent
├─ 단기 메모리 (대화 이력)
├─ 장기 메모리 (사용자 습관, 선호도)
├─ 벡터 DB (유사도 검색)
└─ 메모리 업데이트
```

### 3.4 Tool Agent
**역할**: 모든 Tool의 실행 관리

```
Tool Agent
├─ Tool 등록/해제
├─ Tool 호출 라우팅
├─ 실행 결과 수집
└─ 오류 처리
```

### 3.5 Verifier Agent
**역할**: 작업 완료 후 결과 검증

```
Verifier Agent
├─ 성공 여부 확인
├─ 예상 결과와 비교
├─ 오류 감지
├─ 자동 재시도
└─ 사용자 피드백
```

## 4. Tool 시스템

### 4.1 Tool 구조

```python
BaseTool (기본 클래스)
├─ Browser Tool     : 웹 브라우저 자동화
├─ File Tool        : 파일/폴더 관리
├─ System Tool      : 프로그램/프로세스 제어
├─ Vision Tool      : 화면 분석 & OCR
├─ Voice Tool       : 음성 입출력
└─ Network Tool     : API 호출
```

### 4.2 Tool 실행 흐름

```
Tool Agent
  ↓
[Tool 선택]
  ↓
[파라미터 검증]
  ↓
[실행 권한 확인] (보안 레벨)
  ↓
[Tool 실행]
  ↓
[결과 반환]
```

## 5. AI/ML 모듈

### 5.1 LLM 통합

```
LLM Manager
├─ OpenAI GPT-4
│  ├─ 의도 분석
│  ├─ 작업 계획
│  └─ 응답 생성
├─ Claude-3
│  └─ 복잡한 추론
└─ Gemini
   └─ 멀티모달 분석
```

### 5.2 음성 처리

```
Speech Manager
├─ STT (Speech-to-Text)
│  └─ OpenAI Whisper
├─ Wake Word Detection
│  └─ 로컬 모델
├─ Speaker Verification
│  └─ SpeechBrain
└─ TTS (Text-to-Speech)
   └─ pyttsx3
```

### 5.3 비전 분석

```
Vision Manager
├─ Screenshot Capture
├─ OCR (EasyOCR)
├─ UI Element Detection
├─ Object Detection
└─ Error Analysis
```

## 6. 보안 계층

### 6.1 4단계 인증 시스템

```
Level 1: 일반 명령
├─ 시간 알려주기
├─ 날씨 확인
└─ 인증 불필요

Level 2: PC 제어
├─ 프로그램 실행
├─ 창 관리
└─ 음성 인증 필요

Level 3: 민감 작업
├─ 파일 삭제
├─ 프로그램 설치
└─ 음성 인증 + 승인 필요

Level 4: 고위험 작업
├─ 관리자 권한 요청
├─ 포맷
├─ 레지스트리 변경
└─ 음성 인증 + 비밀번호 필요
```

### 6.2 음성 인증 프로세스

```
[User Input] → [VAD (음성 감지)] → [Speaker Verification]
                                          ↓
                                   [Feature Extraction]
                                          ↓
                                   [SpeechBrain Model]
                                          ↓
                                   [Threshold Check]
                                          ↓
                              [Verified/Not Verified]
```

## 7. 데이터 흐름

### 7.1 대화 흐름

```
1. 입력: 사용자 음성
   ↓
2. 처리: Whisper STT
   ↓
3. 분석: LLM 의도 분석
   ↓
4. 계획: Planner 작업 분해
   ↓
5. 실행: Tool Agent 작업 실행
   ↓
6. 검증: Verifier 결과 확인
   ↓
7. 응답: TTS 음성 출력
   ↓
8. 저장: Memory 업데이트
```

### 7.2 메모리 구조

```
Short-term Memory (대화 컨텍스트)
├─ 현재 대화 주제
├─ 최근 5-10개 문장
└─ TTL: 세션 종료 시까지

Long-term Memory (사용자 정보)
├─ 사용자 선호도
├─ 자주 사용하는 프로그램
├─ 프로젝트 정보
├─ 업무 습관
└─ Vector DB에 저장
```

## 8. 시스템 상태 다이어그램

```
[Idle]
   ↓ (Wake Word Detected)
[Listening]
   ↓ (Audio Collected)
[Processing]
   ├─ Speech Recognition
   ├─ Intent Analysis
   ├─ Task Planning
   ├─ Authorization
   └─ Task Execution
   ↓
[Responding]
   ↓ (Response Generated)
[Idle]
```

## 9. 확장성 고려사항

### 9.1 마이크로서비스 분리

```
현재: 단일 프로세스
미래: 마이크로서비스

├─ 음성 서비스 (별도 프로세스)
├─ LLM 서비스 (별도 프로세스)
├─ Tool 서비스 (별도 프로세스)
└─ 메모리 서비스 (별도 프로세스)
```

### 9.2 Tool 플러그인 시스템

```
Tool Registry
├─ 동적 Tool 로드
├─ Tool 버전 관리
├─ Tool 권한 설정
└─ Tool 성능 모니터링
```

## 10. 성능 최적화

### 10.1 캐싱 전략

```
Query Cache
├─ 자주 사용되는 쿼리 캐싱
├─ 음성 특징 캐싱
└─ 스크린샷 캐싱
```

### 10.2 리소스 관리

```
Memory Management
├─ 메모리 사용량 모니터링
├─ GPU 사용 최적화
├─ 불필요한 모델 언로드
└─ 자동 가비지 컬렉션
```

## 11. 오류 처리

### 11.1 오류 복구 전략

```
Error Detection
   ↓
[Log Error]
   ↓
[Auto Retry] (최대 3회)
   ↓
[Fallback Action]
   ↓
[User Notification]
   ↓
[Manual Intervention]
```

### 11.2 오류 타입

```
1. 일시적 오류 (Transient)
   - API 타임아웃
   - 네트워크 오류
   → 자동 재시도

2. 영구적 오류 (Permanent)
   - 파일을 찾을 수 없음
   - 권한 거부
   → 사용자 알림

3. 시스템 오류 (System)
   - 메모리 부족
   - 디스크 부족
   → 시스템 정리 및 재시작
```

## 12. 배포 구조

```
NOVA AI Application
├─ Backend (Python)
│  ├─ Core Agents
│  ├─ AI/ML Models
│  ├─ Tool System
│  └─ Security Layer
├─ Frontend (Electron + React)
│  ├─ Chat UI
│  ├─ Task Planner Panel
│  ├─ Status Display
│  └─ Voice Button
└─ Database
   ├─ SQLite (로컬)
   └─ ChromaDB (벡터 DB)
```
