# pylint: disable=missing-module-docstring, missing-function-docstring, invalid-name
import uuid

from typing import Dict

from fastapi import APIRouter, HTTPException, Depends

from ..database import DBSession, get_db
from ..models import Task

router = APIRouter()

@router.get(
    '',
    summary='read all tasks',
    description='Read all tasks.',
    response_model=Dict[uuid.UUID, Task],
)
async def read_all_tasks(db: DBSession = Depends(get_db)):
    return db.read_all_tasks()


@router.get(
    '/user/{owner_uuid}',
    summary='Reads task list',
    description='Reads the whole task list.',
    response_model=Dict[uuid.UUID, Task],
)
async def read_tasks(completed: bool = None, owner_uuid = uuid.UUID, db: DBSession = Depends(get_db)):
    return db.read_tasks(completed, owner_uuid)


@router.post(
    '',
    summary='Creates a new task',
    description='Creates a new task and returns its UUID.',
    response_model=uuid.UUID,
)
async def create_task(item: Task, db: DBSession = Depends(get_db)):
    return db.create_task(item)


@router.get(
    '/{uuid_}/user/{owner_uuid}',
    summary='Reads task',
    description='Reads task from UUID.',
    response_model=Task,
)
async def read_task(uuid_: uuid.UUID, owner_uuid = uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        return db.read_task(uuid_, owner_uuid)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@router.put(
    '/{uuid_}',
    summary='Replaces a task',
    description='Replaces a task identified by its UUID.',
)
async def replace_task(
        uuid_: uuid.UUID,
        item: Task,
        db: DBSession = Depends(get_db),
):
    try:
        db.replace_task(uuid_, item)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@router.patch(
    '/{uuid_}/user/{owner_uuid}',
    summary='Alters task',
    description='Alters a task identified by its UUID',
)
async def alter_task(
        uuid_: uuid.UUID,
        owner_uuid: uuid.UUID,
        item: Task,
        db: DBSession = Depends(get_db),
):
    try:
        old_item = db.read_task(uuid_, owner_uuid)
        update_data = item.dict(exclude_unset=True)
        new_item = old_item.copy(update=update_data)
        db.replace_task(uuid_, new_item, owner_uuid)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@router.delete(
    '/{uuid_}/user/{owner_uuid}',
    summary='Deletes task',
    description='Deletes a task identified by its UUID',
)
async def remove_task(uuid_: uuid.UUID, owner_uuid: uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        db.remove_task(uuid_, owner_uuid)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@router.delete(
    '/delete/all',
    summary='Deletes all tasks, use with caution',
    description='Deletes all tasks, use with caution',
)
async def remove_all_tasks(db: DBSession = Depends(get_db)):
    db.remove_all_tasks()