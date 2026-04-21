from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app.core.config import get_settings


def _get_mongodb_uri() -> str:
    mongodb_uri = get_settings().mongodb_uri.strip()
    if not mongodb_uri:
        raise RuntimeError("MONGODB_URI is not set in the environment.")
    return mongodb_uri


def get_mongo_client() -> MongoClient:
    return MongoClient(
        _get_mongodb_uri(),
        appname="company-knowledge-assistant",
        serverSelectionTimeoutMS=5000,
    )


def get_database() -> Database:
    return get_mongo_client()[get_settings().mongo_database_name]


def get_documents_collection() -> Collection:
    return get_database()[get_settings().mongo_collection_name]


def get_rag_chunks_collection() -> Collection:
    return get_database()[get_settings().mongo_collection_name]


def get_chat_history_collection() -> Collection:
    collection = get_database()["chat_history"]
    collection.create_index([("user_id", 1), ("updated_at", -1)])
    collection.create_index([("conversation_id", 1)], unique=True)
    return collection


def get_users_collection() -> Collection:
    collection = get_database()["users"]
    collection.create_index([("email", 1)], unique=True)
    return collection
