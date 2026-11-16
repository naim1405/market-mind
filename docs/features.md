# MarketMindAI — F-Commerce Order, Margin & Courier Copilot

## 1. Project Introduction

**What it is:**  
MarketMindAI is an AI-powered operations and sales copilot built specifically for Bangladeshi **F-commerce** (Facebook & Instagram) shops handling high volumes of customer DMs and courier deliveries.

**Who it is for:**  
Small-to-mid-sized online shop owners and page moderators in Bangladesh who currently manage product inquiries, price bargaining, stock tracking, order entry, and courier parcel booking manually across Messenger DMs, Excel sheets, and courier portals.

**The problem it solves:**  
F-commerce sellers lose hours every day replying to *"Price please?"*, negotiating discounts manually, double-checking stock so they don't oversell, calculating Inside/Outside Dhaka delivery charges, booking parcels one by one, and answering *"Where is my parcel?"* messages. Moderators also accidentally give discounts below cost when bargaining quickly.

**What our product does:**  
MarketMindAI automates the core F-commerce workflow in one place:
- Reads customer messages, identifies products, checks real-time stock, and handles **margin-safe bargaining** against hidden merchant floor prices.
- Confirms orders, deducts stock, calculates zone-based delivery totals, books courier parcels with tracking IDs, and answers parcel status queries.
- Answers delivery, return, sizing, and care questions accurately from the shop's policy knowledge base (and honestly says when something isn't covered).
- Gives the shop owner an **MCP-powered operations interface** to monitor low stock, dispatch pending parcels, and review daily shop operations.

**Business model (Sellability):**  
Monthly B2B SaaS subscription (e.g., ৳1,500–৳3,000/month per Facebook page depending on order volume), replacing manual Excel tracking and repetitive moderator work while protecting profit margins.

> **Evaluation targets:** **A. Project Idea & Originality (10 marks)** & **E. Sellable Project (8 marks)**

---

## 2. Feature List & Evaluation Mapping

### Feature 1: Role-Based Shop & Customer Accounts
- User registration, login, and profile endpoint (`/api/v1/auth/...`) with secure password hashing and expiring JWT tokens.
- Two database-backed roles: **`admin`** (shop owner/moderator) and **`customer`** (buyer).
- All catalog modifications, pricing/margin settings, and parcel status updates are restricted to `admin` only; invalid credentials return a uniform error without leaking details.
- **Targets:**
  - **B10** — Authentication & Authorization (7 marks)
  - **B5** — Error Handling & Status Codes (3 marks)
  - **E** — Realistic roles (part of 8 marks)

---

### Feature 2: Product Catalog & Hidden Margin Guardrails
- Full CRUD API for shop products with search and filtering (by keyword, category, and in-stock availability).
- Realistic Bangladeshi F-commerce product fields: SKU, product name, category, public `selling_price`, merchant-only `min_floor_price`, `max_discount_pct`, and live `stock_qty`.
- Pre-populated with realistic sample products (not `test1`/`test2`), managed through database migrations and a seed script.
- **Targets:**
  - **B3** — Database, Migrations & Seeding (5 marks)
  - **B4** — Domain API with full CRUD & filtering (4 marks)
  - **B10** — Admin-only domain writes (part of 7 marks)
  - **E** — Realistic data fields & ready-to-show demo (part of 8 marks)

---

### Feature 3: Role-Aware Multi-Turn AI Chat (Customer & Owner Modes)
- Dedicated LLM chat endpoint supporting multi-turn conversation history and direct tool calling.
- **Customer mode:** Helps buyers check stock, negotiate prices, confirm orders, ask shop policies, and track parcels.
- **Owner mode (`admin`):** Lets the shop owner ask operational questions (e.g., *"How is stock?"*, *"Any pending dispatches?"*) directly inside the app using seller-only tools.
- Guided by a strict system prompt defining the agent's boundaries—keeping responses helpful, concise, and bound to verified store data (never guessing stock or leaking hidden floor prices).
- **Targets:**
  - **B6** — LLM Chat with integration layer, system prompt & multi-turn (6 marks)
  - **A** — Differentiates from a generic "shopping chatbot" via seller margin & courier ops focus (10 marks)

---

### Feature 4: Smart Product Lookup & Margin-Safe Bargaining (DB Tools)
- **Inventory & Price Tool:** Identifies the product mentioned in a customer message and fetches real-time stock and selling price from PostgreSQL.
- **Bargain Evaluation Tool:** When a customer proposes a price or asks for a discount, compares the offer against the product's hidden `min_floor_price` and `max_discount_pct` in the database, returning an accept, smart counter-offer, or polite decline—without exposing the floor price.
- **Targets:**
  - **B7** — Tool Calling with real DB-backed tools (7 marks)
  - **A** — Unique domain twist for F-commerce (10 marks)
  - **E** — Saves money & prevents under-margin sales (part of 8 marks)

