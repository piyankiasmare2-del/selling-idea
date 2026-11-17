from flask import Flask, request, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)
DATABASE = "selling_idea.db"

def connect_db():
    return sqlite3.connect(DATABASE)

def setup_database():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                seller TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/ideas", methods=["GET"])
def get_ideas():
    with connect_db() as db:
        rows = db.execute(
            "SELECT id, title, seller, category, description, price FROM ideas"
        ).fetchall()

    return jsonify([
        {
            "id": r[0],
            "title": r[1],
            "seller": r[2],
            "category": r[3],
            "description": r[4],
            "price": r[5]
        } for r in rows
    ])

@app.route("/ideas", methods=["POST"])
def add_idea():
    data = request.get_json(silent=True) or {}
    required = ["title", "seller", "category", "description", "price"]

    if any(not data.get(field) for field in required):
        return jsonify({"error": "Complete all fields"}), 400

    try:
        price = float(data["price"])
        if price <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid price"}), 400

    with connect_db() as db:
        cursor = db.execute(
            """INSERT INTO ideas
            (title, seller, category, description, price)
            VALUES (?, ?, ?, ?, ?)""",
            (data["title"], data["seller"], data["category"],
             data["description"], price)
        )
        idea_id = cursor.lastrowid

    return jsonify({"message": "Idea submitted", "id": idea_id}), 201

if __name__ == "__main__":
    setup_database()
    app.run(host="0.0.0.0", port=8000, debug=False)
