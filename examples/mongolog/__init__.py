from pymongo import MongoClient
from datetime import datetime

def auto_int(x):
    return int(x, 0)

class MongoLogger():
    def __init__(self, url = 'localhost', port = 27017, user = 'root', password = 'root', database = 'meteobox', sensor = 'SensorName', collection = "meteoboxData", sensor_type = "SensorType"):
        print(url, port)
        self.db = MongoClient(url, port)
        print(self.db)

        dbnames = self.db.list_database_names()
        if database not in dbnames:
            print("Database is not exist, trying to create")
        self.db = self.db[database]

        if collection not in self.db.list_collection_names():
            print("Colection does not exists")
            #self.db.create_collection(
            #     collection,
            #     {
            #       "timeseries": {
            #          "timeField": "timestamp",
            #          "metaField": "metadata",
            #          #granularity: "hours"
            #       }
            #    }
            #)
        self.col = self.db[collection]
        self.sensor = sensor
        self.type = sensor_type
        
        self.insert_message("{} driver started with sensorID".format(sensor_type, sensor))

    def insert_data(self, values):
        data = {
            "timestamp": datetime.now(),
            "metadata": {"dataId": self.sensor, "type": self.type, "data": "value"},
        }
        d = {**data, **values}
        print(type(d), d)
        return self.col.insert_one(d)

    def insert_message(self, message):
        data = {
            "timestamp": datetime.now(),
            "metadata": {"dataId": self.sensor, "type": self.type, "data": "message"},
            "message": message
        }
        return self.col.insert_one(data)











class InfluxLogger():
    def __init__(self, url = 'localhost', port = 8086, user = 'admin', password = 'admin', database = 'meteobox', sensor = 'SensorName', collection = "meteoboxData", sensor_type = "SensorType"):
        from influxdb import InfluxDBClient
        print(url, port)
        self.col = database
        self.sensor = sensor
        self.type = sensor_type

        from datetime import datetime

        from influxdb_client import InfluxDBClient, Point, WritePrecision
        from influxdb_client.client.write_api import SYNCHRONOUS

        # You can generate a Token from the "Tokens Tab" in the UI"
        token = "FrTdVeNHkBrAe-xWciEiU_XUXOwS33RN61_4Vj47UkGmzwdlF_lJE3C3D6G7Nk1ymeEsrotts1q0DAnQSU95Ow=="
        org = "meteobox"
        bucket = "meteobox"

        self.client = InfluxDBClient(url="http://localhost:8086", token=token)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def insert_data(self, values):
        data = {
            #"tags": self.sensor,
            "time": datetime.now(),
            "tags": {"dataId": self.sensor, "type": self.type, "data": "value"},
            "fields": values,
            "measurement": self.sensor
        }
        #d = {**data, **values}
        self.write_api.write('meteobox', 'meteobox', data)

    def insert_message(self, message):
        data = {
            "timestamp": datetime.now(),
            "metadata": {"dataId": self.sensor, "type": self.type, "data": "message"},
            "message": message
        }
        return self.col.insert_one(data)















import argparse

class loggerArgparse(argparse.ArgumentParser):

    def __init__(self, description = "Pymlab device logger"):
        super(loggerArgparse, self).__init__(description = description)

        self.add_argument("--driver", type=str, default= None)
        self.add_argument("--bus", type=int, default=0)
        self.add_argument("--address", type=auto_int, default = None)
        self.add_argument("--debug", action='store_true')
