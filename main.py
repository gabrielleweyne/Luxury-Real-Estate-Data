from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from models import create_models
from routers.api import api_routes
from routers.browser import browser_routes
import uvicorn

# Create REST API
app = FastAPI()

create_models()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_routes)
app.include_router(browser_routes)

# ========= INICIALIZAR SERVIDOR =========
if __name__ == "__main__":
    uvicorn.run("main:app", port=3000)
