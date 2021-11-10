import json

with open("config.json", "r", encoding="utf-8") as raw_file:
    data = json.load(raw_file)
    secret_key = data["secret_key"]
    SQLALCHEMY_DATABASE_URI = data["SQLALCHEMY_DATABASE_URI"]
    master_password = data["master_password"]

class Config:
    secret_key = secret_key
    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    master_password = master_password
    
    
