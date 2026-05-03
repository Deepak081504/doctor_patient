from fastapi import FastAPI
from app.database import engine, Base
from app.routers import router
from app.models import User,Doctor,Patient,Appointment
app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router)

@app.get("/")
def home():
    return {"message": "API working"}