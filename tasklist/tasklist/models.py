# pylint: disable=missing-module-docstring,missing-class-docstring
from typing import Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from uuid import uuid4

# pylint: disable=too-few-public-methods

owner_uuid_str = str(uuid4)

class Task(BaseModel):
    description: Optional[str] = Field(
        'no description',
        title='Task description',
        max_length=1024,
    )
    completed: Optional[bool] = Field(
        False,
        title='Shows whether the task was completed',
    )
    owner_uuid: Optional[str] = Field(
        None,
        title="Owner UUID",
        max_length=32,
    )

    class Config:
        schema_extra = {
            'example': {
                'description': 'Buy baby diapers',
                'completed': False,
                "owner_uuid": '1b57f7a1-22df-4cb4-b6b6-3356e1cd0be7'
            }
        }

class User(BaseModel):
    name: Optional[str] = Field(
        'no name',
        title='user name',
        max_length=1024,
    )
    owner_uuid: Optional[str] = Field(
        None,
        title="Owner UUID",
        max_length=32,
    )

    class Config:
        schema_extra = {
            'example': {
                'name': 'Jua1mmmmmmm',
                "owner_uuid": '1b57f7a1-22df-4cb4-b6b6-3356e1cd0be7'
            }
        }