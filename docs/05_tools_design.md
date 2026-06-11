# Tool 설계 (Tool Design)

## 1. 개요

각 Tool은 **독립적인 모듈**로 설계되어 있으며, `BaseTool` 추상 클래스를 상속받습니다.
Tool Agent가 모든 Tool을 관리하고 실행합니다.

## 2. Browser Tool 상세 설계

### 2.1 개요

**용도**: 웹 브라우저 자동화 (Playwright 기반)

**지원 기능**:
- 웹 페이지 네비게이션
- 요소 클릭/입력
- 폼 자동 작성
- 웹 검색
- 스크린샷 캡처
- 텍스트 추출

### 2.2 상태 관리

```python
BrowserTool 상태:
├─ Uninitialized: 초기 상태
├─ Initialized: 브라우저 시작
├─ Connected: 페이지 로드
├─ Processing: 작업 중
└─ Idle: 대기 상태
```

### 2.3 주요 메서드

#### initialize()
```python
async def initialize() -> bool:
    """
    브라우저 초기화 (Playwright)
    
    과정:
    1. Playwright 시작
    2. Chromium 브라우저 실행
    3. 새 컨텍스트/페이지 생성
    
    Returns: 초기화 성공 여부
    """
```

#### navigate(url)
```python
async def navigate(url: str) -> Dict[str, Any]:
    """
    웹 페이지 이동
    
    Args:
        url: 목표 URL
        
    Process:
    1. URL 형식 검증 (http:// 추가)
    2. goto() 실행 (networkidle 대기)
    3. 현재 URL 저장
    4. 페이지 로드 완료 확인
    
    Returns:
    {
        "success": True,
        "url": "https://example.com",
        "title": "Example",
        "load_time": 2.5
    }
    """
```

#### click(selector)
```python
async def click(selector: str) -> Dict[str, Any]:
    """
    CSS 셀렉터로 요소 클릭
    
    Args:
        selector: CSS 셀렉터
        
    Process:
    1. 셀렉터 유효성 검사
    2. 요소 대기 (최대 5초)
    3. 클릭 실행
    4. 결과 확인
    
    Returns:
    {
        "success": True,
        "selector": "button.submit",
        "element_found": True,
        "clicked": True
    }
    """
```

#### type(selector, text)
```python
async def type(selector: str, text: str) -> Dict[str, Any]:
    """
    입력 필드에 텍스트 입력
    
    Args:
        selector: CSS 셀렉터
        text: 입력할 텍스트
        
    Process:
    1. 요소 선택
    2. 기존 텍스트 지우기 (clear)
    3. 텍스트 입력
    4. 입력 완료 대기
    
    Returns:
    {
        "success": True,
        "selector": "input.email",
        "text_length": 20
    }
    """
```

#### search(query)
```python
async def search(query: str) -> Dict[str, Any]:
    """
    Google에서 검색 수행
    
    Args:
        query: 검색어
        
    Process:
    1. Google 페이지 이동
    2. 검색창 입력
    3. Enter 키 실행
    4. 결과 페이지 로드 대기
    5. 검색 결과 개수 확인
    
    Returns:
    {
        "success": True,
        "query": "배틀필드 최적화",
        "results_count": 1000000,
        "time": 0.8
    }
    """
```

#### screenshot(path)
```python
async def screenshot(path: str = "screenshot.png") -> Dict[str, Any]:
    """
    현재 페이지 스크린샷 캡처
    
    Args:
        path: 저장 경로
        
    Returns:
    {
        "success": True,
        "path": "screenshot.png",
        "width": 1920,
        "height": 1080,
        "size_bytes": 102400
    }
    """
```

### 2.4 에러 처리

```python
Browser 에러 처리:
├─ TimeoutError: 페이지 로드 타임아웃
│  └─ 조치: 재시도 또는 다른 페이지로 이동
├─ ElementNotFound: 셀렉터 미일치
│  └─ 조치: 셀렉터 수정 또는 대기
├─ NetworkError: 네트워크 오류
│  └─ 조치: 연결 재시도
└─ NavigationError: 페이지 이동 실패
   └─ 조치: URL 검증 후 재시도
```

### 2.5 성능 최적화

```python
최적화 전략:
1. 페이지 캐싱
   - 같은 URL 재방문 시 캐시된 DOM 사용
   
2. 요소 선택기 캐싱
   - 자주 사용되는 셀렉터 미리 로드
   
3. 이미지 비활성화
   - 성능 향상을 위해 이미지 로드 생략 (선택)
   
4. 병렬 탭 관리
   - 여러 탭에서 동시 작업 가능
```

## 3. File Tool 상세 설계

### 3.1 개요

