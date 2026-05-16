# Production Gap - 실제 산업 적용 전 필요한 것

이 저장소는 포트폴리오용 프로토타입입니다. 실제 LEO 위성/통신망에 적용된 시스템이 아닙니다.

## 실제 적용 전 필요한 검증

1. **고정밀 궤도/위치 계산**
   - TLE/SGP4 또는 사업자 내부 궤도 데이터
   - 위성 자세, 빔, footprint, 지상국 위치 제약

2. **무선 링크 모델 고도화**
   - 주파수 대역, 안테나 gain, path loss, rain fade, interference
   - 실제 RSRP/SINR/CQI 측정값 또는 고정밀 simulator

3. **네트워크 제약 반영**
   - gateway/backhaul capacity
   - beam hopping, inter-satellite link, scheduling 정책
   - 세션 유지, latency, packet loss, service class SLA

4. **운영 안정성**
   - fail-safe fallback policy
   - latency budget
   - drift monitoring
   - human override / rule-based guardrail
   - 장애 상황 테스트

5. **실데이터 검증**
   - 실제 handover logs 또는 high-fidelity digital twin 결과와 비교
   - traffic burst, regional congestion, weather, terminal mobility scenario 검증

## 포트폴리오에서의 표현 가이드

좋은 표현:

> “공개 가능한 synthetic simulator로 LEO handover 의사결정을 ML ranking 문제로 구현했고, 실제 적용 전 필요한 검증 항목을 분리해 정리했습니다.”

피해야 할 표현:

> “실제 위성망에 적용 가능한 모델입니다.”
> “산업 현장 성능을 검증했습니다.”
> “상용 서비스에서 사용할 수 있습니다.”
