# Solar Blind Adjuster - 설계 계획 문서

## 1. 프로젝트 개요

### 1.1 프로젝트명
**Solar Blind Adjuster** (태양광 블라인드 조절사)

### 1.2 프로젝트 설명
태양의 실시간 위치를 추적하여 사용자가 설정한 일조 전략에 따라 블라인드를 지능적으로 자동 제어하는 HomeAssistant 커스텀 통합 컴포넌트

### 1.3 목표
- 태양 위치 기반 정밀한 블라인드 자동 제어
- 직관적인 UI/UX로 누구나 쉽게 설정 가능
- 다양한 일조 전략 제공으로 사용자 맞춤 자동화
- 에너지 효율 최적화 지원

---

## 2. 핵심 기능 명세

### 2.1 태양 위치 추적
- **GPS 좌표 기반 계산**: 위도, 경도 입력
- **고도 보정**: 건물 높이 및 지형 고도 반영
- **실시간 추적**: 태양 고도각, 방위각 계산
- **천문학적 정확도**: 일출/일몰 시각 정밀 계산

### 2.2 블라인드 자동 제어
- **위치 제어**: 블라인드 열림 정도 (0-100%)
- **각도 제어**: 슬랫 각도 조절 (0-100%)
- **부드러운 전환**: 급격한 변화 방지
- **최소 동작 간격**: 모터 보호

### 2.3 일조 전략

#### 전략 1: 빛 최대 유입 (Maximize Light)
- 태양광을 최대한 실내로 유입
- 자연 채광 극대화
- 겨울철, 북향 창문에 적합

#### 전략 2: 빛 차단 (Block Light)
- 직사광선 차단으로 실내 온도 상승 억제
- 눈부심 방지
- 여름철, 남향 창문에 적합

#### 전략 3: 하이브리드 (Hybrid)
- 시간대별 전략 자동 전환
- 계절 변화 자동 감지
- 최적의 실내 환경 유지

#### 전략 4: 수동 모드 (Manual)
- 자동 제어 비활성화
- 사용자가 직접 제어
- 언제든 전환 가능

### 2.4 일출/일몰 자동화
- **일출 시 동작**: 설정된 상태로 자동 전환
- **일몰 시 동작**: 프라이버시 모드 활성화
- **시간 오프셋**: 일출/일몰 전후 N분 조정 가능
- **계절별 자동 조정**: 낮 길이 변화 대응

---

## 3. 시스템 아키텍처

### 3.1 컴포넌트 구조
```
custom_components/solar_blind_adjuster/
├── __init__.py                 # 컴포넌트 초기화 및 설정
├── manifest.json               # 통합 컴포넌트 메타데이터
├── const.py                    # 상수 및 설정 키 정의
├── config_flow.py              # UI 기반 설정 흐름
├── strings.json                # 다국어 지원 문자열
├── translations/               # 언어별 번역 파일
│   ├── en.json
│   └── ko.json
├── coordinator.py              # 데이터 업데이트 코디네이터
├── solar_calculator.py         # 태양 위치 계산 엔진
├── blind_controller.py         # 블라인드 제어 로직
├── strategy_engine.py          # 전략 선택 및 실행
├── sensor.py                   # 센서 엔티티
├── binary_sensor.py            # 바이너리 센서 엔티티
├── switch.py                   # 스위치 엔티티 (수동 모드 토글)
└── services.yaml               # 커스텀 서비스 정의
```

### 3.2 데이터 흐름 다이어그램
```
[설정 입력]
    ↓
[태양 위치 계산 엔진]
    ↓
[현재 태양 위치 데이터]
    ↓
[전략 엔진] ← [사용자 선택 전략]
    ↓
[블라인드 제어 명령 생성]
    ↓
[HomeAssistant Cover 엔티티]
    ↓
[실제 블라인드 디바이스]
```

### 3.3 통합 방식
- **Integration Type**: Custom Component
- **Configuration**: UI Config Flow + YAML 지원
- **Platform**: sensor, binary_sensor, switch
- **Dependencies**: astral, pytz

---

## 4. 상세 설계

### 4.1 태양 위치 계산 모듈

#### 입력 데이터
- 위도 (latitude): -90° ~ 90°
- 경도 (longitude): -180° ~ 180°
- 고도 (elevation): 미터 단위
- 타임존 (timezone): IANA 타임존 문자열
- 현재 시각

