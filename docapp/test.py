import pymongo
from pymongo import MongoClient
cluster = pymongo.MongoClient("mongodb+srv://Akash:12345@cluster0-7trci.mongodb.net/test?retryWrites=true&w=majority")
db = cluster.docs
collection = db["document"]
post = {"_line":0,"_string":"abcd"}
post_count=collection.count_documents({})