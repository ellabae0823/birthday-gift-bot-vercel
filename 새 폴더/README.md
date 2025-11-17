# Birthday Gift Recommender

친구에 대한 설명과 예산을 입력하면 적절한 선물을 추천해주는 챗봇입니다. CLI 모드와 웹 API 모두 제공합니다.

## 준비

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows PowerShell
pip install -r requirements.txt
```

## CLI로 실행

```bash
python chatbot.py
```

친구의 취향이나 예산을 자연어로 입력하면 최대 3개의 추천을 출력합니다. `quit` 또는 `exit`로 종료할 수 있습니다.

## 웹 API로 실행

```bash
uvicorn chatbot:app --reload
```

- 기본 주소: `http://127.0.0.1:8000`
- `GET /` : API 소개 메시지
- `POST /recommend`

```json
{
  "description": "운동 좋아하고 10만원 정도의 예산"
}
```

응답 예시:

```json
{
  "recommendations": [
    {
      "name": "무선 노이즈 캔슬링 이어버드",
      "category": "music",
      "price_label": "18만 원대",
      "description": "깨끗한 음질과 방수 등급으로 야외 활동에도 잘 어울려요."
    }
  ]
}
```

원하는 플랫폼(PaaS, 서버리스 등)에서 `uvicorn` 실행 명령을 서버 시작 스크립트로 등록하면 손쉽게 배포할 수 있습니다.
