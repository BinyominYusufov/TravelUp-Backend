import uvicorn  
from fastapi import FastAPI, staticfiles
from accounts.views import auth_route
from destinations.api import destinations_router
from fastapi.middleware.cors import CORSMiddleware
from bookings.api import bookings_router
from reviews.api import reviews_router
from payments.api import payments_router
from middlewares import simple_midlleware, process_time_per_request
from database import engine, BaseModel
from accounts.models import User, Role, Permission, BlackListTokens


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    print("Database initialized successfully")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:8081",    
        "http://127.0.0.1:8080",
        'https://adminpanel-travelup.vercel.app',
        'https://travel-up-front-end.vercel.app'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    auth_route,
    prefix="/auth",
    tags=["Authentication endpoints"],
)

app.include_router(destinations_router, prefix="/destinations", tags=["Destinations endpoints"])
app.include_router(bookings_router, prefix="/bookings", tags=["Bookings endpoints"])
app.include_router(reviews_router, prefix="/reviews", tags=["Reviews endpoints"])
app.include_router(payments_router, prefix="/payments", tags=["Payments endpoints"])

app.middleware("http")(simple_midlleware)
app.middleware("http")(process_time_per_request)

app.mount("/media", staticfiles.StaticFiles(directory="media"), name="media")


@app.get("/test")
async def get_test():
    return {"message": "test"}


if __name__ == "__main__":
    uvicorn.run(
        "manage:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
