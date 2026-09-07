"""Intent routing for the demo agent. Replace route_message with an LLM tool loop when an API key is configured."""
import re
from memory import get_memories, learn_from_message
from tools import get_order_status, recommend_products, request_return, search_products


def _money(message):
    match = re.search(r"(?:₹|rs\.?|under|below)\s*([\d,]+)", message.lower())
    return float(match.group(1).replace(",", "")) if match else None


def route_message(message, customer_id="CUST001", context=""):
    message = message.strip()
    if not message:
        return {"reply": "Please type a question and I will help with products, orders, returns, or recommendations.", "tool": None, "memory": []}
    memory_updates = learn_from_message(customer_id, message)
    lowered = message.lower()
    conversation_text = f"{message} {context}".lower()
    order_match = re.search(r"\b(?:ord(?:er)?[-\s]?)?([0-9]{4,})\b", conversation_text, re.I)
    order_id = f"ORD{order_match.group(1)}" if order_match else None
    if any(word in lowered for word in ("return", "refund", "send back", "exchange")):
        result = request_return(order_id or "", message)
        if "error" in result:
            reply = result["error"]
        else:
            reply = f"Your return request {result['return']['return_id']} has been created for {result['return']['order_id']}. The status is {result['return']['status']}."
    elif any(word in lowered for word in ("where is", "track", "status", "delivered", "shipped", "order")) and order_id:
        result = get_order_status(order_id)
        if "error" in result:
            reply = result["error"]
        else:
            order = result["order"]
            reply = f"{order['order_id']} is currently {order['status']}. Estimated delivery is {order['estimated_delivery']}."
    elif any(word in lowered for word in ("recommend", "suggest", "for me", "what should")):
        result = recommend_products(customer_id, max_price=_money(message))
        reply = "Based on your saved preferences, here are my recommendations." if result["products"] else "I could not find an in-stock match yet. Try a different budget or category."
    else:
        catalog_terms = next((term for term in ("headphones", "earbuds", "laptops", "running shoes", "monitors") if term in lowered), "")
        result = search_products(catalog_terms, max_price=_money(message), available_only=True)
        if result["count"]:
            reply = f"I found {result['count']} in-stock product(s) matching your request."
        else:
            result = None
            reply = "I can help search products, track an order, create a return, or recommend something from your preferences."
    return {"reply": reply, "tool": result, "memory": memory_updates, "memories": get_memories(customer_id)}
