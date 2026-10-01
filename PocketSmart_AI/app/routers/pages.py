from fastapi import (
    APIRouter,
    Request,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    include_in_schema=False
)


templates = Jinja2Templates(
    directory="app/templates"
)


def render(
    request: Request,
    name: str,
    **context,
):

    return templates.TemplateResponse(
        request=request,
        name=name,
        context=context,
    )


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(request: Request):

    return render(
        request,
        "index.html",
    )


@router.get(
    "/login",
    response_class=HTMLResponse,
)
def login_page(request: Request):

    return render(
        request,
        "login.html",
    )


@router.get(
    "/register",
    response_class=HTMLResponse,
)
def register_page(request: Request):

    return render(
        request,
        "register.html",
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
)
def dashboard(request: Request):

    return render(
        request,
        "dashboard.html",
    )


@router.get(
    "/planner/{planner}",
    response_class=HTMLResponse,
)
def planner(
    request: Request,
    planner: str,
):

    if planner not in {
        "home",
        "party",
        "jewelry",
    }:

        return render(
            request,
            "404.html",
        )

    return render(
        request,
        f"{planner}_planner.html",
        planner=planner,
    )


@router.get(
    "/history",
    response_class=HTMLResponse,
)
def history_page(request: Request):

    return render(
        request,
        "history.html",
    )


@router.get(
    "/testimonials",
    response_class=HTMLResponse,
)
def testimonials(request: Request):

    return render(
        request,
        "testimonials.html",
    )