#### 출력 데이터
- 태양 고도각 (altitude): -90° ~ 90°
- 태양 방위각 (azimuth): 0° ~ 360° (북쪽 기준)
- 일출 시각 (sunrise)
- 일몰 시각 (sunset)
- 태양 정오 (solar_noon)
- 일조 시간 (daylight_duration)
- 태양광 상대 강도 (solar_intensity): 0 ~ 100

#### 계산 주기
- 일반 시간대: 5분마다
- 일출/일몰 전후 1시간: 1분마다
- 수동 트리거: 즉시

### 4.2 블라인드 제어 모듈

#### 제어 파라미터
```
BlindState:
  - position: 0-100 (블라인드 위치, 0=완전 닫힘, 100=완전 열림)
  - tilt: 0-100 (슬랫 각도, 0=완전 닫힘, 100=완전 열림)
```

#### 창문 설정
```
WindowConfig:
  - azimuth: 0-360 (창문이 향하는 방향)
  - tilt_offset: -45 ~ 45 (슬랫 각도 보정값)
  - position_limits: min/max (동작 범위 제한)
  - tilt_limits: min/max (각도 범위 제한)
```

#### 제어 알고리즘 핵심 로직

**창문 직사광 여부 판단**
- 태양 방위각과 창문 방향의 각도 차이 계산
- 허용 오차 범위 내면 직사광으로 판단 (기본 ±45°)
- 태양 고도각이 임계값 이상일 때만 적용 (기본 15°)

**전략별 위치/각도 계산**
1. **Maximize Light**
   - 직사광 시: 완전 개방 + 빛 유입 최적 각도
   - 비직사광 시: 부분 개방 + 간접광 유입 각도

2. **Block Light**
   - 직사광 시: 부분 차단 + 직사광 차단 각도
   - 비직사광 시: 완전 개방 + 자유 각도

3. **Hybrid**
   - 시간대별 전략 자동 전환
   - 태양 고도각 기반 동적 조정

**부드러운 전환 로직**
- 이전 상태와 목표 상태 비교
- 변화량이 임계값 이상일 때만 실행 (기본 5%)
- 최소 동작 간격 준수 (기본 5분)

### 4.3 전략 엔진

#### 전략 선택 기준
- 사용자 수동 선택
- 시간대 기반 자동 전환
- 계절 기반 자동 전환
- 실내 온도 센서 연동 (선택 사항)
- 날씨 정보 연동 (선택 사항)

#### 전략 우선순위
1. 수동 모드 (최우선)
2. 일출/일몰 특수 동작
3. 시간대별 설정
4. 기본 전략

### 4.4 센서 엔티티

#### 제공 센서
```
sensor.solar_blind_adjuster_[name]_sun_altitude
  - 태양 고도각
  - 단위: 도(°)
  - 아이콘: mdi:angle-acute

sensor.solar_blind_adjuster_[name]_sun_azimuth
  - 태양 방위각
  - 단위: 도(°)
  - 아이콘: mdi:compass

sensor.solar_blind_adjuster_[name]_solar_intensity
  - 태양광 상대 강도
  - 단위: %
  - 아이콘: mdi:white-balance-sunny

sensor.solar_blind_adjuster_[name]_recommended_position
  - 추천 블라인드 위치
  - 단위: %
  - 아이콘: mdi:window-shutter

sensor.solar_blind_adjuster_[name]_recommended_tilt
  - 추천 슬랫 각도
  - 단위: %
  - 아이콘: mdi:blinds

binary_sensor.solar_blind_adjuster_[name]_sun_facing
  - 창문 직사광 여부
  - 아이콘: mdi:weather-sunny
```

#### 센서 속성
```
attributes:
  - sunrise: 일출 시각
  - sunset: 일몰 시각
  - solar_noon: 태양 정오
  - daylight_duration: 일조 시간
  - current_strategy: 현재 적용 전략
  - manual_override: 수동 모드 활성화 여부
  - next_update: 다음 업데이트 시각
  - window_azimuth: 창문 방향
```

---

## 5. 설정 구조

### 5.1 필수 설정
```yaml
solar_blind_adjuster:
  - name: "거실 블라인드"
    blind_entity_id: "cover.living_room_blind"
    latitude: 37.5665
    longitude: 126.9780
    elevation: 50
    window_azimuth: 180
```

