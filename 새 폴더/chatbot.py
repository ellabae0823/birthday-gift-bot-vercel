import json
import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel


@dataclass
class Gift:
    name: str
    category: str
    tags: List[str]
    description: str
    price_tier: str
    price_label: str


class GiftRecommender:
    PRICE_HINTS = {
        "budget": ["저렴", "부담없", "가볍", "소소", "3만", "30,000"],
        "mid": ["5만", "8만", "10만", "중간", "적당", "60,000", "100,000"],
        "premium": ["프리미엄", "고급", "비싼", "특별", "20만", "200,000"],
    }

    def __init__(self, gifts: List[Dict[str, str]]):
        self.gifts = [Gift(**item) for item in gifts]

    def _extract_amount(self, text: str) -> Optional[int]:
        matches = re.findall(r"(\d[\d,]*)\s*(만|만원|만원대|원)?", text)
        if not matches:
            return None
        largest = 0
        for raw_number, unit in matches:
            number = int(raw_number.replace(",", ""))
            if unit in {"만", "만원", "만원대"}:
                number *= 10_000
            largest = max(largest, number)
        return largest or None

    def _infer_price_tier(self, text: str) -> Optional[str]:
        normalized = text.lower()
        amount = self._extract_amount(text)
        if amount:
            if amount <= 40_000:
                return "budget"
            if amount <= 120_000:
                return "mid"
            return "premium"
        for tier, hints in self.PRICE_HINTS.items():
            if any(hint in text or hint in normalized for hint in hints):
                return tier
        return None

    def recommend(self, user_text: str) -> List[Gift]:
        user_text_lower = user_text.lower()
        desired_tier = self._infer_price_tier(user_text)
        candidates = [
            gift for gift in self.gifts if not desired_tier or gift.price_tier == desired_tier
        ]
        if not candidates:
            candidates = self.gifts
        scored: List[Gift] = []
        scored_with_points = []
        for gift in candidates:
            score = 0
            if gift.category.lower() in user_text_lower:
                score += 3
            for tag in gift.tags:
                if tag.lower() in user_text_lower:
                    score += 1
            if score == 0 and not desired_tier:
                score = 1
            if score:
                scored_with_points.append((score, gift))
        scored_with_points.sort(key=lambda item: item[0], reverse=True)
        scored = [gift for _, gift in scored_with_points[:3]]
        if not scored:
            return candidates[:3]
        return scored


def load_gifts() -> List[Dict[str, str]]:
    gift_data = """
    [
        {
            "name": "아로마 테라피 캔들 세트",
            "category": "relax",
            "tags": ["힐링", "향기", "집", "휴식"],
            "description": "맞춤 향을 섞은 3종 캔들로 방 안 분위기를 부드럽게 만들어줘요.",
            "price_tier": "budget",
            "price_label": "3만 원대"
        },
        {
            "name": "포토북 제작 바우처",
            "category": "memories",
            "tags": ["사진", "추억", "감성"],
            "description": "함께 찍은 사진을 예쁜 미니 포토북으로 만들어 선물할 수 있어요.",
            "price_tier": "budget",
            "price_label": "4만 원대"
        },
        {
            "name": "홈 바디케어 세트",
            "category": "selfcare",
            "tags": ["웰니스", "스파", "힐링"],
            "description": "필로우 미스트, 바디스크럽, 오일로 구성된 홈 스파 키트입니다.",
            "price_tier": "budget",
            "price_label": "5만 원대"
        },
        {
            "name": "바리스타 클래스 체험권",
            "category": "experience",
            "tags": ["체험", "커피", "데이트"],
            "description": "주말에 함께 V60와 라떼 아트를 배워보는 소규모 클래스예요.",
            "price_tier": "mid",
            "price_label": "8만 원대"
        },
        {
            "name": "디자인 손목시계",
            "category": "fashion",
            "tags": ["패션", "세련", "출근"],
            "description": "심플한 다이얼과 가죽 스트랩이 돋보이는 데일리 시계예요.",
            "price_tier": "mid",
            "price_label": "9만 원대"
        },
        {
            "name": "프리미엄 원두 커피 구독권",
            "category": "coffee",
            "tags": ["커피", "카페", "모닝 루틴"],
            "description": "스페셜티 원두를 한 달 동안 받아볼 수 있는 구독형 선물입니다.",
            "price_tier": "mid",
            "price_label": "11만 원대"
        },
        {
            "name": "무선 노이즈 캔슬링 이어버드",
            "category": "music",
            "tags": ["운동", "출퇴근", "음악"],
            "description": "깨끗한 음질과 방수 등급으로 야외 활동에도 잘 어울려요.",
            "price_tier": "premium",
            "price_label": "18만 원대"
        },
        {
            "name": "디자이너 실크 스카프",
            "category": "style",
            "tags": ["패션", "예술", "포인트"],
            "description": "산뜻한 패턴으로 어떤 룩에도 포인트가 되는 한정판 스카프예요.",
            "price_tier": "premium",
            "price_label": "16만 원대"
        },
        {
            "name": "미니 빔프로젝터",
            "category": "entertainment",
            "tags": ["영화", "홈시네마", "기술"],
            "description": "어두운 방에서 영화관 느낌을 낼 수 있는 휴대용 프로젝터예요.",
            "price_tier": "premium",
            "price_label": "22만 원대"
        }
    ]
    """
    return json.loads(gift_data)


class RecommendRequest(BaseModel):
    description: str


class Recommendation(BaseModel):
    name: str
    category: str
    price_label: str
    description: str


def build_recommendations(description: str) -> List[Recommendation]:
    gifts = RECOMMENDER.recommend(description)
    return [
        Recommendation(
            name=gift.name,
            category=gift.category,
            price_label=gift.price_label,
            description=gift.description,
        )
        for gift in gifts
    ]


def run_cli() -> None:
    print("친구 생일 선물 추천 챗봇입니다. 종료하려면 'quit'를 입력하세요.")
    while True:
        user_input = input("친구에 대해 설명하거나 원하는 예산을 적어주세요: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            print("도움이 되었기를 바랄게요. 즐거운 파티 보내세요!")
            break
        recommendations = RECOMMENDER.recommend(user_input)
        if not recommendations:
            print("조건에 맞는 선물을 찾지 못했어요. 친구의 취향이나 예산을 더 알려주세요.")
            continue
        print("이런 선물은 어떨까요?")
        for gift in recommendations:
            print(f"- {gift.name} [{gift.price_label}] : {gift.description}")


app = FastAPI(
    title="Birthday Gift Recommender",
    description="친구에 대한 설명을 입력하면 예산대별 맞춤 선물을 추천해주는 API",
)
RECOMMENDER = GiftRecommender(load_gifts())


@app.get("/")
def root() -> Dict[str, str]:
    return {
        "message": "친구 생일 선물 추천 API입니다.",
        "usage": "POST /recommend 엔드포인트로 description을 보내주세요.",
    }


@app.post("/recommend")
def recommend_endpoint(payload: RecommendRequest) -> Dict[str, List[Recommendation]]:
    return {"recommendations": build_recommendations(payload.description)}


if __name__ == "__main__":
    run_cli()
