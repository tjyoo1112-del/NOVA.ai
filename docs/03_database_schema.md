# 데이터베이스 설계 (Database Design)

## 1. 개요

NOVA AI는 **SQLite**를 주 데이터베이스로, **ChromaDB**를 벡터 데이터베이스로 사용합니다.

- **SQLite**: 로컬 저장소, 사용자 정보, 메모리, 작업 로그
- **ChromaDB**: 벡터 저장소, 의미론적 검색

## 2. 데이터베이스 다이어그램 (ERD)

```
┌─────────────────────────┐
│         Users           │
├─────────────────────────┤
│ id (PK)                 │
│ username (UNIQUE)       │
│ email (UNIQUE)          │
│ created_at              │
│ last_login              │
└──────────┬──────────────┘
           │
           ├─────┬──────────────────┬──────────────────┐
           │     │                  │                  │
┌──────────▼──┐ ┌▼──────────────┐ ┌▼──────────────┐ ┌▼──────────────┐
│VoiceProfile │ │   Memories    │ │   TaskLogs    │ │ SystemPrefs   │
├─────────────┤ ├───────────────┤ ├───────────────┤ ├───────────────┤
│ id (PK)     │ │ id (PK)       │ │ id (PK)       │ │ id (PK)       │
│ user_id (FK)│ │ user_id (FK)  │ │ user_id (FK)  │ │ user_id (FK)  │
│ features    │ │ key           │ │ task_name     │ │ preference    │
│ created_at  │ │ value         │ │ parameters    │ │ value         │
│ updated_at  │ │ category      │ │ result        │ │ created_at    │
└─────────────┘ │ created_at    │ │ success       │ └───────────────┘
                │ updated_at    │ │ duration      │
                └───────────────┘ │ created_at    │
                                  └───────────────┘
```

## 3. 테이블 정의

### 3.1 Users 테이블

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

**용도**: 사용자 기본 정보

**컬럼 설명**:
- `id`: 고유 식별자
- `username`: 사용자 이름
- `email`: 이메일 주소
- `created_at`: 계정 생성 시간
- `last_login`: 마지막 로그인 시간
- `is_active`: 계정 활성 여부

### 3.2 VoiceProfile 테이블

```sql
CREATE TABLE voice_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    feature_vector TEXT NOT NULL,  -- JSON 형식의 음성 특징
    language VARCHAR(10),           -- 'ko', 'en' 등
    sample_count INTEGER,           -- 등록된 샘플 수
    verification_score FLOAT,       -- 인증 정확도
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_voice_profile_user_id ON voice_profiles(user_id);
```

**용도**: 음성 인증을 위한 음성 특징 저장

**컬럼 설명**:
- `feature_vector`: SpeechBrain 모델로 추출한 음성 특징 (JSON)
- `language`: 음성 언어
- `sample_count`: 등록된 음성 샘플 수
- `verification_score`: 음성 인증 정확도 (0-1)

### 3.3 Memories 테이블

```sql
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    key VARCHAR(100) NOT NULL,      -- 메모리 키
    value TEXT NOT NULL,             -- 메모리 값
    category VARCHAR(50),            -- 카테고리: 'habit', 'preference', 'project' 등
    importance INTEGER DEFAULT 5,    -- 중요도 (1-10)
    access_count INTEGER DEFAULT 0,  -- 접근 횟수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,            -- 만료 시간 (NULL이면 만료 안 함)
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, key, category)
);

CREATE INDEX idx_memories_user_id ON memories(user_id);
CREATE INDEX idx_memories_category ON memories(category);
```

**용도**: 사용자 습관, 선호도, 프로젝트 정보 저장

**컬럼 설명**:
- `key`: 메모리 키 (예: "favorite_program", "work_start_time")
- `value`: 메모리 값
- `category`: 메모리 분류
- `importance`: 중요도 (검색 순서에 영향)
- `access_count`: 사용 빈도
- `expires_at`: 자동 삭제 시간

**예시 데이터**:
```python
{
    "key": "favorite_programs",
    "value": "VS Code, Discord, Steam",
    "category": "habit",
    "importance": 8
}
```

### 3.4 TaskLogs 테이블

```sql
CREATE TABLE task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_name VARCHAR(100) NOT NULL,
    tool_name VARCHAR(50),           -- 사용된 Tool
    parameters TEXT,                 -- 파라미터 (JSON)
    result TEXT,                     -- 결과 (JSON)
    success INTEGER,                 -- 0=실패, 1=성공
    duration FLOAT,                  -- 실행 시간 (초)
    error_message TEXT,              -- 오류 메시지
    retries INTEGER DEFAULT 0,       -- 재시도 횟수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_task_logs_user_id ON task_logs(user_id);
CREATE INDEX idx_task_logs_created_at ON task_logs(created_at);
```

**용도**: 모든 작업 실행 이력 기록

