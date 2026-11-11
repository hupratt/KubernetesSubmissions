import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from . import db, events

logger = logging.getLogger(__name__)

MAX_LENGTH = 140

router = APIRouter(prefix="/todos", tags=["todos"])


class TodoIn(BaseModel):
    # Strip first, so "   " fails min_length. The limit is enforced on the
    # server too; the frontend check is only a convenience.
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=1, max_length=MAX_LENGTH)


class TodoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str | None = Field(default=None, min_length=1, max_length=MAX_LENGTH)
    done: bool | None = None


@router.get("")
def list_todos():
    with db.pool.connection() as conn:
        return conn.execute("SELECT id, text, done FROM todos ORDER BY id").fetchall()


@router.post("", status_code=201)
def create_todo(payload: TodoIn, background_tasks: BackgroundTasks):
    # Log every incoming todo request text along with its character count
    logger.info("Received todo request (%d chars): %r", len(payload.text), payload.text)

    with db.pool.connection() as conn:
        todo = conn.execute(
            "INSERT INTO todos (text) VALUES (%s) RETURNING id, text, done",
            (payload.text,),
        ).fetchone()
    logger.info("Created todo %s", todo["id"])

    # Runs after the response is sent, on the event loop, and only after the
    # DB transaction above has committed.
    background_tasks.add_task(events.publish, "created", todo)
    return todo


@router.put("/{todo_id}")
def update_todo(todo_id: int, payload: TodoUpdate, background_tasks: BackgroundTasks):
    with db.pool.connection() as conn:
        existing = conn.execute(
            "SELECT id, text, done FROM todos WHERE id = %s", (todo_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Todo not found")

        new_text = payload.text if payload.text is not None else existing["text"]
        new_done = payload.done if payload.done is not None else existing["done"]

        updated = conn.execute(
            "UPDATE todos SET text = %s, done = %s WHERE id = %s RETURNING id, text, done",
            (new_text, new_done, todo_id),
        ).fetchone()
    logger.info("Updated todo %s", todo_id)

    background_tasks.add_task(events.publish, "updated", updated)
    return updated
