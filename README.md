# Solar Blind Adjuster

태양의 실시간 위치를 추적하여 블라인드를 지능적으로 자동 제어하는 HomeAssistant 커스텀 통합 컴포넌트입니다.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=YOUR_GITHUB_USERNAME&repository=solar_blind_adjuster&category=integration)

## 주요 기능

- 🌞 **태양 위치 기반 정밀 제어**: GPS 좌표 기반으로 태양 고도각, 방위각 실시간 계산
- 🎯 **다양한 제어 전략**: 빛 최대 유입, 직사광 차단, 하이브리드, 수동 모드
- 🏠 **HomeAssistant 완벽 통합**: UI 기반 설정, 센서 엔티티, 자동화 지원
- 🌍 **다국어 지원**: 한국어, 영어
- ⏰ **일출/일몰 자동화**: 시간대별 자동 제어 및 계절 변화 대응
- 🧪 **시뮬레이션/미리보기**: 특정 날짜·시간 기준으로 추천 값을 확인

## 설치 방법

### 원클릭 설치 (HACS 필요)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=W1NNERSTAY&repository=solar-blind-adjuster&category=integration)

위 버튼을 클릭하면 HACS를 통해 자동으로 설치됩니다.

### HACS를 통한 수동 설치

1. HACS에서 "Solar Blind Adjuster" 검색
2. 설치 후 HomeAssistant 재시작

### 수동 설치

1. 이 저장소를 클론하거나 다운로드
2. `custom_components/solar_blind_adjuster` 폴더를 HomeAssistant의 `custom_components` 디렉토리에 복사
3. HomeAssistant 재시작

## 설정

### 원클릭 설정

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=solar_blind_adjuster)

위 버튼을 클릭하면 바로 설정을 시작할 수 있습니다.

### UI를 통한 수동 설정
> 이 통합은 블라인드를 직접 제어하지 않고 추천 값만 제공합니다. 생성되는 센서를 자동화에 연결하면 됩니다.

1. **설정** > **기기 및 서비스** > **통합** 이동
2. **+ 통합 추가** 클릭
3. "Solar Blind Adjuster" 검색
4. 설정 마법사를 따라 진행:

#### 1단계: 기본 정보
- 통합 이름 입력

#### 2단계: 위치 정보
- 위도/경도 (기본값: HomeAssistant 설정값)
- 고도 (미터 단위)
- 창문 방향: 동/서/남/북 선택 또는 직접 각도 입력(0-360°, 0=북쪽)

#### 3단계: 제어 전략 선택
- **Maximize Light**: 태양광 최대 유입
- **Block Light**: 직사광선 차단
- **Hybrid**: 시간대별 자동 전환
- **Manual**: 수동 모드

#### 4단계: 고급 설정 (선택 사항)
- 업데이트 주기
- 변화 임계값
- 제어 범위 제한

## 제어 전략

### Maximize Light (빛 최대 유입)
- 태양광을 최대한 실내로 유입
- 자연 채광 극대화
- 추천 환경: 겨울철, 북향 창문

### Block Light (직사광 차단)
- 직사광선 차단으로 실내 온도 상승 억제
- 눈부심 방지
- 추천 환경: 여름철, 남향 창문

### Hybrid (하이브리드)
- 시간대별 전략 자동 전환
- 계절 변화 자동 감지
- 최적의 실내 환경 유지

### Manual (수동)
- 자동 제어 비활성화
- 사용자가 직접 제어

## 생성되는 엔티티

### 센서 (Sensor)
- `sensor.{name}_sun_altitude`: 태양 고도각 (°)
- `sensor.{name}_sun_azimuth`: 태양 방위각 (°)
- `sensor.{name}_solar_intensity`: 태양광 상대 강도 (%)
- `sensor.{name}_recommended_position`: 추천 블라인드 위치 (%)
- `sensor.{name}_recommended_tilt`: 추천 슬랫 각도 (%)
  - 속성: `should_update` (동작 필요 여부)

### 바이너리 센서 (Binary Sensor)
- `binary_sensor.{name}_sun_facing`: 창문 직사광 여부

### 스위치 (Switch)
- `switch.{name}_manual_mode`: 수동 모드 토글

### 센서 속성 (Attributes)
모든 센서는 다음 속성을 포함합니다:
- `sunrise`: 일출 시각
- `sunset`: 일몰 시각
- `solar_noon`: 태양 정오
- `daylight_duration`: 일조 시간
- `current_strategy`: 현재 적용 전략
- `manual_override`: 수동 모드 활성화 여부
- `window_azimuth`: 창문 방향

## 자동화 예제

### 기본 블라인드 제어 자동화

```yaml
automation:
  - alias: "Solar Blind Adjuster - 자동 제어"
    trigger:
      - platform: state
        entity_id: sensor.living_room_recommended_position
      - platform: state
        entity_id: sensor.living_room_recommended_tilt
    condition:
      - condition: state
        entity_id: switch.living_room_manual_mode
        state: 'off'
    action:
      - service: cover.set_cover_position
        target:
          entity_id: cover.living_room_blind
        data:
          position: "{{ states('sensor.living_room_recommended_position') }}"
      - service: cover.set_cover_tilt_position
        target:
          entity_id: cover.living_room_blind
        data:
          tilt_position: "{{ states('sensor.living_room_recommended_tilt') }}"
```

