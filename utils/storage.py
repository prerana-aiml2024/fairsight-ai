import json
import os
import base64
from datetime import date, datetime

DB_PATH = "fairsight_db.json"

def load_db():
    if not os.path.exists(DB_PATH):
        return {"users": {}, "histories": {}}
    try:
        with open(DB_PATH, "r", encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception:
        return {"users": {}, "histories": {}}

def save_db(data):
    # Convert date objects to strings for JSON serialization
    def serializer(obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        return str(obj)

    try:
        with open(DB_PATH, "w", encoding='utf-8') as f:
            json.dump(data, f, default=serializer, indent=4)
    except Exception as e:
        print(f"Error saving database: {e}")

def get_user_data(email):
    db = load_db()
    user = db["users"].get(email, {})
    if not user:
        return None
        
    # Convert DOB back to date object
    if "dob" in user and isinstance(user["dob"], str):
        try:
            user["dob"] = date.fromisoformat(user["dob"])
        except ValueError:
            user["dob"] = date(1990, 1, 1)
    
    # Convert profile_pic back to bytes
    if "profile_pic" in user and user["profile_pic"]:
        try:
            user["profile_pic"] = base64.b64decode(user["profile_pic"])
        except Exception:
            user["profile_pic"] = None
            
    return user

def verify_user(email, password):
    db = load_db()
    user = db["users"].get(email)
    if user and user.get("password") == password:
        return True
    return False

def update_user_data(email, updates):
    db = load_db()
    if email not in db["users"]:
        db["users"][email] = {}
    
    user = db["users"][email]
    user.update(updates)
    
    # Re-save the whole DB
    save_db(db)

def get_user_history(email):
    db = load_db()
    return db["histories"].get(email, [])

def add_history_entry(email, entry):
    db = load_db()
    if email not in db["histories"]:
        db["histories"][email] = []
    
    # Ensure entry has date
    if 'date' not in entry:
        entry['date'] = datetime.now().isoformat()
        
    db["histories"][email].append(entry)
    save_db(db)