### 5.2 선택 설정
```yaml
    # 전략 설정
    strategy: "block_light"  # maximize_light, block_light, hybrid, manual
    
    # 업데이트 주기
    update_interval: 300  # 초 단위, 기본 5분
    
    # 제어 범위
    position_limits:
      min: 0
      max: 100
    tilt_limits:
      min: 0
      max: 100
    
    # 부드러운 전환
    change_threshold: 5  # 변화량 임계값 (%)
    min_action_interval: 300  # 최소 동작 간격 (초)
    
    # 태양 추적 설정
    sun_facing_tolerance: 45  # 직사광 판단 허용 각도
    sun_altitude_threshold: 15  # 최소 태양 고도각
    
    # 일출 동작
    sunrise_action:
      enabled: true
      offset: 0  # 일출 후 몇 분 (음수 가능)
      position: 100
      tilt: 100
    
    # 일몰 동작
    sunset_action:
      enabled: true
      offset: -30  # 일몰 30분 전
      position: 0
      tilt: 0
    
    # Hybrid 전략 상세 설정
    hybrid_schedule:
      - start_time: "06:00"
        end_time: "09:00"
        strategy: "maximize_light"
      - start_time: "09:00"
        end_time: "18:00"
        strategy: "block_light"
      - start_time: "18:00"
        end_time: "22:00"
        strategy: "maximize_light"
```

### 5.3 UI Config Flow 단계
1. **기본 정보 입력**
   - 통합 이름
   - 블라인드 엔티티 선택

2. **위치 정보 입력**
   - 위도/경도 (HomeAssistant 기본값 사용 옵션)
   - 고도
   - 창문 방향

3. **전략 선택**
   - 4가지 전략 중 선택
   - 각 전략 설명 제공

4. **고급 설정** (선택)
   - 일출/일몰 동작
   - 제어 범위 제한
   - 업데이트 주기

---

## 6. 사용자 인터페이스

### 6.1 Lovelace 카드 구성

#### 기본 정보 카드
```yaml
type: vertical-stack
cards:
  - type: entities
    title: Solar Blind Adjuster - 거실
    entities:
      - entity: sensor.solar_blind_adjuster_living_sun_altitude
        name: 태양 고도각
      - entity: sensor.solar_blind_adjuster_living_sun_azimuth
        name: 태양 방위각
      - entity: binary_sensor.solar_blind_adjuster_living_sun_facing
        name: 직사광 여부
      - entity: sensor.solar_blind_adjuster_living_solar_intensity
        name: 일조 강도
```

#### 제어 상태 카드
```yaml
  - type: glance
    title: 추천 블라인드 상태
    entities:
      - entity: sensor.solar_blind_adjuster_living_recommended_position
        name: 위치
      - entity: sensor.solar_blind_adjuster_living_recommended_tilt
        name: 각도
```

#### 전략 선택 카드
```yaml
  - type: entities
    title: 제어 설정
    entities:
      - entity: input_select.solar_blind_adjuster_living_strategy
        name: 제어 전략
      - entity: switch.solar_blind_adjuster_living_manual_mode
        name: 수동 모드
```

#### 시간 정보 카드
```yaml
  - type: markdown
    content: |
      **일출:** {{ state_attr('sensor.solar_blind_adjuster_living_sun_altitude', 'sunrise') }}
      **일몰:** {{ state_attr('sensor.solar_blind_adjuster_living_sun_altitude', 'sunset') }}
      **일조 시간:** {{ state_attr('sensor.solar_blind_adjuster_living_sun_altitude', 'daylight_duration') }}
```

### 6.2 커스텀 카드 (선택 사항)
- 태양 경로 시각화
- 블라인드 상태 애니메이션
- 일일 일조량 그래프
- 전략 효과 비교 차트

---

## 7. 자동화 시나리오