---

### Feature 5: Order Confirmation, Courier Booking & Parcel Tracking (DB Tools)
- **Order & Parcel Booking Tool:** Confirms an order at the agreed price, checks and deducts stock, applies Dhaka Inside / Sub-Dhaka / Outside Dhaka delivery charges, creates an order + parcel record, and returns a tracking ID (built around a clean courier adapter pattern).
- **Parcel Tracking Tool:** Extracts a tracking ID from a customer message and returns live parcel status (`booked`, `in_transit`, `delivered`, `returned`), courier name, and order summary.
- **Targets:**
  - **B7** — Tool Calling with real DB-backed tools (7 marks)
  - **B3** — Multi-table relational workflow (`users`, `products`, `orders`, `parcels`) (5 marks)
  - **E** — Directly replaces manual Excel + courier portal entry (part of 8 marks)

---

### Feature 6: Shop Policy, Delivery & Sizing Knowledge Base (RAG)
- Ingests shop reference documents into `pgvector`—covering delivery zone rates & timelines, return/exchange policies, size guides, and care/warranty FAQs.
- Answers customer policy questions strictly from retrieved chunks.
- Explicitly informs the user when nothing relevant is found in the knowledge base (e.g., off-topic or unsupported questions).
- **Targets:**
  - **B8** — RAG with `pgvector`, ingest script, grounded answers & honest fallback (8 marks)

---

### Feature 7: Seller Operations MCP Server
- Exposes store operations to external AI clients (e.g., Claude Desktop, Cursor, MCP Inspector) over both **HTTP (`/mcp`)** and **`stdio`**, reusing the app's core services and database:
  - **Tools (2+):** Book/dispatch parcel for a confirmed order, check low-stock SKUs below a threshold, look up parcel status.
  - **Resource (1):** Live feed of confirmed orders awaiting courier dispatch.
  - **Prompt (1):** Daily shop ops & low-stock briefing prompt for the merchant.
- **Targets:**
  - **B9** — MCP Server (8 marks)

---

### Feature 8: Clean Web Frontend
- User-friendly interface demonstrating the full product end-to-end:
  - Login/registration and role awareness.
  - Interactive **AI Chat** for customer inquiries, bargaining, order booking, policy Q&A, and parcel tracking.
  - **Shop Ops / Catalog View** for browsing products, reviewing orders/parcels, and managing inventory as admin.
- **Targets:**
  - **C5** — UI Frontend (4 marks)
  - **C1 & C3** — Overview & Live Demo readiness (part of 15-mark Video section)
  - **E** — Ready to show end-to-end (part of 8 marks)

---

### Feature 9: Clean Architecture, Error Handling, Docker & Documentation
- Clean modular, layered backend structure with dependency injection, strict environment validation (refuses startup on missing secrets), and standardized HTTP error responses (no leaked tracebacks or raw DB errors).
- One-command **Docker Compose** setup launching the backend, PostgreSQL (`pgvector`), and embedding service.
- Clear README with setup commands, sample requests, live Swagger link (`/docs`), demo video link, and tidy commit history.
- **Targets:**
  - **B1** — Project Setup (3 marks)
  - **B2** — Layered Module Structure (4 marks)
  - **B5** — Error Handling & Status Codes (3 marks)
  - **B11** — Docker & Docker Compose (5 marks)
  - **D** — README & Git Hygiene (7 marks)
  - **C2 & C4** — Clear DataFlow & Code Walkthrough (part of 15-mark Video section)

---

## 3. Quick Rubric Coverage Summary (100 Marks)

| Rubric Area | Marks | Covered By |
| :--- | :---: | :--- |
| **A.** Project idea & originality | 10 | Margin-guard bargaining + courier ops F-commerce copilot |
| **B1–B5.** Setup, Structure, DB, CRUD API, Errors | 19 | Modular FastAPI + Postgres/Alembic + Product/Order/Parcel APIs |
| **B6–B7.** Multi-turn LLM Chat + DB Tools | 13 | Assistant chat + Stock, Bargain, Order/Parcel & Tracking tools |
| **B8.** RAG (`pgvector`) | 8 | Delivery, return & sizing policy ingestion + honest fallback |
| **B9.** MCP Server (`/mcp` + `stdio`) | 8 | Seller ops tools, pending-dispatch resource, daily brief prompt |
| **B10–B11.** Auth & Docker | 12 | JWT + Argon2/bcrypt + `admin`/`customer` roles + full Compose stack |
| **C1–C5.** Video & UI Frontend | 15 | Clean web UI + clear 5-flow demo & walkthrough |
| **D.** README & Git hygiene | 7 | Clean incremental commits + full setup/demo README |
| **E.** Sellable project | 8 | Clear BD F-commerce buyer, SaaS pricing, realistic data & workflow |
| **Total** | **100** | **100% Covered** |
