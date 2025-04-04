from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from authentication import auth_route



app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credential=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

app.include_router(auth_route.router, tags=["Auth"])


@app.get("/")
def Main():
    return ("Test")