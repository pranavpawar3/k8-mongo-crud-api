import os
import uvicorn
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio
import uuid

app = FastAPI()
USER_NAME = os.environ["USER_NAME"]
USER_PWD = os.environ["USER_PWD"]
DB_URL = os.environ["DB_URL"]
MONGODB_URL = f'mongodb://{USER_NAME}:{USER_PWD}@{DB_URL}'

# MONGODB_URL = "mongodb://admin:password@localhost:27017"
# MONGODB_URL = "mongodb://mongouser:mongopassword@db-service"
print(f"trying with {MONGODB_URL}")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.college
print("mongo connected", db)

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class ArticleModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    content_type: str = Field(...)
    status: str = Field(...)
    title: str = Field(...)
    version: str = Field(...)
    read_duration: float = Field(..., description="read duration in minutes")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "content_type": "FAQs",
                "status": "published",
                "title": "If your iPhone or iPod touch will not charge",
                "version": "1.0",
                "read_duration": 5
            }
        }


class UpdateArticleModel(BaseModel):
    content_type: Optional[str]
    status: Optional[str]
    title: Optional[str]
    version: Optional[str]
    read_duration: Optional[float]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "content_type": "FAQs",
                "status": "published",
                "title": "If your iPhone or iPod touch will not charge",
                "version": "1.0",
                "read_duration": 5
            }
        }


@app.post("/", response_description="Add new article", response_model=ArticleModel)
async def create_article(article: ArticleModel = Body(...)):
    article = jsonable_encoder(article)
    new_article = await db["articles"].insert_one(article)
    created_article = await db["articles"].find_one({"_id": new_article.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_article)


@app.get(
    "/", response_description="List all articles", response_model=List[ArticleModel]
)
async def list_articles():
    articles = await db["articles"].find().to_list(1000)
    return articles


@app.get(
    "/{id}", response_description="Get a single article", response_model=ArticleModel
)
async def show_article(id: str):
    if (article := await db["articles"].find_one({"_id": id})) is not None:
        return article

    raise HTTPException(status_code=404, detail=f"Article {id} not found")


@app.put("/{id}", response_description="Update an article", response_model=ArticleModel)
async def update_article(id: str, article: UpdateArticleModel = Body(...)):
    article = {k: v for k, v in article.dict().items() if v is not None}

    if len(article) >= 1:
        update_result = await db["articles"].update_one({"_id": id}, {"$set": article})

        if update_result.modified_count == 1:
            if (
                updated_article := await db["articles"].find_one({"_id": id})
            ) is not None:
                return updated_article

    if (existing_article := await db["articles"].find_one({"_id": id})) is not None:
        return existing_article

    raise HTTPException(status_code=404, detail=f"Article {id} not found")


@app.delete("/{id}", response_description="Delete an article")
async def delete_article(id: str):
    delete_result = await db["articles"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

    raise HTTPException(status_code=404, detail=f"Article {id} not found")
