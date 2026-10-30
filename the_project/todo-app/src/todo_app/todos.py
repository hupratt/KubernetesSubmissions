# /todos
import logging
from itertools import count

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

MAX_LENGTH = 140

router = APIRouter(prefix="/todos", tags=["todos"])

# In-memory for now; replaced by a database in a later exercise.
_todos: list[dict] = [
    {"id": 1, "text": "Learn how Kubernetes Deployments work"},
    {"id": 2, "text": "Write a Dockerfile for the todo app"},
]
_ids = count(start=3)


class TodoIn(BaseModel):
    # Enforce the limit on the server too; the frontend check is only a convenience.
    text: str = Field(min_length=1, max_length=MAX_LENGTH)


@router.get("")
def list_todos():
    return _todos


@router.post("", status_code=201)
def create_todo(payload: TodoIn):
    todo = {"id": next(_ids), "text": payload.text.strip()}
    _todos.append(todo)
    logger.info("Created todo %s", todo["id"])
    return todo