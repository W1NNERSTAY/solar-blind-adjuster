# 로컬 테스트 가이드

GitHub Release 전에 Solar Blind Adjuster를 로컬 HomeAssistant 환경에서 테스트하는 방법을 안내합니다.

## 방법 1: 로컬 HomeAssistant에 직접 복사 (권장)

### 1. HomeAssistant 설정 디렉토리 찾기

HomeAssistant 설정 디렉토리는 설치 방법에 따라 다릅니다:

- **Home Assistant OS / Supervised**: `/config`
- **Home Assistant Container**: Docker 볼륨 마운트 경로
- **Home Assistant Core (venv)**: `~/.homeassistant` 또는 설정한 경로

### 2. 통합 복사

```bash
# HomeAssistant 설정 디렉토리로 이동 (예시)
cd /config  # 또는 ~/.homeassistant

# custom_components 디렉토리 생성 (없으면)
mkdir -p custom_components

# Solar Blind Adjuster 복사
cp -r /Users/ohilseung/Workspace/Projects/_toy/solar_blind_adjuster/custom_components/solar_blind_adjuster custom_components/

# 복사 확인
ls -la custom_components/solar_blind_adjuster/
```

### 3. HomeAssistant 재시작

UI 또는 CLI에서 재시작:

```bash
# CLI 재시작 (Container의 경우)
docker restart homeassistant

# 또는 UI에서: 설정 > 시스템 > 재시작
```

### 4. 통합 추가 및 테스트

1. **설정** > **기기 및 서비스** > **통합** 이동
2. **+ 통합 추가** 클릭
3. "Solar Blind Adjuster" 검색
4. 설정 마법사 진행

## 방법 2: 개발 환경 심볼릭 링크 (개발 중 빠른 테스트)

심볼릭 링크를 사용하면 코드 수정 시마다 복사할 필요가 없습니다.

```bash
# HomeAssistant custom_components 디렉토리로 이동
cd /config/custom_components  # 또는 ~/.homeassistant/custom_components

# 심볼릭 링크 생성
ln -s /Users/ohilseung/Workspace/Projects/_toy/solar_blind_adjuster/custom_components/solar_blind_adjuster solar_blind_adjuster

# 확인
ls -la
```

코드 수정 후 HomeAssistant만 재시작하면 변경사항이 적용됩니다.

## 방법 3: Docker Compose로 테스트 환경 구축

독립적인 테스트 환경을 만들 수 있습니다.

### docker-compose.yml 생성

```yaml
version: '3'
services:
  homeassistant:
    container_name: ha-test
    image: homeassistant/home-assistant:latest
    volumes:
      - ./test-config:/config
      - ./custom_components/solar_blind_adjuster:/config/custom_components/solar_blind_adjuster
    environment:
      - TZ=Asia/Seoul
    ports:
      - "8123:8123"
    restart: unless-stopped
```

### 테스트 설정 초기화

```bash
# 프로젝트 루트에서
mkdir -p test-config
cd test-config

# 기본 설정 파일 생성
cat > configuration.yaml << 'EOF'
# Test configuration for Solar Blind Adjuster
default_config:

# 테스트용 더미 블라인드
cover:
  - platform: template
    covers:
      test_blind:
        friendly_name: "Test Blind"
        position_template: "{{ states('input_number.blind_position') | int }}"
        tilt_template: "{{ states('input_number.blind_tilt') | int }}"
        open_cover:
          service: input_number.set_value
          target:
            entity_id: input_number.blind_position
          data:
            value: 100
        close_cover:
          service: input_number.set_value
          target:
            entity_id: input_number.blind_position
          data:
            value: 0
        set_cover_position:
          service: input_number.set_value
          target:
            entity_id: input_number.blind_position
          data:
            value: "{{ position }}"
        set_cover_tilt_position:
          service: input_number.set_value
          target:
            entity_id: input_number.blind_tilt
          data:
            value: "{{ tilt }}"

input_number:
  blind_position:
    name: Blind Position
    min: 0
    max: 100
    step: 1
    initial: 50
  blind_tilt:
    name: Blind Tilt
    min: 0
    max: 100
    step: 1
    initial: 50

logger:
  default: info
  logs:
    custom_components.solar_blind_adjuster: debug
EOF
```

### Docker 실행

