# 프로젝트 카드 - LEO Satellite Handover AI Optimizer

## 한 줄 소개

빠르게 이동하는 LEO 위성 네트워크에서 사용자 단말이 어떤 위성으로 연결을 유지하거나 전환할지 결정하기 위한 AI 기반 핸드오버 ranking 프로토타입입니다.

## 중요 경고

이 프로젝트는 공개 포트폴리오용 synthetic/fake data 기반 실험입니다. 실제 위성망에 적용된 시스템이 아니며, 실제 산업 성능을 검증한 결과가 아닙니다.

## 문제 정의

LEO 위성은 지상 단말 대비 빠르게 이동하기 때문에 가시 위성, 신호 품질, 남은 가시 시간, 위성 부하가 짧은 시간 안에 계속 변합니다. 단순히 현재 신호가 가장 강한 위성을 고르면 곧바로 다시 핸드오버가 필요해질 수 있습니다.

## 접근 방식

1. 공개 가능한 synthetic LEO 후보 링크 시뮬레이터를 구성했습니다.
2. elevation, distance, RSRP-like signal, satellite load, remaining visibility, handover cost 등의 변수를 설계했습니다.
3. 투명한 oracle utility로 학습 라벨을 생성했습니다.
4. Random Forest 기반 AI ranker를 학습하여 후보 위성을 점수화했습니다.
5. `max_signal`, `sticky_signal`, `visibility_guard`, `load_aware`, `stability_aware` baseline과 비교했습니다.
6. `/score`, `/explain` FastAPI endpoint로 추론 계약과 설명 기능을 구성했습니다.
7. 테스트, GitHub Actions, GitHub Pages용 landing page까지 정리했습니다.

## 기술 스택

Python, NumPy, Pandas, scikit-learn, Matplotlib, FastAPI, Pytest, GitHub Actions

## 포트폴리오에서 강조할 점

- 통신 도메인 문제를 ML ranking 문제로 재정의한 경험
- 빠르게 변하는 네트워크 환경을 반영한 feature engineering
- baseline과 AI 모델을 같은 기준으로 비교하는 실험 설계
- synthetic data 사용 사실과 실제 적용 한계를 명확히 구분한 점
- API, explanation, 테스트, GitHub Pages까지 포함한 end-to-end 구현

## 추천 LinkedIn 프로젝트 설명

LEO 위성 네트워크의 빠른 topology 변화 환경에서 핸드오버 결정을 최적화하기 위한 AI 기반 프로토타입을 구현했습니다. 공개 가능한 synthetic constellation simulator를 만들고, elevation angle, signal quality, satellite load, remaining visibility, handover penalty 등의 변수를 설계했습니다. 이후 transparent oracle utility를 기반으로 supervised ranking model을 학습하고 다양한 baseline과 비교했습니다. 실제 산업 적용 결과가 아닌 공개용 synthetic demo임을 명확히 표시했으며, FastAPI scoring/explanation endpoint와 GitHub Actions 테스트까지 구성했습니다.

## 추천 Skills

Machine Learning, Python, Data Simulation, Network Optimization, FastAPI, Model Evaluation
