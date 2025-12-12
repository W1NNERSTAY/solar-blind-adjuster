# GitHub Actions 릴리스 가이드

이 문서는 GitHub Actions를 사용하여 Solar Blind Adjuster의 릴리스를 자동화하는 방법을 설명합니다.

## 워크플로우 개요

### 1. Release Workflow (`.github/workflows/release.yml`)

**트리거**: `v*.*.*` 형식의 태그 푸시 시 자동 실행

**수행 작업**:
- 태그에서 버전 추출
- manifest.json의 버전과 태그 버전 일치 확인
- 변경 이력(CHANGELOG) 자동 생성
- 통합 파일을 ZIP으로 압축 (`solar_blind_adjuster.zip`)
- GitHub Release 자동 생성
- ZIP 파일을 릴리스에 첨부

### 2. Validate Workflow (`.github/workflows/validate.yml`)

**트리거**: `main` 또는 `develop` 브랜치에 푸시 또는 PR 생성 시

**수행 작업**:
- Python 의존성 설치
- manifest.json 유효성 검증
- hacs.json 유효성 검증
- 필수 파일 존재 확인
- Python 문법 검증
- 번역 파일 유효성 검증
- HACS 공식 검증

## 릴리스 프로세스

### 1단계: 코드 준비

```bash
# 최신 코드가 main 브랜치에 있는지 확인
git checkout main
git pull origin main

# 모든 변경사항 커밋
git add .
git commit -m "Prepare for release v0.1.0"
git push origin main
```

### 2단계: 버전 업데이트

`custom_components/solar_blind_adjuster/manifest.json` 파일의 버전 업데이트:

```json
{
  "version": "0.1.0"
}
```

### 3단계: 태그 생성 및 푸시

```bash
# 버전 태그 생성 (반드시 v 접두사 사용)
git tag v0.1.0

# 태그를 원격 저장소에 푸시
git push origin v0.1.0
```

이제 GitHub Actions가 자동으로:
1. ✅ 버전 검증
2. ✅ CHANGELOG 생성
3. ✅ ZIP 파일 생성
4. ✅ GitHub Release 생성
5. ✅ 릴리스에 ZIP 첨부

### 4단계: 릴리스 확인

1. GitHub 저장소 페이지 이동
2. **Releases** 탭 클릭
3. 새 릴리스가 생성되었는지 확인
4. ZIP 파일이 첨부되었는지 확인

## 릴리스 타입별 가이드

### 패치 릴리스 (버그 수정)

버전: `0.1.0` → `0.1.1`

```bash
# manifest.json 버전 업데이트
# "version": "0.1.1"

git add custom_components/solar_blind_adjuster/manifest.json
git commit -m "Bump version to 0.1.1"
git push origin main

git tag v0.1.1
git push origin v0.1.1
```

### 마이너 릴리스 (새 기능)

버전: `0.1.1` → `0.2.0`

```bash
# manifest.json 버전 업데이트
# "version": "0.2.0"

git add custom_components/solar_blind_adjuster/manifest.json
git commit -m "Bump version to 0.2.0 - Add new features"
git push origin main

git tag v0.2.0
git push origin v0.2.0
```

### 메이저 릴리스 (큰 변경사항)

버전: `0.2.0` → `1.0.0`

```bash
# manifest.json 버전 업데이트
# "version": "1.0.0"

git add custom_components/solar_blind_adjuster/manifest.json
git commit -m "Bump version to 1.0.0 - Major release"
git push origin main

git tag v1.0.0
git push origin v1.0.0
```

## 릴리스 수정하기

이미 생성된 릴리스를 수정해야 하는 경우:

### 방법 1: GitHub UI에서 수정

1. GitHub 저장소의 **Releases** 페이지 이동
2. 수정할 릴리스의 **Edit** 버튼 클릭
3. 제목, 설명, 파일 수정
4. **Update release** 클릭

### 방법 2: 태그 삭제 후 재생성

```bash
# 로컬 태그 삭제
git tag -d v0.1.0

# 원격 태그 삭제
git push origin :refs/tags/v0.1.0

# GitHub에서 릴리스 수동 삭제

# 코드 수정 후 다시 태그 생성
git tag v0.1.0
git push origin v0.1.0
```

## 워크플로우 실행 확인

### 1. Actions 탭에서 확인

1. GitHub 저장소의 **Actions** 탭 클릭
2. 워크플로우 실행 목록 확인
3. 실행 중인 워크플로우 클릭하여 상세 로그 확인

