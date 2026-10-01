import asyncio
import json
import logging
from typing import Any

from google import genai
from google.genai import types

from ..config import get_settings
from ..models.schemas import (
    RecommendationResponse,
)

from .recommendations import (
    fallback_home,
    fallback_party,
    fallback_jewelry,
)


logger = logging.getLogger(__name__)


def _client():

    settings = get_settings()

    if not settings.gemini_api_key:
        return None

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def _prompt(
    planner: str,
    data: dict[str, Any],
) -> str:

    common = f"""
You are PocketSmart AI,
a budget-aware recommendation assistant.

Planner:
{planner}

User data:
{json.dumps(data, ensure_ascii=False)}

Currency:
INR.

Your job is to produce practical,
concise and budget-conscious recommendations.

IMPORTANT RULES:

1. Never invent live prices.
2. Never claim current stock availability.
3. Never invent ratings or reviews.
4. Never invent real-time vendor availability.
5. Estimated prices must be treated as estimates.
6. Do not fabricate product URLs.
7. Keep recommended spending at or below
   the user's budget.
8. Explain important trade-offs.
9. Return valid JSON matching the supplied schema.
10. Use simple platform names such as Amazon,
    Flipkart, IKEA, Swiggy, Zomato or OYO.
"""

    if planner == "home":

        return common + """
Recommend home interior items for the
specified rooms and style.

Balance:
- furniture
- lighting
- storage
- decor

Focus on practical budget allocation.
"""

    if planner == "party":

        return common + """
Create a party/event budget plan.

Consider:
- guest count
- event type
- venue
- food
- decoration
- entertainment

Provide a realistic budget allocation.
"""

    return common + """
Recommend jewelry categories and combinations
based on:

- occasion
- style
- outfit colour
- notes

If an outfit image is supplied, use it only
to discuss visible style and colour cues.

Do not make sensitive personal inferences
from the image.
"""


def _generate(
    planner: str,
    data: dict[str, Any],
    image_bytes: bytes | None,
    mime_type: str | None,
) -> RecommendationResponse:

    client = _client()

    if client is None:

        return _fallback(
            planner,
            data,
        )

    settings = get_settings()

    contents: list[Any] = [
        _prompt(
            planner,
            data,
        )
    ]

    if (
        image_bytes
        and mime_type
    ):

        contents.append(
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            )
        )

    try:

        response = client.models.generate_content(

            model=settings.gemini_model,

            contents=contents,

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

                response_schema=RecommendationResponse,

                temperature=0.3,
            ),
        )

        return RecommendationResponse.model_validate_json(
            response.text
        )

    except Exception:

        logger.exception(
            "Gemini request failed; "
            "using fallback recommendations"
        )

        return _fallback(
            planner,
            data,
        )


def _fallback(
    planner: str,
    data: dict[str, Any],
) -> RecommendationResponse:

    if planner == "home":

        return fallback_home(
            data["budget"],
            data["rooms"],
            data["style"],
        )

    if planner == "party":

        return fallback_party(
            data["budget"],
            data["guests"],
            data["event_type"],
        )

    return fallback_jewelry(
        data["budget"],
        data["occasion"],
        data["style"],
        data.get(
            "outfit_color",
            "not specified",
        ),
    )


async def generate_recommendation(
    planner: str,
    data: dict[str, Any],
    image_bytes: bytes | None = None,
    mime_type: str | None = None,
):

    return await asyncio.to_thread(
        _generate,
        planner,
        data,
        image_bytes,
        mime_type,
    )
