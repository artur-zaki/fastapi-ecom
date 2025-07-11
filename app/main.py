from fastapi import FastAPI
from app.routers import category, products, auth, permission, reviews

app = FastAPI()
app_v1 = FastAPI()
app_v2 = FastAPI()


@app_v1.get("/")
async def welcome() -> dict:
    return {"message": "My e-commerce app - V1"}

@app_v2.get("/")
async def welcome() -> dict:
    return {"message": "My e-commerce app - V2"}


app_v1.include_router(category.router)
app_v1.include_router(products.router)
app_v1.include_router(auth.router)
app_v1.include_router(permission.router)
app_v1.include_router(reviews.router)

app_v2.include_router(category.router)
app_v2.include_router(products.router)
app_v2.include_router(auth.router)
app_v2.include_router(permission.router)
app_v2.include_router(reviews.router)

app.mount("/v1", app_v1)
app.mount("/v2", app_v2)