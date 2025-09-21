🌍 FlexiTrip AI

“Your AI-Powered Travel Companion – Plan Smarter, Travel Better”
📌 LLM Agent + MCP Server + Local + Cloud Ready (Vertex AI + BigQuery)

FlexiTrip AI is a next-generation travel planner that blends an AI agent, an MCP (Model Context Protocol) server, and LLM-driven intelligence with a streamlined Streamlit interface to deliver an end-to-end trip planning experience. The core workflow is simple yet powerful: the AI agent interprets user preferences (budget, duration, travel style, and interests), the MCP server ensures structured data exchange, and a local SQLite database stores trip details, bookings, payments, and analytics. On the front end, users interact with a clean dashboard showing AI-generated itineraries, maps, bookable items, and real-time insights.

🌍 FlexiTrip AI – Intelligent Travel Planner

FlexiTrip AI is an AI-powered travel planning assistant that brings together LLMs, MCP (Model Context Protocol), and data-driven intelligence to simplify and personalize trip planning.
-It provides an end-to-end workflow:
-Users give their preferences (destination, budget, duration, travel style, group size).
-The AI agent generates a customized itinerary.
-The MCP server ensures structured context sharing across modules.
-Trips, bookings, payments, and chat history are stored in a local SQLite database.
-A Streamlit dashboard displays itineraries, maps, bookable items, and insights in real time.

✨ Features

✅ AI-Powered Itinerary Generation – Get detailed trip plans tailored to your budget, style, and interests.
✅ Bookings & Payments Integration – Store booking details, payment status, and confirmations.
✅ MCP Server Context Sharing – Unified pipeline for LLM and agent interactions.
✅ Chat with AI Agent – Ask trip-related queries in a natural conversational flow.
✅ Analytics Dashboard – See trends like popular destinations, average budgets, and booking insights.
✅ Local First, Cloud Ready – Runs locally with SQLite, but designed for scaling on Google Cloud.

flowchart TD
    A[User Input via Streamlit UI] --> B[AI Agent]
    B --> C[MCP Server - Context Sharing]
    C --> D[AI Model - Generate Trip Plan]
    D --> E[TripDatabase - SQLite]
    E --> F[Trips / Bookings / Payments / Analytics Tables]
    E --> G[Streamlit Dashboard Display]
    F --> H[Analytics Dashboard & Insights]

🏗️ Tech Stack

- Frontend → Streamlit
 (interactive dashboard)
AI Agent & MCP → Python-based LLM agent + Model Context Protocol
Database → SQLite (local, file-based DB)
Backend Logic → Custom Python modules (trip_database.py, local_ai_integration.py, ai_agent.py)
Visualization → Plotly, Streamlit Charts
Future Cloud Stack → Google Cloud Vertex AI (LLM training & inference), BigQuery (large-scale analytics)

.

📊 Database Schema (SQLite)

Trips Table → Itineraries, costs, styles, maps, bookable items
Bookings Table → Payment status, confirmation IDs, booking metadata
Chat Messages Table → User queries & AI responses
Analytics Table → Events for insights (trip_created, booking_saved, etc.)

☁️ Future Roadmap (Cloud & Scaling)

🔹 Vertex AI Integration – Train and deploy scalable LLMs for smarter, context-aware trip planning.
🔹 BigQuery Analytics – Large-scale storage & querying of millions of trips for real-time insights.
🔹 Payment Gateway APIs – Direct integration with UPI, Stripe, or Razorpay.
🔹 Multi-User Accounts – Secure login, profiles, and cross-device sync.
🔹 Marketplace Integration – Pull real-time data from hotel, flight, and tour APIs.

📖 Why FlexiTrip AI?

Travel planning is traditionally fragmented across search engines, booking sites, and scattered itineraries. FlexiTrip AI brings everything together: AI understands your preferences, suggests optimized plans, stores your bookings, and even learns from your feedback. With LLMs + MCP + Cloud-ready design, it’s not just a trip planner—it’s a step toward an intelligent travel assistant at scale.  

📂 Project Structure
flexitrip-ai/
│── app.py                # Streamlit frontend UI
│── mcp_server.py         # MCP tools for AI-agent (weather, hotels, events, routes)
│── ai_agent.py           # AI logic & context-aware trip planner
│── database.py           # SQLite DB for trips, users, bookings
│── maps_integration.py   # Maps + route optimization
│── payment_system.py     # Booking & payment handling
│── requirements.txt      # Python dependencies
│── README.md             # Project documentation



📂 Project Files  

- app.py → The main Streamlit app (frontend UI).  
- ai_agent.py → The AI brain that generates trip plans.  
- mcp_server.py → Tools to fetch real-time data (weather, hotels, events, maps).  
- database.py → Saves trips, bookings, and analytics in SQLite.  
- maps_integration.py → Route optimization and map visuals.  
- payment_system.py → Handles booking + payment details.  