**용도**: 파일/폴더 관리 (os, shutil 기반)

**지원 기능**:
- 파일 생성/삭제/복사/이동
- 디렉토리 관리
- 파일 검색
- 파일 읽기/쓰기

### 3.2 보안 고려사항

```python
파일 보안:
1. 경로 검증
   - 상대경로로 ../ 를 통한 탈출 방지
   - Windows/Linux 경로 모두 지원
   
2. 권한 확인
   - 파일 삭제 시 Security Level 3+ 필요
   - 시스템 폴더 접근 제한
   
3. 파일 크기 제한
   - 한 번에 읽기: 최대 100MB
   - 메모리 초과 방지
```

### 3.3 주요 메서드

#### search(query, path)
```python
async def search(query: str, path: str = None) -> Dict[str, Any]:
    """
    파일 검색 (와일드카드 지원)
    
    Args:
        query: 검색 패턴 (예: "*.pdf", "config*")
        path: 검색 시작 경로
        
    Returns:
    {
        "success": True,
        "query": "*.pdf",
        "results": [
            "C:/Downloads/document1.pdf",
            "C:/Downloads/document2.pdf"
        ],
        "count": 2,
        "search_time": 1.2
    }
    
    최적화:
    - 최대 50개 결과만 반환
    - 숨김 파일 제외
    - 시스템 폴더 제외
    """
```

#### organize_by_type(path)
```python
async def organize_by_type(path: str) -> Dict[str, Any]:
    """
    폴더 자동 정렬 (파일 유형별)
    
    원본 구조:
    Downloads/
    ├─ document.pdf
    ├─ image.jpg
    ├─ video.mp4
    └─ archive.zip
    
    정렬 후:
    Downloads/
    ├─ PDFs/
    │  └─ document.pdf
    ├─ Images/
    │  └─ image.jpg
    ├─ Videos/
    │  └─ video.mp4
    └─ Archives/
       └─ archive.zip
    
    Returns:
    {
        "success": True,
        "path": "C:/Downloads",
        "folders_created": 4,
        "files_moved": 4
    }
    """
```

## 4. System Tool 상세 설계

### 4.1 개요

**용도**: Windows 시스템 제어

**지원 기능**:
- 프로그램 실행/종료
- 프로세스 정보 조회
- 바로가기 실행
- 단축키 실행

### 4.2 프로세스 관리

```python
프로세스 생명주기:
1. 실행 대기
   └─ 권한 확인
   
2. 프로세스 시작
   └─ 자식 프로세스 추적
   
3. 실행 중
   └─ CPU/메모리 모니터링
   
4. 종료
   └─ 정상 종료 또는 강제 종료
```

### 4.3 주요 메서드

#### launch_program(program_name, args)
```python
async def launch_program(
    program_name: str,
    args: List[str] = None
) -> Dict[str, Any]:
    """
    프로그램 실행
    
    Args:
        program_name: 프로그램명 또는 경로
        args: 실행 인자
        
    프로그램 검색 순서:
    1. 정확한 경로
    2. PATH 환경변수
    3. Windows 설치 폴더
    4. 시작 메뉴 바로가기
    
    Returns:
    {
        "success": True,
        "program": "VS Code",
        "pid": 12345,
        "timestamp": "2026-06-11T10:00:00Z"
    }
    """
```

#### get_process_info(process_name)
```python
async def get_process_info(process_name: str) -> Dict[str, Any]:
    """
    프로세스 상세 정보 조회
    
    Returns:
    {
        "success": True,
        "name": "chrome.exe",
        "pid": 5678,
        "cpu_percent": 15.3,
        "memory_mb": 512.5,
        "threads": 42,
        "status": "running",
        "create_time": "2026-06-11T08:30:00Z"
    }
    """
```

## 5. Vision Tool (Screen Analysis) 상세 설계

### 5.1 개요

**용도**: 화면 분석 (EasyOCR 기반)

**기능**:
- 스크린샷 캡처
- OCR 텍스트 추출
- UI 요소 감지
- 화면 분석

### 5.2 OCR 처리 흐름

```python
OCR 파이프라인:
1. 스크린샷 캡처
   └─ PIL.ImageGrab.grab()
   
2. 이미지 전처리
   ├─ 그레이스케일 변환
   ├─ 노이즈 제거 (선택)
   └─ 대비 조정
   
3. EasyOCR 인식
   ├─ 다중언어 지원 (한영)
   ├─ 신뢰도 계산
   └─ 바운딩박스 추출
   
4. 결과 후처리
   ├─ 텍스트 정렬
   ├─ 신뢰도 필터링 (0.5 이상)
   └─ 중복 제거
```

