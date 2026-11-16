# MarketMindAI

**AI-Powered Order, Margin & Courier Copilot for Bangladeshi F-Commerce Shops**

---

## Overview

Thousands of Facebook and Instagram commerce (F-commerce) pages in Bangladesh handle orders completely manually—replying to *"Price please?"* in DMs, tracking stock in notebooks or Excel, negotiating discounts on the fly, calculating Inside/Outside Dhaka delivery fees, booking courier parcels one by one, and answering endless *"Where is my parcel?"* updates.

**MarketMindAI** automates this workflow for small-to-mid-sized F-commerce sellers. It combines an AI sales & support assistant for customers with an operations copilot for shop owners—powered by live inventory data, margin-safe bargaining rules, shop policy knowledge (RAG), and an MCP server.

---

## Who It Is For

- **Primary Users:** Bangladeshi F-commerce shop owners and page moderators managing daily Messenger/DM inquiries, inventory, and parcel dispatches.
- **Secondary Users:** Online shoppers asking about products, negotiating prices, placing orders, checking store policies, and tracking their parcels.

---

## Core Capabilities (Planned)

- **Smart Inventory & Price Lookup:** Identifies products from natural customer messages and checks live stock and pricing.
- **Margin-Safe Bargaining:** Evaluates customer discount offers against merchant-defined hidden floor prices—accepting valid deals or issuing smart counter-offers without leaking cost limits.
- **Order Confirmation & Parcel Tracking:** Confirms orders, deducts inventory, applies zone-based delivery charges (Inside/Sub/Outside Dhaka), books parcels with tracking IDs, and reports live parcel status.
- **Shop Policy & Sizing Q&A (RAG):** Answers delivery, return/exchange, and sizing questions grounded in the store's knowledge base—and clearly states when something isn't covered.
- **Owner Copilot & MCP Server:** Lets shop owners check stock, review orders awaiting dispatch, and manage operations either in-app or from external AI clients (via MCP over HTTP `/mcp` and `stdio`).
- **Role-Based Access Control:** Separate `admin` (shop owner) and `customer` roles protecting catalog, pricing limits, and parcel updates.

---

## Planned Tech Stack

- **Backend:** Python, FastAPI, Pydantic
- **Database & Vector Search:** PostgreSQL, SQLAlchemy (async), Alembic, `pgvector`
- **AI & Integrations:** Multi-turn LLM chat with DB-backed tool calling, RAG, and an MCP server
- **Auth & Deployment:** JWT authentication, Argon2/bcrypt password hashing, Docker & Docker Compose

---

## Status & Links

> *Initial project scope—setup instructions, API examples, and links will be updated as modules are implemented.*

- **Live API Docs (Swagger):** *TBD (Render deployment)*
- **Demo Video:** *TBD*