### 7.1 기본 자동화
```yaml
automation:
  - alias: "Solar Blind Adjuster - 거실 자동 제어"
    trigger:
      - platform: state
        entity_id: sensor.solar_blind_adjuster_living_recommended_position
      - platform: state
        entity_id: sensor.solar_blind_adjuster_living_recommended_tilt
    condition:
      - condition: state
        entity_id: switch.solar_blind_adjuster_living_manual_mode
        state: 'off'
    action:
      - service: cover.set_cover_position
        target:
          entity_id: cover.living_room_blind
        data:
          position: "{{ states('sensor.solar_blind_adjuster_living_recommended_position') }}"
      - service: cover.set_cover_tilt_position
        target:
          entity_id: cover.living_room_blind
        data:
          tilt_position: "{{ states('sensor.solar_blind_adjuster_living_recommended_tilt') }}"
```

### 7.2 조건부 자동화
- 실내 온도 기반: 온도가 높을 때 Block Light 전략
- 재실 감지 기반: 사람이 없을 때 에너지 절약 모드
- 날씨 연동: 흐린 날 Maximize Light 전략

---

## 8. 고급 기능

### 8.1 머신러닝 학습 (Phase 3)
- 사용자 수동 조작 패턴 학습
- 최적 설정값 자동 제안
- 계절별 선호도 분석

### 8.2 에너지 최적화
- 냉난방 부하 최소화
- 조명 에너지 절약 계산
- 월간 에너지 보고서

### 8.3 다중 블라인드 연동
- 방향이 다른 여러 창문 통합 제어
- 그룹 단위 전략 적용
- 우선순위 기반 조정

### 8.4 외부 연동
- 날씨 서비스 (구름 정보)
- 실내 온습도 센서
- 조도 센서
- HVAC 시스템

---

## 9. 개발 로드맵

### Phase 1: MVP (4주)
**목표**: 핵심 기능 구현 및 테스트

- Week 1: 프로젝트 구조 및 태양 위치 계산 모듈
  - `manifest.json`, `const.py` 작성
  - `solar_calculator.py` 구현
  - 단위 테스트 작성

- Week 2: 블라인드 제어 로직 및 전략 엔진
  - `blind_controller.py` 구현
  - `strategy_engine.py` 기본 전략 구현
  - Maximize Light, Block Light 전략 완성

- Week 3: HomeAssistant 통합
  - `config_flow.py` UI 설정 구현
  - `sensor.py`, `binary_sensor.py` 엔티티 구현
  - `coordinator.py` 데이터 업데이트 로직

- Week 4: 테스트 및 문서화
  - 통합 테스트
  - 시뮬레이션 테스트 (하지/동지/춘분)
  - README 및 사용자 가이드 작성

### Phase 2: 고급 기능 (3주)
**목표**: 사용성 향상 및 기능 확장

- Week 5: Hybrid 전략 및 일출/일몰 자동화
  - 시간대별 전략 전환
  - 일출/일몰 이벤트 처리
  - 계절별 자동 조정

- Week 6: 슬랫 각도 정밀 제어
  - 태양 각도 기반 최적 각도 계산
  - 창문 방향 고려 알고리즘
  - 각도 변화 시뮬레이션

- Week 7: UI 개선 및 다국어 지원
  - Lovelace 카드 예제 제공
  - 한국어/영어 번역
  - 설정 검증 강화

### Phase 3: 최적화 및 확장 (2주)
**목표**: 성능 최적화 및 외부 연동

- Week 8: 성능 최적화
  - 계산 결과 캐싱
  - 불필요한 업데이트 최소화
  - 비동기 처리 개선

- Week 9: 외부 연동 및 베타 릴리스
  - 날씨 서비스 연동 (선택)
  - 에너지 최적화 모드
  - 베타 테스터 모집 및 피드백 수집

---

## 10. 테스트 전략

### 10.1 단위 테스트
```
test_solar_calculator:
  - 태양 위치 계산 정확도
  - 일출/일몰 시각 정확도
  - 극한 위도에서의 동작 (북극/남극)

test_blind_controller:
  - 직사광 판단 로직
  - 각도 계산 정확도
  - 제어 범위 제한

test_strategy_engine:
  - 전략별 올바른 출력
  - 전략 전환 로직
  - 우선순위 처리
```

### 10.2 통합 테스트
```
test_full_day_cycle:
  - 24시간 주기 시뮬레이션
  - 블라인드 상태 변화 추적
  - 예상 동작과 실제 동작 비교

test_season_change:
  - 하지/동지/춘분 시뮬레이션
  - 낮 길이 변화 대응
  - 일출/일몰 시각 변화 검증
```

