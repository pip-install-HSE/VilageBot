from peewee import *
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

db = PostgresqlDatabase(os.getenv('POSTGRES_DB'), port=5432,
                        host=os.getenv('POSTGRES_HOST'),
                        user=os.getenv('POSTGRES_USER'),
                        password=os.getenv('POSTGRES_PASSWORD'))


class User(Model):
    tg_id = IntegerField(primary_key=True)
    state = TextField(null=True)
    car = TextField(null=True)
    name = TextField(null=True)
    phone = TextField(null=True, unique=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        db_table = 'user'


class Problem(Model):
    student_id = ForeignKeyField(User, backref='users')
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        db_table = 'problem'


if __name__ == '__main__':
    db.connect()
    db.create_tables([User, Problem])