# GitHub 업로드용 안내

이 ZIP은 `leo-handover-ai-optimizer` 저장소에 바로 업로드할 수 있도록 정리한 포트폴리오 버전입니다.

## 이번 버전에서 강화한 점

- README 상단에 synthetic/fake data 경고문 추가
- `DISCLAIMER.md`, `DATA_NOTICE.md`, `docs/DATA_CARD.md` 추가
- 실제 산업 적용이 아니라는 내용을 `docs/PRODUCTION_GAP_KO.md`에 분리
- `/explain` API와 `scripts/05_explain_epoch.py` 추가
- `visibility_guard`, `stability_aware` baseline 추가
- `handover_rate`, `low_margin_rate`, `oracle_regret` 등 평가 metric 보강
- `docs/RUN_REPORT.md`와 `risk_tradeoff.png` 추가
- 사람이 설명한 느낌이 나도록 `docs/BUILD_NOTES_KO.md` 추가

## 추천 repository 이름

`leo-handover-ai-optimizer`

## 업로드 후 바로 확인할 것

- `README.md`가 GitHub 메인 화면에 보이는지 확인
- README 상단 warning이 보이는지 확인
- `DISCLAIMER.md`, `DATA_NOTICE.md`, `docs/DATA_CARD.md`가 있는지 확인
- `docs/assets/readme_hero.png`, `risk_tradeoff.png` 이미지가 README에 표시되는지 확인
- GitHub Pages를 사용할 경우 `index.html`이 정상 표시되는지 확인

## 로컬 실행

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=src bash scripts/run_full_pipeline.sh
```

## 공개 저장소 버전의 데이터 정책

실제 위성/통신 운영 로그 대신 synthetic simulation을 사용했습니다. 공개 저장소에 민감 데이터가 들어가지 않도록 하기 위한 선택입니다. 따라서 결과 metric은 실제 산업 성능이 아니라, 포트폴리오용 재현 가능한 실험 결과로만 해석해야 합니다.

상세 업로드 명령어는 `docs/GITHUB_PUSH_GUIDE_KO.md`를 보면 됩니다.