### 10.3 실제 환경 테스트
```
test_real_world:
  - 다양한 창문 방향 (동/서/남/북향)
  - 여러 지역 (위도별)
  - 다양한 블라인드 타입
  - 장기간 안정성 (1주일 이상)
```

---

## 11. 성능 및 안정성

### 11.1 성능 목표
- 태양 위치 계산: < 100ms
- 블라인드 제어 명령 생성: < 50ms
- 메모리 사용량: < 50MB
- CPU 사용률: 평균 < 1%

### 11.2 안정성 보장
- **모터 보호**: 최소 동작 간격 강제
- **Failsafe 모드**: 오류 시 안전 상태로 복귀
- **수동 우선권**: 언제든 자동 제어 중단 가능
- **상태 복원**: 재시작 후 이전 설정 유지

### 11.3 에러 처리
- 블라인드 엔티티 응답 없음
- GPS 좌표 유효성 검증
- 타임존 오류 처리
- 네트워크 타임아웃 대응

---

## 12. 보안 및 프라이버시

### 12.1 데이터 처리
- **로컬 처리**: 모든 계산은 로컬에서 수행
- **외부 통신 없음**: 인터넷 연결 불필요 (날씨 연동 제외)
- **개인정보 미수집**: GPS 좌표는 로컬 저장만

### 12.2 권한 관리
- HomeAssistant 표준 권한 체계 준수
- 블라인드 제어 권한 필요
- 센서 읽기 권한 필요

---

## 13. 문서화 계획

### 13.1 사용자 문서
- **README.md**: 프로젝트 소개 및 빠른 시작 가이드
- **INSTALLATION.md**: 설치 방법 상세 가이드
- **CONFIGURATION.md**: 설정 옵션 완전 가이드
- **FAQ.md**: 자주 묻는 질문
- **TROUBLESHOOTING.md**: 문제 해결 가이드

### 13.2 개발자 문서
- **ARCHITECTURE.md**: 시스템 아키텍처 설명
- **API.md**: 내부 API 및 서비스 문서
- **CONTRIBUTING.md**: 기여 가이드라인
- **CHANGELOG.md**: 버전별 변경 사항

---

## 14. 배포 및 유지보수

### 14.1 배포 채널
- **HACS (HomeAssistant Community Store)**: 주 배포 채널
- **GitHub Releases**: 수동 설치용
- **Docker Hub**: 컨테이너 이미지 (선택)

### 14.2 버전 관리
- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Release Cycle**: 
  - Major: 1년
  - Minor: 분기별
  - Patch: 필요 시

### 14.3 커뮤니티 지원
- GitHub Issues: 버그 리포트 및 기능 요청
- GitHub Discussions: 사용자 커뮤니티
- Discord 채널 (선택)

---

## 15. 라이선스 및 크레딧

### 15.1 라이선스
- **MIT License**: 오픈소스 배포
- 상업적 사용 허용
- 재배포 자유

### 15.2 사용 라이브러리
- **astral**: 천문학적 계산 (Apache 2.0)
- **pytz**: 타임존 처리 (MIT)
- **HomeAssistant Core**: 통합 프레임워크 (Apache 2.0)

---

## 16. 성공 지표 (KPI)

### 16.1 기술적 지표
- GitHub Stars: 100+ (6개월 내)
- HACS 다운로드: 500+ (6개월 내)
- 버그 리포트 해결율: 90% 이상
- 코드 커버리지: 80% 이상

### 16.2 사용자 만족도
- 사용자 피드백 점수: 4.5+ / 5.0
- 재사용률: 80% 이상
- 추천 의향: 70% 이상

---

## 부록

### A. 용어 정의
- **태양 고도각 (Solar Altitude)**: 지평선에서 태양까지의 각도
- **태양 방위각 (Solar Azimuth)**: 북쪽을 기준으로 한 태양의 방향
- **일조량 (Solar Intensity)**: 단위 면적당 태양 에너지
- **슬랫 (Slat)**: 블라인드의 개별 가로 날개

### B. 참고 자료
- NOAA Solar Calculator
- PySolar Documentation
- Astral Documentation
- HomeAssistant Developer Documentation

### C. 연락처
- GitHub Repository: [예정]
- 개발자 이메일: [예정]
- 커뮤니티 포럼: [예정]
