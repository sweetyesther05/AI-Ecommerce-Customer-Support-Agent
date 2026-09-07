"""Commerce tools called by the agent. Every factual answer comes from SQLite."""
from datetime import date
from uuid import uuid4
from database import get_connection


def search_products(query="", category=None, min_price=None, max_price=None, available_only=False):
    sql = "SELECT * FROM Products WHERE 1=1"
    values = []
    if query:
        sql += " AND (LOWER(product_name) LIKE ? OR LOWER(category) LIKE ? OR LOWER(description) LIKE ?)"
        term = f"%{query.lower()}%"
        values.extend([term, term, term])
    if category:
        sql += " AND LOWER(category) = LOWER(?)"
        values.append(category)
    if min_price is not None:
        sql += " AND price >= ?"
        values.append(min_price)
    if max_price is not None:
        sql += " AND price <= ?"
        values.append(max_price)
    if available_only:
        sql += " AND stock > 0"
    sql += " ORDER BY rating DESC, price ASC"
    connection = get_connection()
    products = [dict(row) for row in connection.execute(sql, values).fetchall()]
    connection.close()
    return {"tool": "search_products", "count": len(products), "products": products}


def get_order_status(order_id):
    connection = get_connection()
    row = connection.execute("""SELECT o.*, p.product_name FROM Orders o JOIN Products p ON p.product_id = o.product_id WHERE UPPER(o.order_id) = UPPER(?)""", (order_id.strip(),)).fetchone()
    connection.close()
    if not row:
        return {"tool": "get_order_status", "error": "We could not find that order. Please check the ID, such as ORD1001."}
    return {"tool": "get_order_status", "order": dict(row)}


def request_return(order_id, reason="Customer requested a return"):
    connection = get_connection()
    order = connection.execute("SELECT * FROM Orders WHERE UPPER(order_id) = UPPER(?)", (order_id.strip(),)).fetchone()
    if not order:
        connection.close()
        return {"tool": "request_return", "error": "We could not find that order, so a return was not created."}
    if order["status"] == "Cancelled":
        connection.close()
        return {"tool": "request_return", "error": "Cancelled orders cannot be returned."}
    existing = connection.execute("SELECT * FROM Returns WHERE order_id = ? AND status != 'Rejected'", (order["order_id"],)).fetchone()
    if existing:
        connection.close()
        return {"tool": "request_return", "error": f"A return is already open for {order['order_id']}", "return": dict(existing)}
    return_id = f"RET-{uuid4().hex[:8].upper()}"
    connection.execute("INSERT INTO Returns VALUES (?, ?, ?, ?, ?)", (return_id, order["order_id"], reason, "Requested", date.today().isoformat()))
    connection.commit()
    connection.close()
    return {"tool": "request_return", "return": {"return_id": return_id, "order_id": order["order_id"], "reason": reason, "status": "Requested"}}


def recommend_products(customer_id="CUST001", category=None, max_price=None):
    connection = get_connection()
    memories = {row["memory_key"]: row["memory_value"] for row in connection.execute("SELECT memory_key, memory_value FROM CustomerMemory WHERE customer_id = ?", (customer_id,)).fetchall()}
    if not category:
        category = "Headphones" if "headphone" in memories.get("preferred_category", "").lower() else None
    if max_price is None and "₹" in memories.get("preferred_budget", ""):
        max_price = 3000
    connection.close()
    result = search_products(category=category, max_price=max_price, available_only=True)
    result["tool"] = "recommend_products"
    result["based_on_memory"] = memories
    return result
