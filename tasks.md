# Solar Blind Adjuster - 개발 태스크

## Phase 1: MVP 개발

### Week 1: 기본 구조 및 태양 위치 계산

- [x] 1. 프로젝트 구조 및 기본 파일 생성 (manifest.json, const.py, __init__.py)
- [x] 2. 태양 위치 계산 모듈 구현 (solar_calculator.py)

### Week 2: 블라인드 제어 로직 및 전략

- [x] 3. 블라인드 제어 로직 구현 (blind_controller.py)
- [x] 4. 전략 엔진 구현 - 기본 전략 (strategy_engine.py)
- [x] 5. Maximize Light 전략 완성
- [x] 6. Block Light 전략 완성

### Week 3: HomeAssistant 통합

- [x] 7. 데이터 업데이트 코디네이터 구현 (coordinator.py)
- [x] 8. UI Config Flow 구현 (config_flow.py)
- [x] 9. 센서 엔티티 구현 (sensor.py)
- [x] 10. 바이너리 센서 엔티티 구현 (binary_sensor.py)
- [x] 11. 스위치 엔티티 구현 - 수동 모드 토글 (switch.py)
- [x] 12. 다국어 지원 파일 작성 (strings.json, translations/)
- [x] 13. 서비스 정의 파일 작성 (services.yaml)

### Week 4: 테스트 및 문서화

- [ ] 14. 단위 테스트 작성 (태양 위치 계산, 블라인드 제어 로직) - Phase 2로 이동
- [ ] 15. 통합 테스트 작성 (24시간 주기 시뮬레이션) - Phase 2로 이동
- [x] 16. README 및 사용자 가이드 작성

---

## 진행 상황

### 완료된 작업

- 태스크 1: 프로젝트 구조 및 기본 파일 생성 완료
  - custom_components/solar_blind_adjuster/ 디렉토리 생성
  - manifest.json 작성 (도메인, 의존성, 버전 정보)
  - const.py 작성 (상수, 설정 키, 기본값 정의)
  - __init__.py 작성 (통합 컴포넌트 초기화)

- 태스크 2: 태양 위치 계산 모듈 구현 완료
  - SolarCalculator 클래스 구현
  - 태양 고도각, 방위각 계산
  - 일출/일몰/정오 시각 계산
  - 태양광 상대 강도 계산
  - 창문 직사광 여부 판단 로직
  - 동적 업데이트 주기 계산

- 태스크 3: 블라인드 제어 로직 구현 완료
  - BlindController 클래스 구현
  - BlindState, WindowConfig 데이터 클래스
  - Maximize Light 전략 계산 로직
  - Block Light 전략 계산 로직
  - 변화량 임계값 및 최소 동작 간격 체크
  - 제어 범위 제한 적용

- 태스크 4-6: 전략 엔진 및 전략 구현 완료
  - StrategyEngine 클래스 구현
  - HybridScheduleEntry 클래스 (시간대별 전략 관리)
  - Hybrid 모드 스케줄 파싱
  - 전략 우선순위 처리 (수동 모드 > 하이브리드 > 기본 전략)
  - 일출/일몰 자동화 액션 처리
  - Maximize Light 전략 (blind_controller에 구현됨)
  - Block Light 전략 (blind_controller에 구현됨)

- 태스크 7: 데이터 업데이트 코디네이터 구현 완료
  - SolarBlindAdjusterCoordinator 클래스 구현
  - 태양 데이터 주기적 업데이트
  - 블라인드 추천 상태 계산
  - 일출/일몰 액션 우선순위 처리
  - 전략 변경 및 수동 모드 토글 메서드
  - 블라인드 동작 기록 기능

- 태스크 8: UI Config Flow 구현 완료
  - SolarBlindAdjusterConfigFlow 클래스 구현
  - 4단계 설정 흐름 (기본 정보, 위치, 전략, 고급 설정)
  - 블라인드 엔티티 선택 및 검증
  - 위도/경도/창문 방향 설정
  - 전략 선택 UI
  - 고급 옵션 (업데이트 주기, 제어 범위, 임계값)
  - Options Flow 구현

- 태스크 9-11: 센서 및 엔티티 구현 완료
  - 센서 엔티티 5개 (태양 고도각, 방위각, 일조 강도, 추천 위치/각도)
  - 바이너리 센서 (창문 직사광 여부)
  - 스위치 엔티티 (수동 모드 토글)
  - CoordinatorEntity 기반 구현
  - 상태 속성 (일출/일몰, 전략, 마지막 동작 시간 등)

- 태스크 12-13: 다국어 지원 및 서비스 정의 완료
  - strings.json (기본 번역 파일)
  - translations/en.json (영어)
  - translations/ko.json (한국어)
  - services.yaml (서비스 정의: set_strategy, refresh_calculation, record_blind_action)

- 태스크 16: README 및 사용자 가이드 작성 완료
  - 주요 기능 소개
  - 설치 및 설정 가이드
  - 제어 전략 설명
  - 생성되는 엔티티 목록
  - 자동화 예제
  - 서비스 사용법
  - Lovelace 카드 예제
  - 트러블슈팅 가이드

### 현재 작업

- Phase 1 MVP 개발 완료!

### 다음 작업

- Phase 2: 고급 기능 개발
  - Hybrid 모드 스케줄 UI 설정
  - 일출/일몰 자동화 UI 설정
  - 단위/통합 테스트 작성
  - 날씨 서비스 연동
