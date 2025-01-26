import json

# Read the original JSON file
with open("db_utf8.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Write back the data as a new JSON file
with open("cleaned_db.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