### 직사광 감지 시 알림

```yaml
automation:
  - alias: "직사광 감지 알림"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_sun_facing
        to: 'on'
    action:
      - service: notify.mobile_app
        data:
          message: "거실에 직사광이 들어오고 있습니다."
```

### 실내 온도 기반 전략 변경

```yaml
automation:
  - alias: "온도 기반 전략 변경"
    trigger:
      - platform: numeric_state
        entity_id: sensor.living_room_temperature
        above: 26
    action:
      - service: solar_blind_adjuster.set_strategy
        target:
          entity_id: sensor.living_room_sun_altitude
        data:
          strategy: "block_light"
```

## 서비스

### solar_blind_adjuster.set_strategy
제어 전략을 변경합니다.

```yaml
service: solar_blind_adjuster.set_strategy
target:
  entity_id: sensor.living_room_sun_altitude
data:
  strategy: "block_light"
```

### solar_blind_adjuster.refresh_calculation
태양 데이터를 수동으로 다시 계산합니다.

```yaml
service: solar_blind_adjuster.refresh_calculation
target:
  entity_id: sensor.living_room_sun_altitude
```

### solar_blind_adjuster.record_blind_action
블라인드 동작을 수동으로 기록합니다.

```yaml
service: solar_blind_adjuster.record_blind_action
target:
  entity_id: sensor.living_room_sun_altitude
data:
  position: 75
  tilt: 60
```

### solar_blind_adjuster.run_simulation
특정 날짜/시간 구간에 대해 추천 값을 시뮬레이션합니다. 응답에 각 시각별 추천 position/tilt와 전략이 포함됩니다.

```yaml
service: solar_blind_adjuster.run_simulation
target:
  entity_id: sensor.living_room_sun_altitude
data:
  date: 2024-12-15
  start_time: "08:00"
  end_time: "12:00"
  interval_minutes: 30
```

### solar_blind_adjuster.preview_time
특정 날짜/시간을 기준으로 센서 값을 임시로 갱신해 미리보기 합니다. 다음 주기 업데이트 시 실제 시간으로 다시 계산됩니다.

```yaml
service: solar_blind_adjuster.preview_time
target:
  entity_id: sensor.living_room_sun_altitude
data:
  date: 2024-12-15
  time: "10:30"
```

## Lovelace 카드 예제

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Solar Blind Adjuster - 거실
    entities:
      - entity: sensor.living_room_sun_altitude
        name: 태양 고도각
      - entity: sensor.living_room_sun_azimuth
        name: 태양 방위각
      - entity: binary_sensor.living_room_sun_facing
        name: 직사광 여부
      - entity: sensor.living_room_solar_intensity
        name: 일조 강도

  - type: glance
    title: 추천 블라인드 상태
    entities:
      - entity: sensor.living_room_recommended_position
        name: 위치
      - entity: sensor.living_room_recommended_tilt
        name: 각도

  - type: entities
    title: 제어 설정
    entities:
      - entity: switch.living_room_manual_mode
        name: 수동 모드
```

## 트러블슈팅

### 블라인드가 움직이지 않아요
- 이 통합은 추천 값만 제공합니다. `cover.set_cover_position`/`cover.set_cover_tilt_position` 같은 자동화를 별도로 만들어야 실제 블라인드가 움직입니다.
- 수동 모드가 활성화되어 있는지 확인하세요
- `change_threshold` (변화 임계값)이 너무 높게 설정되어 있을 수 있습니다
- `min_action_interval` (최소 동작 간격)로 인해 대기 중일 수 있습니다

### 태양 위치가 정확하지 않아요
- 위도/경도 설정을 확인하세요
- 타임존이 올바르게 설정되어 있는지 확인하세요
- 고도 설정을 확인하세요

### 센서 값이 업데이트되지 않아요
- HomeAssistant 로그에서 오류 메시지를 확인하세요
- 통합을 재시작해보세요 (설정 > 기기 및 서비스 > Solar Blind Adjuster > 재시작)

## 기술 스택

- **천문 계산**: [astral](https://github.com/sffjunkie/astral) - 태양 위치 계산
- **시간대 처리**: Home Assistant `get_time_zone` 유틸 - 캐시된 타임존 지원
- **플랫폼**: HomeAssistant Custom Component

## 라이선스

MIT License

## 기여

이슈와 풀 리퀘스트는 언제나 환영합니다!

## 개발 로드맵

### Phase 2: 고급 기능 (계획 중)
- Hybrid 모드 스케줄 UI 설정
- 일출/일몰 자동화 UI 설정
- 날씨 서비스 연동 (구름 정보)
- 에너지 최적화 모드

### Phase 3: 최적화 (계획 중)
- 머신러닝 기반 사용자 패턴 학습
- 다중 블라인드 통합 제어
- 커스텀 Lovelace 카드

## 문의

- GitHub Issues: [여기에 이슈를 등록해주세요]
- 버그 리포트, 기능 요청 환영합니다!

---

**만든 이**: Solar Blind Adjuster Team
**버전**: 0.1.0
**최종 업데이트**: 2024-01
