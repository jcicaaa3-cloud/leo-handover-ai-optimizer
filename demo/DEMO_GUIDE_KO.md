# Demo Guide

> ⚠️ `demo/`의 샘플도 실제 위성망 데이터가 아니라 synthetic simulator에서 뽑은 시범용 예시입니다.

## 1. 샘플 후보 링크 확인

`demo/sample_candidates.csv`는 한 decision epoch에서 단말이 평가하는 후보 위성 링크 예시입니다. 실제 telemetry가 아니라 공개용 fake/synthetic data입니다.

## 2. API 예시 요청

`demo/demo_request.json`을 사용해 `/score` endpoint에 요청할 수 있습니다.

```bash
PYTHONPATH=src uvicorn leo_handover.api:app --reload
curl -X POST http://127.0.0.1:8000/score \
  -H "Content-Type: application/json" \
  --data @demo/demo_request.json
```

## 3. 설명 endpoint

```bash
curl -X POST http://127.0.0.1:8000/explain \
  -H "Content-Type: application/json" \
  --data @demo/demo_request.json
```

모델 artifact가 있으면 AI ranker가 사용되고, 아직 학습하지 않았다면 fallback load-aware scoring이 사용됩니다. 두 경우 모두 실제 산업 적용 결과가 아니라 demo contract입니다.
