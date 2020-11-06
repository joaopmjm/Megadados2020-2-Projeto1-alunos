# pylint: disable=missing-module-docstring, missing-function-docstring, missing-class-docstring
import json
import uuid

from functools import lru_cache

import mysql.connector as conn

from fastapi import Depends

from utils.utils import get_config_filename, get_app_secrets_filename

from .models import Task, User


class DBSession:
    def __init__(self, connection: conn.MySQLConnection):
        self.connection = connection

    def read_tasks(self, completed: bool = None, owner_uuid: str = None):
        query = 'SELECT BIN_TO_UUID(uuid), description, completed FROM tasks'
        if completed is not None:
            query += ' WHERE completed = '
            if completed:
                query += 'True'
            else:
                query += 'False'
        if completed is not None and owner_uuid is not "":
            query += " AND "

        if owner_uuid is not None:
            query += " WHERE owner_uuid = UUID_TO_BIN(%s)"

        with self.connection.cursor() as cursor:
            cursor.execute(query, owner_uuid)
            db_results = cursor.fetchall()

        return {
            uuid_: Task(
                description=field_description,
                completed=bool(field_completed),
            )
            for uuid_, field_description, field_completed in db_results
        }

    def create_task(self, item: Task):
        uuid_ = uuid.uuid4()

        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO tasks VALUES (UUID_TO_BIN(%s), %s, %s, %s)',
                (str(uuid_), item.description, item.completed, item.owner_uuid),
            )
        self.connection.commit()

        return uuid_

    def read_task(self, uuid_: uuid.UUID, owner_uuid):
        if not self.__task_exists(uuid_):
            raise KeyError()

        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT description, completed
                FROM tasks
                WHERE uuid = UUID_TO_BIN(%s) AND owner_uuid=UUID_TO_BIN(%s)
                ''',
                (str(uuid_), owner_uuid),
            )
            result = cursor.fetchone()

        return Task(description=result[0], completed=bool(result[1]))

    def replace_task(self, uuid_, item: Task, owner_uuid):
        if not self.__task_exists(uuid_):
            raise KeyError()

        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE tasks SET description=%s, completed=%s
                WHERE uuid=UUID_TO_BIN(%s) AND owner_uuid=UUID_TO_BIN(%s)
                ''',
                (item.description, item.completed, str(uuid_), owner_uuid),
            )
        self.connection.commit()

    def remove_task(self, uuid_, owner_uuid):
        if not self.__task_exists(uuid_):
            raise KeyError()

        with self.connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM tasks WHERE uuid=UUID_TO_BIN(%s) AND owner_uuid=UUID_TO_BIN(%s)',
                (str(uuid_), owner_uuid),
            )
        self.connection.commit()

    def remove_all_tasks(self):
        with self.connection.cursor() as cursor:
            cursor.execute('DELETE FROM tasks')
        self.connection.commit()

    def __task_exists(self, uuid_: uuid.UUID):
        with self.connection.cursor() as cursor:
            cursor.execute(
                '''
                SELECT EXISTS(
                    SELECT 1 FROM tasks WHERE uuid=UUID_TO_BIN(%s)
                )
                ''',
                (str(uuid_), ),
            )
            results = cursor.fetchone()
            found = bool(results[0])

        return found

    def create_user(self, item: User):
        uuid_ = uuid.uuid4()

        with self.connection.cursor() as cursor:
            cursor.execute(
                'INSERT INTO users VALUES (UUID_TO_BIN(%s), %s)',
                (str(uuid_),  item.name),
            )
        self.connection.commit()

        return uuid_

    def delete_user(self, owner_uuid):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'DELETE FROM users WHERE owner_uuid=UUID_TO_BIN(%s)',
                (owner_uuid),
            )
        self.connection.commit()

        return 200

    def update_user(self, name: str, owner_uuid):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'UPDATE users SET name=%s WHERE owner_uuid=UUID_TO_BIN(%s)',
                (name, owner_uuid),
            )
        self.connection.commit()

        return 200

    def read_user(self, owner_uuid):
        with self.connection.cursor() as cursor:
            cursor.execute(
                'SELECT name FROM users WHERE owner_uuid=UUID_TO_BIN(%s)',
                (owner_uuid),
            )
        self.connection.commit()
        result = cursor.fetchone()

        return User(name=result[0])


@lru_cache
def get_credentials(
        config_file_name: str = Depends(get_config_filename),
        secrets_file_name: str = Depends(get_app_secrets_filename),
):
    with open(config_file_name, 'r') as file:
        config = json.load(file)
    with open(secrets_file_name, 'r') as file:
        secrets = json.load(file)
    return {
        'user': secrets['user'],
        'password': secrets['password'],
        'host': config['db_host'],
        'database': config['database'],
    }


def get_db(credentials: dict = Depends(get_credentials)):
    try:
        connection = conn.connect(**credentials)
        yield DBSession(connection)
    finally:
        connection.close()