```bash
# 프로젝트 루트로 돌아가기
cd ..

# Docker Compose 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f homeassistant
```

브라우저에서 `http://localhost:8123` 접속하여 테스트합니다.

## 테스트 체크리스트

### 1. 기본 기능 테스트

- [ ] 통합 추가 시 config flow 4단계가 정상 작동
- [ ] 블라인드 엔티티 선택 및 검증
- [ ] 위도/경도 입력 및 검증 (범위 체크)
- [ ] 창문 방향 입력 및 검증 (0-360)
- [ ] 전략 선택 (Maximize Light, Block Light, Hybrid, Manual)
- [ ] 고급 설정 옵션 (생략 가능)

### 2. 엔티티 생성 확인

통합 추가 후 다음 엔티티들이 생성되는지 확인:

```bash
# 개발자 도구 > 상태에서 확인
sensor.{name}_sun_altitude
sensor.{name}_sun_azimuth
sensor.{name}_solar_intensity
sensor.{name}_recommended_position
sensor.{name}_recommended_tilt
binary_sensor.{name}_sun_facing
switch.{name}_manual_mode
```

### 3. 센서 값 확인

- [ ] 태양 고도각이 시간에 따라 변하는지 (낮: 양수, 밤: 음수)
- [ ] 태양 방위각이 0-360 범위인지
- [ ] 일조 강도가 태양 고도에 따라 변하는지
- [ ] 추천 위치/각도가 0-100 범위인지
- [ ] 직사광 여부가 창문 방향과 태양 위치에 따라 변하는지

### 4. 속성(Attributes) 확인

각 센서의 속성에서 다음 정보 확인:

```yaml
sunrise: "2024-01-15T07:30:00+09:00"
sunset: "2024-01-15T17:45:00+09:00"
solar_noon: "2024-01-15T12:37:00+09:00"
daylight_duration: "10:15:00"
current_strategy: "maximize_light"
manual_override: false
window_azimuth: 180
```

### 5. 전략별 동작 테스트

#### Maximize Light 전략

- [ ] 태양이 뜬 시간에 블라인드가 완전히 열림 (position: 100)
- [ ] 슬랫 각도가 태양광을 최대한 받도록 조정됨

#### Block Light 전략

- [ ] 직사광이 들어올 때 부분적으로 닫힘
- [ ] 직사광이 없을 때 완전히 열림

#### Manual 전략

- [ ] 수동 모드 스위치가 켜지면 추천 값이 변하지 않음
- [ ] 마지막 추천 값이 유지됨

### 6. 서비스 테스트

#### set_strategy 서비스

```yaml
service: solar_blind_adjuster.set_strategy
target:
  entity_id: sensor.test_sun_altitude
data:
  strategy: "block_light"
```

- [ ] 전략 변경 후 센서의 `current_strategy` 속성이 업데이트됨
- [ ] 추천 값이 새 전략에 맞게 변경됨

#### refresh_calculation 서비스

```yaml
service: solar_blind_adjuster.refresh_calculation
target:
  entity_id: sensor.test_sun_altitude
```

- [ ] 호출 후 모든 센서 값이 즉시 업데이트됨

#### record_blind_action 서비스

```yaml
service: solar_blind_adjuster.record_blind_action
target:
  entity_id: sensor.test_sun_altitude
data:
  position: 75
  tilt: 60
```

- [ ] 마지막 동작 시간이 기록됨
- [ ] `min_action_interval` 동안 새 추천이 억제됨

### 7. 자동화 테스트

README의 예제 자동화를 추가하고 테스트:

```yaml
automation:
  - alias: "Solar Blind Adjuster Test"
    trigger:
      - platform: state
        entity_id: sensor.test_recommended_position
    action:
      - service: system_log.write
        data:
          message: "Recommended position changed to {{ trigger.to_state.state }}"
          level: info
```

- [ ] 센서 값 변경 시 자동화가 트리거됨
- [ ] 로그에 메시지가 기록됨

### 8. 에러 처리 테스트

의도적으로 잘못된 값 입력:

- [ ] 존재하지 않는 블라인드 엔티티 → 오류 메시지 표시
- [ ] 위도 범위 초과 (-90~90) → 검증 오류
- [ ] 경도 범위 초과 (-180~180) → 검증 오류
- [ ] 창문 방향 범위 초과 (0-360) → 검증 오류

