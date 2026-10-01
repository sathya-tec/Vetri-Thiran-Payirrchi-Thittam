from urllib.parse import quote_plus

from ..models.schemas import (
    BudgetAllocation,
    RecommendationItem,
    RecommendationResponse,
)


PLATFORM_SEARCH = {

    "Amazon":
        "https://www.amazon.in/s?k=",

    "Flipkart":
        "https://www.flipkart.com/search?q=",

    "IKEA":
        "https://www.ikea.com/in/en/search/?q=",

    "Swiggy":
        "https://www.swiggy.com/search?query=",

    "Zomato":
        "https://www.zomato.com/search?q=",

    "OYO":
        "https://www.oyorooms.com/search?location=",
}


def url(
    platform: str,
    query: str,
) -> str:

    base = PLATFORM_SEARCH.get(
        platform,
        "https://www.google.com/search?q=",
    )

    return (
        base
        + quote_plus(query)
    )


def fallback_home(
    budget: int,
    rooms: list[str],
    style: str,
) -> RecommendationResponse:

    allocations = [

        BudgetAllocation(
            category="Furniture",
            amount=int(budget * 0.45),
            percentage=45,
            note=(
                "Prioritize essential "
                "pieces first."
            ),
        ),

        BudgetAllocation(
            category="Lighting",
            amount=int(budget * 0.15),
            percentage=15,
            note=(
                "Layer ceiling and "
                "task lighting."
            ),
        ),

        BudgetAllocation(
            category="Decor",
            amount=int(budget * 0.20),
            percentage=20,
            note=(
                "Keep decorative "
                "purchases flexible."
            ),
        ),

        BudgetAllocation(
            category="Storage",
            amount=int(budget * 0.15),
            percentage=15,
            note=(
                "Choose space-efficient "
                "storage."
            ),
        ),

        BudgetAllocation(
            category="Buffer",
            amount=int(budget * 0.05),
            percentage=5,
            note=(
                "Keep a small "
                "contingency."
            ),
        ),
    ]

    items = [

        RecommendationItem(
            name=(
                f"{style.title()} "
                "room storage unit"
            ),
            category="Storage",
            estimated_price=max(
                1500,
                int(budget * 0.12),
            ),
            platform="IKEA",
            search_url=url(
                "IKEA",
                f"{style} storage unit",
            ),
            reason=(
                f"Useful across "
                f"{', '.join(rooms[:2])}."
            ),
            tips=[
                (
                    "Measure the available "
                    "wall space first."
                )
            ],
        ),

        RecommendationItem(
            name="LED ceiling light",
            category="Lighting",
            estimated_price=max(
                800,
                int(budget * 0.06),
            ),
            platform="Amazon",
            search_url=url(
                "Amazon",
                "LED ceiling light",
            ),
            reason=(
                "Adds practical lighting "
                "without consuming much "
                "of the budget."
            ),
            tips=[
                (
                    "Check wattage and room "
                    "size compatibility."
                )
            ],
        ),

        RecommendationItem(
            name="Compact accent table",
            category="Furniture",
            estimated_price=max(
                1800,
                int(budget * 0.10),
            ),
            platform="Amazon",
            search_url=url(
                "Amazon",
                "compact accent table",
            ),
            reason=(
                "Adds useful surface area "
                "while keeping the layout "
                "flexible."
            ),
            tips=[
                (
                    "Compare dimensions, "
                    "not only price."
                )
            ],
        ),

        RecommendationItem(
            name="Wall decor set",
            category="Decor",
            estimated_price=max(
                700,
                int(budget * 0.05),
            ),
            platform="Flipkart",
            search_url=url(
                "Flipkart",
                "wall decor set",
            ),
            reason=(
                "A low-cost way to "
                "personalize the room."
            ),
            tips=[
                (
                    "Choose pieces that "
                    "repeat your chosen style."
                )
            ],
        ),
    ]

    used = sum(
        allocation.amount
        for allocation in allocations[:-1]
    )

    return RecommendationResponse(
        title="PocketSmart Home Plan",
        summary=(
            f"A starter {style} plan "
            f"for {', '.join(rooms)} "
            "with a controlled budget."
        ),
        budget_used=used,
        remaining_budget=max(
            0,
            budget - used,
        ),
        allocations=allocations,
        recommendations=items,
        cautions=[
            (
                "Fallback prices are estimates, "
                "not live prices."
            ),
            (
                "Verify seller, delivery, warranty "
                "and current price before purchasing."
            ),
        ],
    )


