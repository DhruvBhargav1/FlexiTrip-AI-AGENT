# mcp_server.py - Our intelligent server
# ----------------------------------------------------------
# This script defines a custom MCP (Model Context Protocol) 
# server that connects AI with external APIs like:
#  - OpenWeather (for weather data)
#  - Eventbrite (for events)
#  - Makcorps (for hotel prices)
#  - OpenRouteService (for route optimization)
#
# The class uses async/await + aiohttp for non-blocking I/O.
# ----------------------------------------------------------

from mcp import Server, types   # MCP framework for defining custom AI tools
import asyncio                  # Async programming in Python
import aiohttp                  # For async HTTP requests
import json                     # For encoding/decoding JSON data


class FlexiTripMCPServer:
    def __init__(self):
        # Initialize our MCP server with the name "flexitrip-ai"
        self.server = Server("flexitrip-ai")
        self.setup_tools()
        
    def setup_tools(self):
        """
        Register available tools so the AI can call them.
        Each tool has:
          - name (string identifier)
          - description (explains what the tool does)
          - handler (function that gets executed)
        """
        self.server.add_tool(
            name="get_real_time_weather",
            description="Get current weather for destination",
            handler=self.get_weather
        )
        
        self.server.add_tool(
            name="search_local_events", 
            description="Find local festivals and events",
            handler=self.search_events
        )
        
        self.server.add_tool(
            name="get_hotel_prices",
            description="Get real-time hotel pricing",
            handler=self.get_hotel_data
        )
        
        self.server.add_tool(
            name="optimize_route",
            description="Optimize travel routes using maps",
            handler=self.optimize_routes
        )
    
    # ---------------- WEATHER TOOL ----------------
    async def get_weather(self, destination: str, dates: str):
        """
        Fetch real-time weather using OpenWeather API.
        - async/await is used for non-blocking HTTP requests
        - aiohttp.ClientSession() creates an async HTTP session
        """
        api_key = "9e68a1ac01c0d574a1141e174727db98"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={destination}&appid={api_key}&units=metric"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:   # Await response
                    if resp.status != 200:
                        return {"error": "weather fetch failed"}
                    
                    # Convert API response to Python dict
                    data = await resp.json()
                    return {
                        "temperature": data["main"]["temp"],
                        "conditions": data["weather"][0]["description"]
                    }
        except Exception:
            return {"error": "weather fetch failed"}
    
    
    # ---------------- EVENTS TOOL ----------------
    async def search_events(self, query, location):
        """
        Search for local events using Eventbrite API.
        Example: "music festival in Delhi".
        """
        url = f"https://www.eventbriteapi.com/v3/events/search/?q={query}&location.address={location}"
        header = {"Authorization": "bearer MNZXL73H3GADKL3SEVVH"}  # Auth token
    
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=header) as resp:
                if resp.status != 200:
                    return {"error": "event fetch failed"}
                data = await resp.json()
                return data  # Returns entire JSON of events
    
    # ---------------- HOTEL TOOL ----------------
    async def get_hotel_data(self, location):
        """
        Fetch real-time hotel pricing and availability from Makcorps API.
        Extract hotel names + geocodes (latitude, longitude).
        """
        url = f"https://api.makcorps.com/free/{location}"
        headers = {
            "Authorization": "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status != 200:
                        return {"error": "hotel fetch failed"}
                    data = await resp.json()
            
            # Extract hotel coordinates
            hotels_with_coords = []
            for hotel in data.get("hotels", []):     # Loop over hotel list
                geocode = hotel.get("geocode", {})   # Safely get geocode dict
                if geocode:
                    hotels_with_coords.append({
                        "name": hotel.get("name"),
                        "lat": geocode.get("latitude"),
                        "lon": geocode.get("longitude")
                    })
            return hotels_with_coords
        except Exception as e:
            return {"error": f"hotel fetch failed: {e}"}

    # ---------------- ROUTE OPTIMIZATION TOOL ----------------
    async def optimize_routes(self, hotel_coords: list):
        """
        Optimize travel route between hotels using OpenRouteService API.
        
        Input format (list of dicts with hotel name + coordinates):
        [
            {"name": "Hotel A", "lat": 28.6448, "lon": 77.2167},
            {"name": "Hotel B", "lat": 28.6501, "lon": 77.2200},
            ...
        ]

        - Converts hotel coords into ORS API format
        - Sends POST request to ORS optimization endpoint
        - Returns optimized travel route
        """
        url = "https://api.openrouteservice.org/v2/optimization"
        api_key = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6..."
        headers = {
            "Authorization": f"Bearer {api_key}",  # Token-based auth
            "Content-Type": "application/json"     # Tell server we send JSON
        }

        # ORS requires coordinates in [longitude, latitude] format
        locations = [[hotel["lon"], hotel["lat"]] for hotel in hotel_coords]

        # ORS needs vehicles + jobs:
        # - vehicles = starting point (driver/car)
        # - jobs = destinations (hotels)
        data = {
            "vehicles": [
                {"id": 1, "profile": "driving-car", "start": locations[0]}
            ],
            "jobs": [
                {"id": i+1, "location": loc} for i, loc in enumerate(locations[1:])
            ]
        }

        # Send POST request to ORS
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(data)) as resp:
                if resp.status != 200:
                    # Capture error message from ORS API
                    text = await resp.text()
                    return {"error": f"route optimization failed: {text}"}
                
                # Parse successful response into Python dict
                return await resp.json()
    