### 9. 로그 확인

HomeAssistant 로그에서 오류가 없는지 확인:

```bash
# 로그 확인 (Docker의 경우)
docker logs homeassistant | grep solar_blind_adjuster

# 또는 UI에서: 설정 > 시스템 > 로그
```

다음과 같은 로그를 찾습니다:

```
[custom_components.solar_blind_adjuster] Successfully initialized Solar Blind Adjuster
[custom_components.solar_blind_adjuster] Coordinator updated: sun_altitude=45.2, sun_azimuth=180.5
```

### 10. 다국어 테스트

- [ ] 한국어 UI에서 모든 텍스트가 한국어로 표시
- [ ] 영어 UI에서 모든 텍스트가 영어로 표시
- [ ] 오류 메시지도 언어에 맞게 표시

### 11. 옵션 수정 테스트

- [ ] 통합 설정에서 **옵션 구성** 클릭
- [ ] 전략 변경
- [ ] 변경 사항이 즉시 적용됨

### 12. 재시작 테스트

- [ ] HomeAssistant 재시작 후 통합이 정상 로드됨
- [ ] 이전 설정이 유지됨
- [ ] 센서 값이 정상적으로 업데이트됨

### 13. 제거 테스트

- [ ] 통합 제거 시 모든 엔티티가 삭제됨
- [ ] 오류 없이 깔끔하게 제거됨
- [ ] 재추가 시 정상 작동

## 디버깅 팁

### 로그 레벨 증가

`configuration.yaml`에 추가:

```yaml
logger:
  default: warning
  logs:
    custom_components.solar_blind_adjuster: debug
```

### Python 디버거 사용

코드에 브레이크포인트 추가:

```python
import pdb; pdb.set_trace()
```

### VSCode Remote Debugging

1. HomeAssistant에 `debugpy` 설치
2. VSCode의 Remote Debugging 설정
3. 브레이크포인트 설정 후 디버깅

## 시간대별 테스트

태양 위치는 시간에 따라 변하므로 다음 시간대에 테스트:

- [ ] 일출 전 (고도각 음수)
- [ ] 일출 직후 (고도각 0-10도)
- [ ] 오전 (고도각 증가)
- [ ] 정오 (최대 고도각)
- [ ] 오후 (고도각 감소)
- [ ] 일몰 직전 (고도각 0-10도)
- [ ] 일몰 후 (고도각 음수)

### 시간 시뮬레이션 (선택 사항)

빠른 테스트를 위해 코드를 임시로 수정:

```python
# solar_calculator.py의 get_sun_position에서
# 현재 시간 대신 특정 시간 사용
from datetime import datetime
test_time = datetime(2024, 6, 21, 12, 0, 0)  # 하지 정오
# now = datetime.now(pytz.timezone(self.timezone))
now = test_time  # 테스트용
```

## 성능 테스트

- [ ] CPU 사용률이 과도하지 않은지 (업데이트 주기 확인)
- [ ] 메모리 누수가 없는지 (장시간 실행)
- [ ] 업데이트 빈도가 적절한지 (동적 주기 확인)

## 다음 단계

모든 테스트가 통과하면:

1. ✅ 코드 품질 확인 완료
2. ✅ 기능 동작 확인 완료
3. 📝 발견된 버그 수정
4. 🚀 GitHub에 커밋 및 Release 생성

## 일반적인 문제와 해결

### 통합이 목록에 나타나지 않음

- `manifest.json`의 `domain`이 디렉토리명과 일치하는지 확인
- HomeAssistant 재시작
- 로그에서 Import 오류 확인

### 센서 값이 `unknown`

- 좌표가 올바르게 설정되었는지 확인
- `astral` 라이브러리가 설치되었는지 확인
- 로그에서 계산 오류 확인

### 블라인드가 움직이지 않음

- 자동화가 설정되어 있는지 확인 (통합은 추천만 제공)
- 수동 모드가 꺼져 있는지 확인
- `change_threshold`가 너무 높지 않은지 확인

## 참고

- [HomeAssistant 개발자 문서](https://developers.home-assistant.io/)
- [통합 테스트 가이드](https://developers.home-assistant.io/docs/development_testing)
- [Custom Component 튜토리얼](https://developers.home-assistant.io/docs/creating_component_index)
