from peewee import *
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

db = PostgresqlDatabase(os.getenv('POSTGRES_DB'), port=5432,
                        host=os.getenv('POSTGRES_HOST'),
                        user=os.getenv('POSTGRES_USER'),
                        password=os.getenv('POSTGRES_PASSWORD'))


class Users(Model):
    tg_id = IntegerField(primary_key=True)
    status = IntegerField(null=True)

    class Meta:
        database = db
        db_table = 'practice'


if __name__ == '__main__':
    db.connect()
    db.create_tables([Users])
