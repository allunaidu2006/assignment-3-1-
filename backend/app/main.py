import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.database import create_tables
from app.routers import auth, matches, predict, analytics
from app.services.ml_service import ml_service

app = FastAPI(title="Match Predictor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(matches.router)
app.include_router(predict.router)
app.include_router(analytics.router)

@app.on_event("startup")
def on_startup():
    create_tables()

@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": ml_service.is_trained()}

# Serve built frontend static files if present
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't intercept API routes or Swagger
        if full_path.startswith("api") or full_path in ["docs", "openapi.json", "redoc"]:
            return JSONResponse(status_code=404, content={"message": "Resource not found"})
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
