# 포트폴리오 업로드 / 발표 가이드

## 30초 설명

“LEO 위성은 빠르게 움직이기 때문에 단말이 볼 수 있는 위성 후보가 계속 바뀝니다. 저는 이 문제를 후보 위성 ranking 문제로 바꿔서, 현재 신호뿐 아니라 남은 가시 시간, 위성 부하, 불필요한 핸드오버 비용까지 함께 고려하는 AI ranker를 구현했습니다. 실제 통신망 데이터는 사용할 수 없어서 공개용 synthetic simulator로 데이터를 만들었고, 여러 baseline과 비교한 뒤 FastAPI endpoint와 테스트까지 붙여 포트폴리오 형태로 정리했습니다.”

## 꼭 먼저 말할 것

이 프로젝트는 실제 산업 적용 결과가 아닙니다. 데이터는 시범용 fake/synthetic data이고, metric은 실제 상용망 성능이 아니라 공개용 simulator에서의 재현 가능한 benchmark입니다.

## GitHub 업로드 순서

자세한 명령어는 `docs/GITHUB_PUSH_GUIDE_KO.md`를 참고합니다.

1. GitHub에서 `leo-handover-ai-optimizer` 이름으로 새 repository 생성
2. ZIP 압축 해제
3. 로컬에서 `PYTHONPATH=src bash scripts/run_full_pipeline.sh` 실행 확인
4. `git init`, `git add .`, `git commit`, `git remote add origin`, `git push -u origin main`
5. GitHub Pages 사용 시 Settings → Pages → Deploy from branch → main → root 선택

## 면접 질문 대비

**왜 max signal만으로 충분하지 않은가?**  
현재 신호가 강해도 곧 시야에서 사라질 수 있어 재핸드오버가 늘어날 수 있습니다. 그래서 remaining visibility와 handover penalty를 feature와 oracle에 반영했습니다.

**왜 synthetic data를 사용했는가?**  
실제 위성/통신 운영 데이터는 공개하기 어렵고 민감할 수 있습니다. 공개 저장소에서는 재현 가능한 simulator로 문제 정의, feature engineering, 모델링, 평가 구조를 보여주는 것이 안전합니다.

**실제 서비스에 들어가려면 무엇이 더 필요한가?**  
TLE/SGP4 기반 궤도, 실제 link budget, gateway/beam/backhaul 제약, traffic trace, fail-safe policy, latency budget, drift monitoring, 실데이터 검증이 필요합니다.

## 이 프로젝트에서 강조하면 좋은 포인트

- 통신 도메인 문제를 ML ranking 문제로 재정의한 점
- baseline을 여러 개 두고 trade-off를 비교한 점
- synthetic data 경고와 production gap을 숨기지 않은 점
- API, explanation, tests, GitHub Actions, Pages까지 end-to-end로 구성한 점
