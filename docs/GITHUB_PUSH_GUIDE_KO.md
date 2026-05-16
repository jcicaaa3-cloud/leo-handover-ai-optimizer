# GitHub 업로드 가이드

추천 repository 이름: `leo-handover-ai-optimizer`

## 1. GitHub에서 새 repository 만들기

1. GitHub 로그인
2. 우측 상단 `+` 버튼 → `New repository`
3. Repository name: `leo-handover-ai-optimizer`
4. Public 선택
5. **README, .gitignore, license는 GitHub에서 새로 만들지 말기**  
   이미 ZIP 안에 포함되어 있어서 중복될 수 있습니다.
6. `Create repository` 클릭

## 2. ZIP 압축 풀기

```bash
cd ~/Downloads
unzip leo-handover-ai-optimizer-upgraded-github.zip
cd leo-handover-ai-optimizer
```

## 3. 로컬에서 실행 확인

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=src bash scripts/run_full_pipeline.sh
```

## 4. Git 초기화 후 첫 커밋

```bash
git init
git branch -M main
git add .
git commit -m "Add LEO satellite handover AI optimizer portfolio"
```

## 5. 원격 저장소 연결 및 push

아래에서 `<YOUR_GITHUB_USERNAME>`만 본인 GitHub 아이디로 바꾸면 됩니다.

```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/leo-handover-ai-optimizer.git
git push -u origin main
```

## 6. GitHub Pages 켜기

1. Repository → `Settings`
2. 왼쪽 메뉴 `Pages`
3. Source: `Deploy from a branch`
4. Branch: `main`, Folder: `/ (root)`
5. Save

조금 기다리면 아래 형태의 페이지가 열립니다.

```text
https://<YOUR_GITHUB_USERNAME>.github.io/leo-handover-ai-optimizer/
```

## 7. 업로드 후 확인할 것

- README 상단 warning이 보이는지
- `DISCLAIMER.md`, `DATA_NOTICE.md`, `docs/DATA_CARD.md`가 올라갔는지
- `docs/assets/` 이미지가 README에서 잘 보이는지
- Actions 탭에서 test가 통과하는지
- GitHub Pages에서 `index.html`이 열리는지
