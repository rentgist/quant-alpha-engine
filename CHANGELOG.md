# 변경 이력

## [2026-08-19] 미국 ETF 수급 프록시 자동 갱신 복구

- GitHub Actions에서 `us_flow_engine.py`가 `yfinance` 누락으로 실패하던 문제를 수정했습니다.
- 의존성 목록에 `yfinance`를 추가해 시간별 수급 프록시 JSON·리포트 생성이 다시 실행되도록 했습니다.

## [2026-08-08] 미국 ETF 수급 프록시 최신성 보강

- 시간별 자동 작업에 `us_flow_engine.py` 실행을 추가했습니다.
- Markdown 화면용 리포트와 함께 기계 판독용 `us_flow_report.json`을 생성합니다.
- JSON에 생성 시각, 실제 시장 기준일, 계산 방식, 실제 펀드플로우 여부를 명시합니다.