### 5.3 주요 메서드

#### find_button(button_name)
```python
async def find_button(button_name: str) -> Dict[str, Any]:
    """
    화면에서 버튼 찾기
    
    Args:
        button_name: 버튼 텍스트
        
    Process:
    1. 스크린샷 캡처
    2. OCR로 모든 텍스트 추출
    3. 텍스트 매칭
    4. 바운딩박스 중심 계산
    5. 마우스 좌표 반환
    
    Returns:
    {
        "success": True,
        "button": "확인",
        "location": (950, 500),
        "confidence": 0.98,
        "bbox": [[900, 480], [1000, 520]]
    }
    """
```

#### analyze_screen()
```python
async def analyze_screen() -> Dict[str, Any]:
    """
    현재 화면 종합 분석
    
    Returns:
    {
        "success": True,
        "application": "Chrome",
        "window_title": "Google Search",
        "text_content": "검색 결과...",
        "text_regions": 45,
        "has_buttons": True,
        "has_errors": False,
        "error_messages": [],
        "analysis_time": 0.5
    }
    """
```

## 6. Voice Tool 상세 설계

### 6.1 개요

**용도**: 음성 입출력

**기능**:
- 음성 인식 (STT)
- 텍스트 음성 변환 (TTS)
- 호출어 감지
- 음성 녹음/재생

### 6.2 음성 인식 파이프라인

```python
STT 파이프라인 (Whisper):
1. 음성 캡처
   ├─ sounddevice로 마이크 입력
   ├─ 16kHz 샘플링
   └─ PCM 데이터 수집
   
2. 음성 인식
   ├─ Whisper 모델 (base)
   ├─ 한영 다중언어 지원
   └─ 신뢰도 계산
   
3. 텍스트 후처리
   ├─ 띄어쓰기 정규화
   ├─ 특수문자 제거
   └─ 신뢰도 필터링
```

### 6.3 주요 메서드

#### recognize_speech(timeout)
```python
async def recognize_speech(timeout: float = 10) -> Dict[str, Any]:
    """
    사용자 음성 인식
    
    Args:
        timeout: 최대 대기 시간 (초)
        
    Returns:
    {
        "success": True,
        "text": "VS Code 실행해줘",
        "confidence": 0.95,
        "language": "ko",
        "duration": 3.2,
        "recognition_time": 0.8
    }
    """
```

#### synthesize_speech(text, speed)
```python
async def synthesize_speech(
    text: str,
    speed: float = 1.0
) -> Dict[str, Any]:
    """
    텍스트를 음성으로 변환 및 재생
    
    Args:
        text: 변환할 텍스트
        speed: 속도 (0.5~2.0)
        
    Returns:
    {
        "success": True,
        "text": "네, 도와드리겠습니다",
        "duration": 1.5,
        "speed": 1.0
    }
    """
```

## 7. Network Tool 상세 설계

### 7.1 개요

**용도**: 네트워크 작업

**기능**:
- HTTP 요청 (GET, POST)
- 파일 다운로드
- 연결 확인

### 7.2 주요 메서드

#### http_request(method, url, data, timeout)
```python
async def http_request(
    method: str,
    url: str,
    data: Dict = None,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    HTTP 요청 실행
    
    Args:
        method: GET, POST, PUT, DELETE
        url: 요청 URL
        data: 요청 바디
        timeout: 타임아웃 (초)
        
    Returns:
    {
        "success": True,
        "status_code": 200,
        "response": {...},
        "response_time": 0.5
    }
    """
```

#### download_file(url, path)
```python
async def download_file(
    url: str,
    path: str
) -> Dict[str, Any]:
    """
    파일 다운로드
    
    Returns:
    {
        "success": True,
        "url": "https://example.com/file.zip",
        "path": "C:/Downloads/file.zip",
        "size_bytes": 1024000,
        "download_time": 5.2
    }
    """
```

## 8. Tool 간 상호작용

### 8.1 Tool 체이닝

```python
예제: 웹사이트에서 파일 다운로드 후 정렬

1. [Browser] 웹사이트 접속
2. [Browser] 다운로드 버튼 클릭
3. [Network] 파일 다운로드
4. [File] 다운로드 폴더 정렬
5. [Vision] 완료 메시지 화면에서 확인
```

### 8.2 에러 처리 및 재시도

```python
Tool 재시도 정책:

1회차 실패
├─ 일시적 오류 (Timeout, Network)
│  └─ 2초 대기 후 재시도
│  
2회차 실패
├─ 영구적 오류 (FileNotFound, Permission)
│  └─ 사용자에게 알림
│  
3회차 실패
└─ 작업 포기
   └─ Verifier에 실패 보고
```