### 2. 실패 시 대응

워크플로우가 실패하면:

```bash
# 로그에서 오류 확인
# 문제 수정 후

# 태그 삭제 (이미 푸시된 경우)
git push origin :refs/tags/v0.1.0
git tag -d v0.1.0

# 다시 태그 생성
git tag v0.1.0
git push origin v0.1.0
```

## 검증 워크플로우 활용

Pull Request 생성 시 자동으로 검증이 실행됩니다:

```bash
# feature 브랜치 생성
git checkout -b feature/new-strategy

# 코드 수정
# ...

# 커밋 및 푸시
git add .
git commit -m "Add new strategy"
git push origin feature/new-strategy

# GitHub에서 PR 생성
# → Validate 워크플로우 자동 실행
# → 모든 검증 통과 시 Merge 가능
```

## 로컬에서 수동 릴리스 (워크플로우 없이)

GitHub Actions 없이 수동으로 릴리스하는 방법:

```bash
# 1. ZIP 파일 생성
cd custom_components
zip -r ../solar_blind_adjuster.zip solar_blind_adjuster/
cd ..

# 2. GitHub에서 수동으로 Release 생성
# - GitHub 저장소 > Releases > Create a new release
# - Tag: v0.1.0
# - Title: Release v0.1.0
# - Description: 릴리스 노트 작성
# - Attach files: solar_blind_adjuster.zip 업로드
# - Publish release 클릭
```

## 릴리스 체크리스트

릴리스 전 확인사항:

- [ ] 모든 테스트 통과 (TESTING.md 참조)
- [ ] manifest.json의 version 업데이트
- [ ] README.md 업데이트 (변경사항 있는 경우)
- [ ] CHANGELOG 작성 (선택 사항, GitHub Actions가 자동 생성)
- [ ] 모든 변경사항 커밋 및 푸시
- [ ] main 브랜치에 merge 완료
- [ ] 태그 생성 및 푸시
- [ ] GitHub Actions 실행 성공 확인
- [ ] 릴리스 페이지에서 내용 확인
- [ ] ZIP 파일 다운로드하여 수동 설치 테스트

## 버전 관리 전략

Semantic Versioning (SemVer) 사용:

- **MAJOR** (1.0.0): 하위 호환성이 깨지는 변경
- **MINOR** (0.1.0): 하위 호환성을 유지하는 기능 추가
- **PATCH** (0.0.1): 하위 호환성을 유지하는 버그 수정

예시:
- `0.1.0` → 초기 릴리스
- `0.1.1` → 버그 수정
- `0.2.0` → 새 기능 추가 (Hybrid 모드 스케줄 UI)
- `1.0.0` → 안정 버전, API 변경

## 릴리스 노트 작성 팁

자동 생성된 CHANGELOG를 수정하려면:

1. 릴리스 생성 후 **Edit** 클릭
2. 다음 섹션 포함:
   ```markdown
   ## 🎉 주요 변경사항
   - 새 기능 A 추가
   - 버그 B 수정

   ## 🔧 기술적 변경
   - 내부 구조 개선

   ## 📝 알려진 이슈
   - 이슈 C (다음 릴리스에서 수정 예정)

   ## 📦 설치 방법
   [자동 생성된 내용 유지]
   ```

## 문제 해결

### 태그와 manifest.json 버전 불일치

**오류**: "Version mismatch! manifest.json has X but tag is vY"

**해결**:
```bash
# manifest.json 버전 수정
# "version": "Y"

git add custom_components/solar_blind_adjuster/manifest.json
git commit -m "Fix version in manifest.json"
git push origin main

# 태그 삭제 후 재생성
git push origin :refs/tags/vY
git tag vY
git push origin vY
```

### 워크플로우 권한 오류

**오류**: "Resource not accessible by integration"

**해결**:
1. GitHub 저장소 > Settings > Actions > General
2. "Workflow permissions" 섹션에서 "Read and write permissions" 선택
3. Save

### ZIP 파일 생성 실패

**해결**:
```bash
# 로컬에서 ZIP 생성 테스트
cd custom_components
zip -r ../solar_blind_adjuster.zip solar_blind_adjuster/

# 내용 확인
unzip -l ../solar_blind_adjuster.zip
```

## 참고 자료

- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [GitHub Releases 가이드](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Semantic Versioning](https://semver.org/)
- [HACS 릴리스 요구사항](https://hacs.xyz/docs/publish/start)