def fallback_party(
    budget: int,
    guests: int,
    event_type: str,
) -> RecommendationResponse:

    allocations = [

        BudgetAllocation(
            category="Food",
            amount=int(budget * 0.45),
            percentage=45,
            note=(
                "Scale portions to "
                "guest count."
            ),
        ),

        BudgetAllocation(
            category="Venue",
            amount=int(budget * 0.25),
            percentage=25,
            note=(
                "Compare venue packages "
                "and inclusions."
            ),
        ),

        BudgetAllocation(
            category="Decoration",
            amount=int(budget * 0.15),
            percentage=15,
            note=(
                "Use a focused theme "
                "instead of many small items."
            ),
        ),

        BudgetAllocation(
            category="Entertainment",
            amount=int(budget * 0.10),
            percentage=10,
            note=(
                "Keep entertainment simple "
                "if the venue includes activities."
            ),
        ),

        BudgetAllocation(
            category="Buffer",
            amount=int(budget * 0.05),
            percentage=5,
            note=(
                "Reserve for last-minute needs."
            ),
        ),
    ]

    items = [

        RecommendationItem(
            name=(
                f"Catering search for "
                f"{guests} guests"
            ),
            category="Food",
            estimated_price=max(
                1000,
                int(budget * 0.35),
            ),
            platform="Swiggy",
            search_url=url(
                "Swiggy",
                f"{event_type} catering",
            ),
            reason=(
                "Lets you compare food "
                "choices against the "
                "guest count."
            ),
            tips=[
                (
                    "Ask about delivery, "
                    "minimum order and "
                    "serving size."
                )
            ],
        ),

        RecommendationItem(
            name=(
                "Local restaurant/event "
                "catering options"
            ),
            category="Food",
            estimated_price=max(
                1000,
                int(budget * 0.30),
            ),
            platform="Zomato",
            search_url=url(
                "Zomato",
                f"{event_type} catering",
            ),
            reason=(
                "Useful for comparing "
                "nearby food providers."
            ),
            tips=[
                (
                    "Confirm availability "
                    "for the event date."
                )
            ],
        ),

        RecommendationItem(
            name="Budget-friendly event decor",
            category="Decoration",
            estimated_price=max(
                800,
                int(budget * 0.12),
            ),
            platform="Amazon",
            search_url=url(
                "Amazon",
                f"{event_type} party decoration",
            ),
            reason=(
                "A focused decor package "
                "can cover the main visual areas."
            ),
            tips=[
                (
                    "Prioritize backdrop "
                    "and table areas."
                )
            ],
        ),
    ]

    used = sum(
        allocation.amount
        for allocation in allocations[:-1]
    )

    return RecommendationResponse(
        title="PocketSmart Party Plan",
        summary=(
            f"A starter budget for a "
            f"{event_type} event with "
            f"{guests} guests."
        ),
        budget_used=used,
        remaining_budget=max(
            0,
            budget - used,
        ),
        allocations=allocations,
        recommendations=items,
        cautions=[
            (
                "Vendor availability and pricing "
                "vary by date and location."
            )
        ],
    )


def fallback_jewelry(
    budget: int,
    occasion: str,
    style: str,
    outfit_color: str,
) -> RecommendationResponse:

    allocations = [

        BudgetAllocation(
            category="Main piece",
            amount=int(budget * 0.55),
            percentage=55,
            note=(
                "Put most of the budget "
                "into the hero piece."
            ),
        ),

        BudgetAllocation(
            category="Earrings",
            amount=int(budget * 0.20),
            percentage=20,
            note=(
                "Choose a complementary "
                "rather than competing shape."
            ),
        ),

        BudgetAllocation(
            category="Bracelet",
            amount=int(budget * 0.10),
            percentage=10,
            note=(
                "Optional depending "
                "on sleeve length."
            ),
        ),

        BudgetAllocation(
            category="Hair/accessory",
            amount=int(budget * 0.10),
            percentage=10,
            note=(
                "Optional finishing detail."
            ),
        ),

        BudgetAllocation(
            category="Buffer",
            amount=int(budget * 0.05),
            percentage=5,
            note=(
                "Keep room for "
                "price differences."
            ),
        ),
    ]

    items = [

        RecommendationItem(
            name=(
                f"{style.title()} necklace"
            ),
            category="Main piece",
            estimated_price=max(
                600,
                int(budget * 0.40),
            ),
            platform="Amazon",
            search_url=url(
                "Amazon",
                f"{style} necklace {outfit_color}",
            ),
            reason=(
                f"A {style} direction can "
                f"complement a {occasion} outfit "
                "while keeping the main piece "
                "within budget."
            ),
            tips=[
                (
                    "Check necklace length "
                    "and clasp quality."
                )
            ],
        ),

        RecommendationItem(
            name=(
                f"Matching {style} earrings"
            ),
            category="Earrings",
            estimated_price=max(
                400,
                int(budget * 0.18),
            ),
            platform="Flipkart",
            search_url=url(
                "Flipkart",
                f"{style} earrings {outfit_color}",
            ),
            reason=(
                "Keeps the jewelry set "
                "coordinated without requiring "
                "an exact matching set."
            ),
            tips=[
                (
                    "Avoid too many competing "
                    "statement pieces."
                )
            ],
        ),

        RecommendationItem(
            name="Minimal bracelet",
            category="Bracelet",
            estimated_price=max(
                250,
                int(budget * 0.10),
            ),
            platform="Amazon",
            search_url=url(
                "Amazon",
                f"minimal bracelet {outfit_color}",
            ),
            reason=(
                "A subtle bracelet can finish "
                "the look without overpowering "
                "the main piece."
            ),
            tips=[
                (
                    "Match the metal tone "
                    "to the necklace."
                )
            ],
        ),
    ]

    used = sum(
        allocation.amount
        for allocation in allocations[:-1]
    )

    return RecommendationResponse(
        title="PocketSmart Jewelry Plan",
        summary=(
            f"A {style} jewelry direction "
            f"for a {occasion} occasion and "
            f"{outfit_color} outfit."
        ),
        budget_used=used,
        remaining_budget=max(
            0,
            budget - used,
        ),
        allocations=allocations,
        recommendations=items,
        cautions=[
            (
                "Image-based color suggestions "
                "are style guidance, not professional "
                "color analysis."
            ),
            (
                "Fallback prices are estimates, "
                "not live prices."
            ),
        ],
    )
