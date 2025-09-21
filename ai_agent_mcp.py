# ai_agent_mcp.py
from mcp_client import MCPClient
import google.generativeai as genai
import os
import asyncio

class FlexiTripAI_MCP:
    def __init__(self):
        # Connect to our MCP server
        self.mcp_client = MCPClient("http://localhost:8000")
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_enhanced_trip_plan(self, destination, duration, budget, interests, travel_dates):
        """Generate trip plan with real-time data"""
        
        # Step 1: Gather real-time context using MCP tools
        context_data = await self.gather_context(destination, interests, travel_dates, budget)
        
        # Step 2: Create enhanced prompt with real data
        enhanced_prompt = self.build_enhanced_prompt(
            destination, duration, budget, interests, context_data
        )
        
        # Step 3: Get AI response with rich context
        response = await self.model.generate_content_async(enhanced_prompt)
        
        # Step 4: Post-process with MCP insights
        final_plan = await self.enhance_with_mcp_insights(response, context_data)
        
        return final_plan
    
    async def gather_context(self, destination, interests, dates, budget):
        """Use MCP tools to gather real-time context"""
        
        # Parallel data gathering using MCP
        context = await asyncio.gather(
            self.mcp_client.call_tool("get_real_time_weather", {
                "destination": destination, 
                "dates": dates
            }),
            self.mcp_client.call_tool("search_local_events", {
                "destination": destination, 
                "interests": interests
            }),
            self.mcp_client.call_tool("get_hotel_prices", {
                "destination": destination, 
                "budget": budget, 
                "dates": dates
            }),
            self.mcp_client.call_tool("optimize_route", {
                "destination": destination, 
                "interests": interests
            })
        )
        
        return {
            "weather": context[0],
            "events": context[1], 
            "hotels": context[2],
            "routes": context[3]
        }
    
    def build_enhanced_prompt(self, destination, duration, budget, interests, context):
        """Build AI prompt with real-time context"""
        
        return f"""
        You are FlexiTrip AI Agent with access to real-time data.
        
        TRIP REQUIREMENTS:
        • Destination: {destination}
        • Duration: {duration} days
        • Budget: ₹{budget:,}
        • Interests: {', '.join(interests)}
        
        REAL-TIME CONTEXT:
        
        WEATHER DATA:
        • Temperature: {context['weather']['temperature']}°C
        • Conditions: {context['weather']['conditions']}
        • Activity recommendations: {context['weather']['recommendations']}
        
        LOCAL EVENTS:
        • Happening during visit: {context['events']['events']}
        • Cultural significance: {context['events']['cultural_significance']}
        
        ACCOMMODATION:
        • Available hotels: {len(context['hotels']['available_hotels'])} options
        • Price range: ₹{context['hotels']['price_trends']['min']} - ₹{context['hotels']['price_trends']['max']}
        • Best deals: {context['hotels']['best_deals']}
        
        OPTIMIZED ROUTES:
        • Efficient route plan: {context['routes']['optimized_path']}
        • Time savings: {context['routes']['time_saved']} hours
        • Hidden gems on route: {context['routes']['hidden_spots']}
        
        Create a detailed itinerary that:
        1. Adapts to current weather conditions
        2. Includes the local events happening during visit
        3. Uses the best hotel deals within budget
        4. Follows the optimized route plan
        5. Incorporates hidden gems discovered through route optimization
        
        Make this trip plan intelligent and adaptive to real-world conditions!
        """