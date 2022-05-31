from os import getenv

from pymongo import MongoClient


client = MongoClient(getenv('MONGODB_URL') or 'localhost')
db = client.AvezorBot
aiogram_bucket = db.aiogram_bucket