**컬럼 설명**:
- `task_name`: 작업 이름
- `tool_name`: 사용된 Tool
- `parameters`: 입력 파라미터 (JSON)
- `result`: 작업 결과 (JSON)
- `success`: 성공 여부
- `duration`: 실행 시간
- `error_message`: 실패 시 오류 메시지

**예시 데이터**:
```python
{
    "task_name": "Launch Program",
    "tool_name": "System",
    "parameters": {"program": "VS Code"},
    "result": {"success": True, "pid": 1234},
    "success": 1,
    "duration": 2.5
}
```

### 3.5 SystemPrefs 테이블

```sql
CREATE TABLE system_prefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    preference VARCHAR(100) NOT NULL,
    value TEXT NOT NULL,
    data_type VARCHAR(20),          -- 'string', 'int', 'float', 'bool'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, preference)
);
```

**용도**: 시스템 설정 및 사용자 선호도

**예시 데이터**:
```
preference='security_level', value='2'
preference='voice_auth_threshold', value='0.85'
preference='tts_speed', value='1.0'
preference='theme', value='dark'
```

### 3.6 ConversationHistory 테이블

```sql
CREATE TABLE conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_input TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    intent VARCHAR(100),
    entities TEXT,                  -- JSON
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_conversation_user_id ON conversation_history(user_id);
CREATE INDEX idx_conversation_session_id ON conversation_history(session_id);
```

**용도**: 대화 이력 저장 (벡터 DB와 함께)

## 4. ChromaDB (벡터 데이터베이스)

### 4.1 용도
- 사용자 메모리 의미론적 검색
- 유사한 대화 검색
- 프로젝트 정보 검색

### 4.2 컬렉션 구조

```python
# Memories Collection
{
    "id": "memory_123",
    "embedding": [0.123, 0.456, ...],  # 벡터
    "metadata": {
        "user_id": 1,
        "key": "favorite_program",
        "category": "habit",
        "importance": 8
    },
    "document": "VS Code를 자주 사용한다"
}

# Conversation Collection
{
    "id": "conv_456",
    "embedding": [0.789, 0.012, ...],
    "metadata": {
        "user_id": 1,
        "session_id": "session_001",
        "timestamp": "2026-06-11T10:00:00Z"
    },
    "document": "VS Code를 실행해줘"
}
```

## 5. 데이터 흐름

### 5.1 사용자 입력 → 저장

```
음성 입력
   ↓
[STT] → 텍스트 변환
   ↓
[Conversation History] 저장 (SQLite)
   ↓
[ChromaDB] 임베딩 저장
```

### 5.2 메모리 조회

```
[Query] "VS Code 실행하고 싶어"
   ↓
[ChromaDB] 유사 메모리 검색
   ↓
[SQLite] 세부 정보 조회
   ↓
[결과] 관련 메모리 반환
```

## 6. 백업 및 복구

### 6.1 백업 전략

```
일일 백업
├─ SQLite DB
├─ ChromaDB 컬렉션
└─ 음성 프로필

저장 위치
├─ 로컬: ./data/backup/
├─ 클라우드: (미래)
└─ 외장: USB (수동)
```

### 6.2 복구 프로세스

```
[복구 요청]
   ↓
[백업 목록 표시]
   ↓
[사용자 선택]
   ↓
[데이터 복구]
   ↓
[검증]
   ↓
[완료]
```

## 7. 성능 최적화

### 7.1 인덱싱 전략

```sql
-- 자주 조회되는 컬럼에 인덱스
CREATE INDEX idx_memories_user_category ON memories(user_id, category);
CREATE INDEX idx_task_logs_user_success ON task_logs(user_id, success);
```

### 7.2 쿼리 최적화

```sql
-- EXPLAIN 사용하여 쿼리 계획 분석
EXPLAIN QUERY PLAN
SELECT * FROM memories
WHERE user_id = 1 AND category = 'habit'
ORDER BY access_count DESC;
```

## 8. 데이터 보안

### 8.1 암호화

```
민감 데이터 암호화
├─ 음성 특징: AES-256
├─ 개인정보: AES-256
└─ 비밀번호: bcrypt
```

### 8.2 접근 제어

```
데이터 접근
├─ 사용자 본인의 데이터만 접근
├─ 에이전트: 권한 기반 접근
└─ 감사: 모든 접근 로깅
```

## 9. 마이그레이션 전략

### 9.1 초기 생성

```python
# src/database/init.py
def init_database():
    """데이터베이스 초기화"""
    conn = sqlite3.connect('nova.db')
    cursor = conn.cursor()
    
    # 모든 CREATE TABLE 실행
    # ...
    
    conn.commit()
    conn.close()
```

### 9.2 버전 관리

```
Alembic 사용
├─ 마이그레이션 버전 관리
├─ 스키마 변경 추적
└─ 롤백 지원
```

## 10. 모니터링

### 10.1 DB 상태 모니터링

```
모니터링 항목
├─ 데이터베이스 크기
├─ 쿼리 성능
├─ 연결 수
├─ 에러율
└─ 백업 상태
```
