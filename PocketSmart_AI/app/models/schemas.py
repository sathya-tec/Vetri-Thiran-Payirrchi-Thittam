from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


PlannerType = Literal[
    "home",
    "party",
    "jewelry",
]


class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128,
    )


class UserOut(BaseModel):

    id: int
    name: str
    email: EmailStr


class HomeRequest(BaseModel):

    budget: int = Field(
        gt=0,
        le=10_000_000,
    )

    rooms: list[str] = Field(
        min_length=1
    )

    style: str = Field(
        default="modern",
        max_length=100,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )


class PartyRequest(BaseModel):

    budget: int = Field(
        gt=0,
        le=10_000_000,
    )

    guests: int = Field(
        gt=0,
        le=10_000,
    )

    event_type: str = Field(
        min_length=2,
        max_length=100,
    )

    venue: str = Field(
        default="flexible",
        max_length=200,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )


class JewelryRequest(BaseModel):

    budget: int = Field(
        gt=0,
        le=10_000_000,
    )

    occasion: str = Field(
        min_length=2,
        max_length=100,
    )

    style: str = Field(
        default="elegant",
        max_length=100,
    )

    outfit_color: str = Field(
        default="not specified",
        max_length=100,
    )

    notes: str = Field(
        default="",
        max_length=1000,
    )


class RecommendationItem(BaseModel):

    name: str

    category: str

    estimated_price: int = Field(
        ge=0
    )

    platform: str

    search_url: str

    reason: str

    tips: list[str] = Field(
        default_factory=list
    )


class BudgetAllocation(BaseModel):

    category: str

    amount: int = Field(
        ge=0
    )

    percentage: int = Field(
        ge=0,
        le=100,
    )

    note: str = ""


class RecommendationResponse(BaseModel):

    title: str

    summary: str

    budget_used: int = Field(
        ge=0
    )

    remaining_budget: int = Field(
        ge=0
    )

    allocations: list[BudgetAllocation] = Field(
        default_factory=list
    )

    recommendations: list[RecommendationItem] = Field(
        default_factory=list
    )

    cautions: list[str] = Field(
        default_factory=list
    )

    @field_validator("remaining_budget")
    @classmethod
    def nonnegative(cls, value):

        return max(0, value)
    