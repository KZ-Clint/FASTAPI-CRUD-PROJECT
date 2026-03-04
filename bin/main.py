from fastapi import FastAPI
from app.routes.issues import router as issues_router
from app.middleware.timer import timing_middleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

@app.get("/health")
def health_check():
    return { "status": "ok" }

# @app.get("/items")
# def get_items():
#     return { "status": "ok", "items":items }

# @app.get("/items/filter")
# def get_items(skip: int = 0, limit: int = 2, page: int = 1):
#     skip = limit*(page-1)
#     new_items = items[skip:(limit+skip)]
#     return { "status": "ok", "skip":skip, "limit":limit, "page":page, "items":new_items }

# @app.get("/items/{id}")
# async def get_specific_item(id:int):
#     new_items = [ item for item in items if item["id"] == id ]
#     return { "status": "ok", "item":new_items[0] if len(new_items) > 0 else None }


# @app.post("/items")
# def create_item(item:dict):
#     print(item)
#     items.append(item)
#     print(items)
#     return { "status": "ok", "items":items }

app.middleware("http")(timing_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(issues_router)