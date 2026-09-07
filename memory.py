"""Small, explainable customer-memory layer backed by SQLite."""
from database import get_connection


def get_memories(customer_id="CUST001"):
    connection = get_connection()
    rows = connection.execute("SELECT memory_key, memory_value, created_at FROM CustomerMemory WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,)).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def remember(customer_id, memory_key, memory_value):
    connection = get_connection()
    connection.execute("""INSERT INTO CustomerMemory (customer_id, memory_key, memory_value, created_at) VALUES (?, ?, ?, datetime('now')) ON CONFLICT(customer_id, memory_key) DO UPDATE SET memory_value = excluded.memory_value, created_at = excluded.created_at""", (customer_id, memory_key, memory_value))
    connection.commit()
    connection.close()
    return {"memory_key": memory_key, "memory_value": memory_value}


def learn_from_message(customer_id, message):
    lowered = message.lower()
    saved = []
    if "under ₹" in lowered or "below ₹" in lowered:
        budget = lowered.split("₹", 1)[1].split()[0].replace(",", "")
        if budget.isdigit():
            saved.append(remember(customer_id, "preferred_budget", f"Below ₹{budget}"))
    for category in ("headphones", "running shoes", "laptops", "monitors"):
        if category in lowered and ("prefer" in lowered or "usually" in lowered or "like" in lowered):
            saved.append(remember(customer_id, "preferred_category", category.title()))
    return saved
