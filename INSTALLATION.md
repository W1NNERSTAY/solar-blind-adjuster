# GitHub 저장소 설정 가이드

이 문서는 Solar Blind Adjuster를 HACS를 통해 배포하기 위한 GitHub 저장소 설정 방법을 안내합니다.

## 필수 파일 체크리스트

다음 파일들이 저장소 루트에 있어야 합니다:

- [x] `hacs.json` - HACS 통합 메타데이터
- [x] `README.md` - 프로젝트 설명 및 설치 가이드
- [x] `custom_components/solar_blind_adjuster/` - 통합 코드
- [x] `custom_components/solar_blind_adjuster/manifest.json` - HomeAssistant 매니페스트

## GitHub 저장소 설정 단계

### 1. GitHub 저장소 생성

```bash
# GitHub에서 새 저장소 생성 (solar-blind-adjuster)
# 저장소를 Public으로 설정해야 HACS에서 접근 가능합니다

# 로컬에서 git 초기화 (아직 안했다면)
cd /Users/ohilseung/Workspace/Projects/_toy/solar_blind_adjuster
git init
git add .
git commit -m "Initial commit: Solar Blind Adjuster v0.1.0"
git branch -M main
git remote add origin https://github.com/W1NNERSTAY/solar-blind-adjuster.git
git push -u origin main
```

### 2. GitHub Release 생성

HACS는 GitHub Releases를 통해 버전을 관리합니다.

1. GitHub 저장소 페이지에서 **Releases** 클릭
2. **Create a new release** 클릭
3. 태그 생성: `v0.1.0` (반드시 v 접두사 사용)
4. Release title: `v0.1.0 - Initial Release`
5. 설명 작성:
   ```markdown
   ## 첫 번째 릴리스

   ### 주요 기능
   - 태양 위치 기반 블라인드 자동 제어
   - 4가지 제어 전략 (Maximize Light, Block Light, Hybrid, Manual)
   - UI 기반 설정 마법사
   - 5개 센서 + 1개 바이너리 센서 + 1개 스위치
   - 한국어/영어 지원

   ### 설치 방법
   [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=W1NNERSTAY&repository=solar-blind-adjuster&category=integration)
   ```
6. **Publish release** 클릭

### 3. HACS에 등록 (선택 사항)

#### 방법 1: 사용자가 직접 커스텀 저장소로 추가

사용자가 HACS에서 다음 단계로 추가할 수 있습니다:
1. HACS > 통합 > 우측 상단 메뉴 (점 3개) > Custom repositories
2. Repository: `https://github.com/W1NNERSTAY/solar-blind-adjuster`
3. Category: Integration
4. 추가 후 검색하여 설치

#### 방법 2: HACS 기본 저장소에 등록 (공식 등록)

공식 HACS 저장소에 등록하려면:

1. [HACS 저장소](https://github.com/hacs/default)로 이동
2. Fork 생성
3. `integration` 파일 수정하여 저장소 URL 추가:
   ```json
   {
     "name": "Solar Blind Adjuster",
     "domain": "solar_blind_adjuster",
     "owner": "W1NNERSTAY",
     "repository": "solar-blind-adjuster",
     "category": "integration",
     "description": "태양 위치 기반 블라인드 자동 제어"
   }
   ```
4. Pull Request 생성
5. HACS 팀의 승인 대기 (몇 일 소요 가능)

**참고**: HACS 기본 저장소 등록을 위해서는 최소 1개의 릴리스가 필요하며,
저장소가 일정 기준을 충족해야 합니다 (README, hacs.json, 활성 유지 등).

### 4. GitHub Topics 추가

저장소 검색을 쉽게 하기 위해 Topics를 추가하세요:

1. GitHub 저장소 페이지에서 **About** 톱니바퀴 클릭
2. Topics 추가:
   - `home-assistant`
   - `home-assistant-component`
   - `home-assistant-integration`
   - `hacs`
   - `blind-control`
   - `solar-tracker`
   - `smart-home`

### 5. README.md 배지 확인

README.md의 버튼 링크가 올바른지 확인:
- 현재: `owner=W1NNERSTAY&repository=solar-blind-adjuster`
- 실제 GitHub 사용자명과 저장소명으로 변경되었는지 확인

### 6. 라이선스 파일 추가 (권장)

```bash
# MIT License 파일 생성
cat > LICENSE << 'EOF'
MIT License

Copyright (c) 2024 W1NNERSTAY

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

## 테스트

### HACS 커스텀 저장소로 테스트

1. HomeAssistant 인스턴스에서 HACS 설치
2. HACS > 통합 > 메뉴 > Custom repositories
3. 저장소 URL 입력: `https://github.com/W1NNERSTAY/solar-blind-adjuster`
4. Category: Integration
5. 추가 후 "Solar Blind Adjuster" 검색
6. 설치 및 HomeAssistant 재시작
7. 통합 추가 테스트

## 버전 업데이트 방법

새 버전을 릴리스할 때:

1. `custom_components/solar_blind_adjuster/manifest.json`의 `version` 업데이트
2. 코드 변경 사항 커밋
3. GitHub에서 새 Release 생성 (예: `v0.2.0`)
4. Release 노트에 변경 사항 작성
5. HACS가 자동으로 새 버전을 감지하여 사용자에게 업데이트 알림

## 문제 해결

### HACS에서 저장소가 검색되지 않음
- 저장소가 Public인지 확인
- `hacs.json` 파일이 루트에 있는지 확인
- 최소 1개의 Release가 있는지 확인

### 원클릭 버튼이 작동하지 않음
- URL의 owner와 repository 이름이 정확한지 확인
- 사용자가 HomeAssistant에 로그인되어 있는지 확인
- HACS가 설치되어 있는지 확인

### 설치 후 통합이 나타나지 않음
- HomeAssistant를 재시작했는지 확인
- `custom_components/solar_blind_adjuster` 디렉토리 구조가 올바른지 확인
- HomeAssistant 로그에서 오류 확인

## 참고 자료

- [HACS 문서](https://hacs.xyz/)
- [HACS Integration 등록 가이드](https://hacs.xyz/docs/publish/start)
- [HomeAssistant 개발자 문서](https://developers.home-assistant.io/)
- [My Home Assistant 서비스](https://my.home-assistant.io/faq/)
