from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from authentication import auth_route
from transaction import transaction_route
from predictions import prediction_route
from budget import budget_route
from summary import summary_route




app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credential=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth_route.router, tags=["Auth"])
app.include_router(transaction_route.router, tags=["Transactions"])
app.include_router(prediction_route.router, tags=["Predictions"])
app.include_router(budget_route.router, tags=["Budget"])
app.include_router(summary_route.router, tags=["Summary"])


@app.get("/") 
async def root():
    return ("Test")
