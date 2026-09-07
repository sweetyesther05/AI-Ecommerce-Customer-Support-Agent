"""Flask REST API for the AI E-commerce Customer Support Agent."""
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from agent import route_message
from database import get_connection, init_db
from memory import get_memories
from tools import get_order_status, recommend_products, request_return, search_products

ROOT = Path(__file__).parent
app = Flask(__name__, static_folder="dist", static_url_path="")
init_db()


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "ecommerce-agent"})


@app.post("/api/chat")
def chat():
    body = request.get_json(silent=True) or {}
    message = body.get("message", "")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Please enter a message."}), 400
    context = body.get("context", "")
    if not isinstance(context, str):
        context = ""
    return jsonify(route_message(message[:1000], body.get("customer_id", "CUST001"), context[:3000]))


@app.get("/api/products")
def products():
    return jsonify(search_products(request.args.get("q", ""), request.args.get("category"), request.args.get("min_price", type=float), request.args.get("max_price", type=float), request.args.get("available", "false").lower() == "true"))


@app.get("/api/orders/<order_id>")
def order_status(order_id):
    result = get_order_status(order_id)
    return jsonify(result), 404 if "error" in result else 200


@app.post("/api/returns")
def returns():
    body = request.get_json(silent=True) or {}
    order_id = body.get("order_id", "")
    if not isinstance(order_id, str) or not order_id.strip():
        return jsonify({"error": "An order ID is required."}), 400
    result = request_return(order_id, body.get("reason", "Customer requested a return"))
    return jsonify(result), 400 if "error" in result else 201


@app.get("/api/recommendations")
def recommendations():
    return jsonify(recommend_products(request.args.get("customer_id", "CUST001"), request.args.get("category"), request.args.get("max_price", type=float)))


@app.get("/api/memory/<customer_id>")
def memory(customer_id):
    return jsonify({"customer_id": customer_id, "memories": get_memories(customer_id)})


@app.get("/api/orders")
def orders():
    connection = get_connection()
    rows = [dict(row) for row in connection.execute("SELECT o.*, p.product_name FROM Orders o JOIN Products p ON p.product_id = o.product_id ORDER BY o.order_date DESC").fetchall()]
    connection.close()
    return jsonify({"orders": rows})


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def frontend(path):
    if app.static_folder and (ROOT / "dist" / path).is_file():
        return send_from_directory(app.static_folder, path)
    if (ROOT / "dist" / "index.html").is_file():
        return send_from_directory(app.static_folder, "index.html")
    return jsonify({"message": "Frontend is not built. Run npm run build first."}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
