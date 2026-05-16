# Build Notes - 사람이 만든 흔적 남기기

이 프로젝트는 단순히 “AI로 위성을 고른다”로 끝내지 않으려고 했습니다. 처음에는 `max_signal` baseline만 두면 충분해 보였는데, LEO 환경에서는 현재 신호가 좋아도 남은 가시 시간이 짧으면 바로 다시 핸드오버가 발생할 수 있습니다. 그래서 signal만 보는 기준과, load/visibility/stability를 보는 기준을 분리해서 비교했습니다.

## 내가 의도적으로 넣은 부분

- **temporal holdout split**: 랜덤 split 대신 뒤쪽 timestep을 테스트로 잡아, 미래 시점 의사결정에 가까운 평가 형태를 만들었습니다.
- **oracle utility**: 실제 정답 데이터가 없기 때문에, 왜 선택됐는지 설명 가능한 utility로 label을 만들었습니다.
- **baseline 여러 개**: `max_signal`, `sticky_signal`, `visibility_guard`, `load_aware`, `stability_aware`, `ai_ranker`를 같은 metric으로 비교했습니다.
- **설명 JSON**: `/explain` endpoint와 `scripts/05_explain_epoch.py`를 넣어서 선택 결과가 블랙박스처럼 보이지 않게 했습니다.
- **경고문 명시**: 데이터가 시범용 synthetic data이고 실제 산업 적용 결과가 아니라는 점을 README, Data Card, Report, API response에 반복해서 표시했습니다.

## 아쉬운 점도 숨기지 않기

- 궤도는 TLE/SGP4가 아니라 간단한 circular orbit입니다.
- RSRP는 실제 link budget이 아니라 RSRP-like proxy입니다.
- gateway, beam, spectrum, weather, inter-satellite link 제약은 넣지 않았습니다.
- 모델이 맞춘 것은 실제 운영 정답이 아니라 제가 정의한 oracle utility입니다.

이 한계를 명확히 적어두는 편이 오히려 포트폴리오에서 신뢰도가 높습니다. “상용망에 적용했다”처럼 보이게 만들면 안 되고, “실제 적용 전 어떤 검증이 추가되어야 하는지 알고 있다”는 방향으로 설명하는 것이 안전합니다.
