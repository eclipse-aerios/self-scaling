from peewee import *
import os

database = os.environ['MYSQL_DATABASE']
user = os.environ['MYSQL_USER']
password = os.environ['MYSQL_PASSWORD']
host = os.environ['MYSQL_HOST']
port = int(os.environ['MYSQL_PORT'])

db = MySQLDatabase(database, user = user, password = password, host = host, port = port)

class service(Model):
    id = PrimaryKeyField()
    name = CharField()
    infer = BooleanField(default=False)
    class Meta:
        database = db

class serviceComponent(Model):
    id = PrimaryKeyField()
    service_id = ForeignKeyField(service)
    name = CharField()
    infer = BooleanField(default=False)
    class Meta:
        database = db

class data(Model):
    id = PrimaryKeyField()
    service_id = ForeignKeyField(service)
    servicecomponent_id = ForeignKeyField(serviceComponent)
    timestamp = DateTimeField()
    cpu = IntegerField()
    ram = IntegerField()
    real = BooleanField(default=True)
    class Meta:
        database = db