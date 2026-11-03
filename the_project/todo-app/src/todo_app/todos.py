import logging

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from . import db

logger = logging.getLogger(__name__)

MAX_LENGTH = 140

router = APIRouter(prefix="/todos", tags=["todos"])


class TodoIn(BaseModel):
    # Strip first, so "   " fails min_length. The limit is enforced on the
    # server too; the frontend check is only a convenience.
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=1, max_length=MAX_LENGTH)


@router.get("")
def list_todos():
    with db.pool.connection() as conn:
        return conn.execute("SELECT id, text FROM todos ORDER BY id").fetchall()


@router.post("", status_code=201)
def create_todo(payload: TodoIn):
    with db.pool.connection() as conn:
        todo = conn.execute(
            "INSERT INTO todos (text) VALUES (%s) RETURNING id, text",
            (payload.text,),
        ).fetchone()
    logger.info("Created todo %s", todo["id"])
    return todo