import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models.db_models import (
    RecommendationHistory,
    User,
)

from ..models.schemas import (
    HomeRequest,
    PartyRequest,
    JewelryRequest,
    RecommendationResponse,
)

from ..services.auth import get_current_user

from ..services.gemini_service import (
    generate_recommendation,
)


router = APIRouter(
    tags=["planners"]
)


MAX_IMAGE_BYTES = 5 * 1024 * 1024


ALLOWED_IMAGES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}


def save_history(
    db,
    user,
    planner,
    payload,
    result,
):

    history = RecommendationHistory(
        user_id=user.id,
        planner=planner,
        budget=payload["budget"],
        input_json=json.dumps(
            payload
        ),
        result_json=result.model_dump_json(),
    )

    db.add(history)
    db.commit()


@router.post(
    "/generate-home",
    response_model=RecommendationResponse,
)
async def generate_home(
    payload: HomeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    data = payload.model_dump()

    result = await generate_recommendation(
        "home",
        data,
    )

    save_history(
        db,
        user,
        "home",
        data,
        result,
    )

    return result


@router.post(
    "/generate-party",
    response_model=RecommendationResponse,
)
async def generate_party(
    payload: PartyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    data = payload.model_dump()

    result = await generate_recommendation(
        "party",
        data,
    )

    save_history(
        db,
        user,
        "party",
        data,
        result,
    )

    return result


@router.post(
    "/generate-jewelry",
    response_model=RecommendationResponse,
)
async def generate_jewelry(

    budget: int = Form(
        ...,
        gt=0,
        le=10_000_000,
    ),

    occasion: str = Form(
        ...,
        min_length=2,
        max_length=100,
    ),

    style: str = Form(
        "elegant",
        max_length=100,
    ),

    outfit_color: str = Form(
        "not specified",
        max_length=100,
    ),

    notes: str = Form(
        "",
        max_length=1000,
    ),

    outfit_image: UploadFile | None = File(
        None
    ),

    user: User = Depends(get_current_user),

    db: Session = Depends(get_db),
):

    image_bytes = None
    mime_type = None

    if outfit_image:

        if (
            outfit_image.content_type
            not in ALLOWED_IMAGES
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPG, PNG and WebP "
                    "images are supported"
                ),
            )

        image_bytes = await outfit_image.read()

        if len(image_bytes) > MAX_IMAGE_BYTES:

            raise HTTPException(
                status_code=413,
                detail=(
                    "Image must be 5 MB or smaller"
                ),
            )

        mime_type = outfit_image.content_type

    payload = JewelryRequest(
        budget=budget,
        occasion=occasion,
        style=style,
        outfit_color=outfit_color,
        notes=notes,
    )

    data = payload.model_dump()

    result = await generate_recommendation(
        "jewelry",
        data,
        image_bytes,
        mime_type,
    )

    save_history(
        db,
        user,
        "jewelry",
        data,
        result,
    )

    return result


@router.get(
    "/recommendations-details"
)
def recommendation_details(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    item = db.scalar(
        select(
            RecommendationHistory
        )
        .where(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            desc(
                RecommendationHistory.created_at
            )
        )
    )

    if not item:

        return {
            "message": (
                "No recommendations yet"
            )
        }

    return json.loads(
        item.result_json
    )


@router.get("/history")
def history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    rows = db.scalars(
        select(
            RecommendationHistory
        )
        .where(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            desc(
                RecommendationHistory.created_at
            )
        )
        .limit(50)
    ).all()

    return [
        {
            "id": row.id,
            "planner": row.planner,
            "budget": row.budget,
            "created_at": row.created_at.isoformat(),
            "input": json.loads(
                row.input_json
            ),
            "result": json.loads(
                row.result_json
            ),
        }
        for row in rows
    ]
