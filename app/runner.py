import uvicorn
from app.settings import settings

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.SPIRIX_HOST, port=settings.SPIRIX_POST, reload=True)