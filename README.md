# AI E-commerce Customer Support Agent

A student-friendly full-stack demo showing an AI shopping assistant with **tool calling** and **customer memory**. The React frontend talks to a modular Flask + SQLite backend through REST APIs. It uses mock commerce data: no real payments, shipping, or customer data.

## Project structure

```text
NM/
├── app.py                 # Flask REST API and built-frontend server
├── agent.py               # Intent routing and response composition
├── database.py            # SQLite schema and sample data
├── memory.py              # CustomerMemory read/write helpers
├── tools.py               # search, order, return, recommendation tools
├── requirements.txt
├── .env.example
├── ecommerce.db           # Created by database.py/app.py on first run
├── src/
│   ├── App.tsx            # Customer chatbot UI
│   ├── App.css            # Responsive visual design
│   └── index.css
└── vite.config.ts         # `/api` proxy to Flask during development
```

## Installation

### Backend

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
python database.py
```

### Frontend

```powershell
npm install
```

## Run in development

Use two terminals:

```powershell
# Terminal 1
.venv\Scripts\activate
python app.py
```

```powershell
# Terminal 2
npm run dev
```

Open the Vite URL shown in the terminal, usually `http://localhost:5173`.

For a single Flask-served build:

```powershell
npm run build
.venv\Scripts\activate
python app.py
```

Then open `http://127.0.0.1:5000`.

## REST API

- `POST /api/chat` accepts `{ "message": "...", "customer_id": "CUST001" }` and routes to the appropriate tool.
- `GET /api/products?q=headphones&max_price=3000&available=true` searches products.
- `GET /api/orders/ORD1001` retrieves order status.
- `POST /api/returns` accepts `{ "order_id": "ORD1001", "reason": "..." }`.
- `GET /api/recommendations?customer_id=CUST001` uses memory to recommend in-stock products.
- `GET /api/memory/CUST001` displays stored preferences.
- `GET /api/health` confirms the backend is running.

## How tool calling works

`agent.py` performs simple, explainable intent routing suitable for a college demo. Product language calls `search_products`, order language calls `get_order_status`, return language calls `request_return`, and recommendation language calls `recommend_products`. Each tool queries SQLite and returns structured data. The assistant response is composed from that result, so it does not invent prices, stock, order status, or return IDs.

The routing layer is intentionally provider-independent. An LLM provider can be added later by replacing `route_message` with a function-calling loop while keeping the same tool functions and schemas. API keys belong in `.env`, never frontend code.

## How memory works

`CustomerMemory` stores non-sensitive facts as `(customer_id, memory_key, memory_value, created_at)`. Messages containing preferences such as “I prefer headphones under ₹3000” are parsed by `memory.py`, upserted into SQLite, and included when `recommend_products` runs. The UI shows the stored memory so the behavior is easy to demonstrate.

## Demo steps

1. Ask: `Find wireless headphones under ₹3000`.
2. Show the Product Search tool result and the product cards.
3. Ask: `Where is my order ORD1001?`.
4. Show the Out for Delivery status and estimated date.
5. Ask: `I want to return order ORD1001 because I don't like it.`.
6. Show the generated `RET-...` return request.
7. Ask: `I usually prefer products below ₹3000`.
8. Ask: `Recommend something for me` and show the recommendation tool using memory.

## Sample data

The seeded database contains headphones, running shoes, laptops, and a monitor; customers `CUST001` and `CUST002`; orders `ORD1001` to `ORD1003`; and two initial preferences for `CUST001`.

## Future enhancements

- Replace deterministic routing with an LLM function-calling loop.
- Add authentication and customer sessions.
- Add pagination and admin product management.
- Add real order webhooks and carrier integrations.
- Add automated tests for each tool and API endpoint.

