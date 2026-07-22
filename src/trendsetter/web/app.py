"""Dashboard app. Run with: uvicorn trendsetter.web.app:app

Single-password auth (M0): session cookie set on login, an HTTP middleware
redirects everything except /login and /static to the login page.
"""

import secrets
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from trendsetter.config import get_settings
from trendsetter.web.routes.costs import router as costs_router

templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

app = FastAPI(title="Trendsetter")


@app.middleware("http")
async def require_auth(request: Request, call_next):
    path = request.url.path
    public = path.startswith("/login") or path.startswith("/static")
    if not public and not request.session.get("auth"):
        return RedirectResponse("/login", status_code=303)
    return await call_next(request)


# Added after the auth middleware so it wraps it (sessions available inside).
app.add_middleware(SessionMiddleware, secret_key=get_settings().session_secret)


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
async def login(request: Request, password: Annotated[str, Form()] = ""):
    if secrets.compare_digest(password.encode(), get_settings().app_password.encode()):
        request.session["auth"] = True
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request, "login.html", {"error": "Wrong password"}, status_code=401
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


@app.get("/")
async def index():
    return RedirectResponse("/costs")


app.include_router(costs_router)
