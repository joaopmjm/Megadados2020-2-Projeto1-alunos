# pylint: disable=missing-module-docstring, missing-function-docstring, invalid-name
import uuid

from typing import Dict

from fastapi import APIRouter, HTTPException, Depends

from ..database import DBSession, get_db
from ..models import User

router = APIRouter()


@router.post(
    '',
    summary='Creates a new user',
    description='Creates a new user and returns its UUID.',
    response_model=uuid.UUID,
)
async def create_user(item: User, db: DBSession = Depends(get_db)):
    return db.create_user(item)


@router.delete(
    '/{owner_uuid}',
    summary='Deletes user',
    description='Deletes a user identified by its UUID',
)
async def delete_user(owner_uuid: uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        db.delete_user(owner_uuid)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='User not found',
        ) from exception


@router.patch(
    '/{owner_uuid}',
    summary='Alters user name',
    description='Alters a user`s name identified by its UUID',
)
async def alter_user(
        owner_uuid: uuid.UUID,
        item: User,
        db: DBSession = Depends(get_db),
):
    try:
        db.update_user(item, owner_uuid=owner_uuid)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception

@router.get(
    '/{owner_uuid}',
    summary='Reads user name',
    description='Reads user name from UUID.',
    response_model=User,
)
async def read_user(owner_uuid = uuid.UUID, db: DBSession = Depends(get_db)):
    try:
        return db.read_user(owner_uuid)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='User not found',
        ) from exception