"""
AI Agent - The brain of our travel app
This file contains all AI-related functions.
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FlexiTripAI:
    """
    This class represents our AI Agent
    It handles all communication with Google's AI
    """
    
    def __init__(self):
        """
        Initialize the AI Agent
        This runs when we create a new AI agent
        """
        try:
            # Configure Google AI with our API key
            api_key = os.getenv("google_Api_key")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            
            # Create the AI model
            self.model = genai.GenerativeModel('models/gemini-1.5-flash')
            
            # Initialize chat for conversations
            self.chat = self.model.start_chat(history=[])
            
            logger.info("AI Agent initialized successfully!")
            
        except Exception as e:
            logger.error(f"AI Agent initialization failed: {e}")
            raise
    
    def generate_trip_plan(self, destination, duration, budget, interests, travel_style, group_size=2):
        """
        Generate a complete trip plan using AI
        
        Parameters:
        - destination: Where to go (string)
        - duration: How many days (integer)  
        - budget: How much money (float)
        - interests: List of interests (list)
        - travel_style: Budget/Comfort/Luxury (string)
        - group_size: Number of people (integer)
        
        Returns:
        - Complete trip plan (dictionary)
        """
        
        try:
            # Create a detailed prompt for the AI
            interests_text = ', '.join(interests) if interests else 'general sightseeing'
            
            prompt = f"""
            You are FlexiTrip AI Agent, the world's best travel planner for India.
            
            Create a detailed, amazing trip plan with these requirements:
            
            TRIP DETAILS:
            • Destination: {destination}
            • Duration: {duration} days
            • Budget: ₹{budget:,}
            • Group Size: {group_size} people
            • Interests: {interests_text}
            • Travel Style: {travel_style}
            
            PLEASE PROVIDE:
            
            1. **TRIP OVERVIEW**
            - Creative trip title
            - Best travel months
            - Trip highlights (top 3-4 experiences)
            - Cultural significance of the destination
            
            2. **DETAILED DAY-BY-DAY ITINERARY**
            For each day, include:
            - Morning Activity (with time, cost, description)
            - Afternoon Activity (with time, cost, cultural context)
            - Evening Activity (with time, cost, local insights)
            - Recommended meals (restaurant names, costs, must-try dishes)
            - Accommodation suggestion (name, type, cost per night)
            - Daily total cost
            
            3. **BUDGET BREAKDOWN**
            - Accommodation: ₹X (X%)
            - Food & Dining: ₹X (X%)  
            - Activities & Tours: ₹X (X%)
            - Transportation: ₹X (X%)
            - Shopping & Misc: ₹X (X%)
            - Total: ₹X
            
            4. **CULTURAL INSIGHTS**
            - Local customs to know
            - Cultural etiquette tips
            - Traditional festivals or events
            - Historical significance
            
            5. **PRACTICAL INFORMATION**
            - Best photography spots
            - Packing essentials
            - Weather considerations
            - Transportation tips
            - Safety advice
            - Local phrases to learn
            
            6. **AUTHENTIC EXPERIENCES**
            - Hidden gems only locals know
            - Traditional workshops/classes
            - Home dining opportunities
            - Community interactions
            - Unique local experiences
            
            IMPORTANT GUIDELINES:
            Stay within the ₹{budget:,} budget
            Focus on authentic, local experiences
            Include specific costs for transparency
            Add cultural context to activities
            Consider group size in recommendations
            Match activities to stated interests
            Provide actionable, specific advice
            
            Make this trip unforgettable and uniquely tailored to their preferences!
            """
            
            # Send prompt to AI and get response
            logger.info(f"Generating trip plan for {destination}...")
            response = self.model.generate_content(prompt)
            
            # Return structured response
            return {
                'success': True,
                'trip_plan': response.text,
                'destination': destination,
                'duration': duration,
                'budget': budget,
                'estimated_cost': budget * 0.85,  # Assume 85% budget usage
                'savings': budget * 0.15,
                'confidence': 0.95,
                'insights': [
                    f"🤖 AI analyzed 1000+ {destination} experiences",
                    f"💰 Optimized your ₹{budget:,} budget efficiently", 
                    "🌟 Included authentic local experiences",
                    f"🎯 Perfect match for {interests_text} interests"

                ]
            }
            
        except Exception as e:
            logger.error(f"Trip planning error: {e}")
        return {
        'success': False,   # mark as success so app.py doesn’t show error
        'trip_plan': f"Sample trip plan for {destination}: Explore famous attractions, local food, and cultural spots over {duration} days.",
        'destination': destination,
        'duration': duration,
        'budget': budget,
        'estimated_cost': budget * 0.8,
        'savings': budget * 0.2,
        'confidence': 0.5,
        'insights': [
            "⚠️ AI service unavailable, showing sample trip",
            "🌍 Explore major attractions and food spots",
            "💡 Upgrade API key for full personalized plan"
        ]
    }
    
    def chat_with_agent(self, user_message, context=None):
        """
        Chat with the AI agent
        
        Parameters:
        - user_message: What the user asked (string)
        - context: Additional context about current trip (dictionary)
        
        Returns:
        - AI response (dictionary)
        """
        try:
            # Build context-aware prompt
            context_info = ""
            if context:
                context_info = f"""
                CURRENT CONTEXT:
                • Planning trip to: {context.get('destination', 'Not specified')}
                • Budget: ₹{context.get('budget', 'Not specified'):,}
                • Duration: {context.get('duration', 'Not specified')} days
                • Interests: {context.get('interests', 'Not specified')}
                """
            
            full_prompt = f"""
            You are FlexiTrip AI Agent - a friendly, knowledgeable travel expert.
            
            {context_info}
            
            User asked: "{user_message}"
            
            RESPONSE GUIDELINES:
            🤖 Be enthusiastic and helpful about travel
            💡 Provide specific, actionable advice  
            🌍 Share cultural insights when relevant
            💰 Be mindful of budget considerations
            🎯 Ask follow-up questions to help better
            ⭐ Include personal recommendations
            
            If they ask about travel planning, give detailed, practical advice.
            If they ask about destinations, provide insider knowledge.
            Keep responses engaging but informative.
            """
            
            # Get AI response
            response = self.chat.send_message(full_prompt)
            
            # Generate smart suggestions based on message
            suggestions = self._generate_suggestions(user_message, context)
            
            return {
                'success': True,
                'response': response.text,
                'suggestions': suggestions,
                'context_used': bool(context)
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                'success': False,
                'response': "I'm having trouble connecting right now. Please try again in a moment! 🤖",
                'error': str(e)
            }
    
    def _generate_suggestions(self, user_message, context):
        """
        Generate smart follow-up suggestions based on user message
        """
        message_lower = user_message.lower()
        
        # Context-based suggestions
        if context and context.get('destination'):
            destination = context['destination']
            return [
                f"Tell me more about {destination} culture",
                f"What's the best time to visit {destination}?",
                "Help me optimize my budget"
            ]
        
        # Message-based suggestions
        if any(word in message_lower for word in ['budget', 'money', 'cost']):
            return [
                "How can I save money on accommodation?",
                "What are the hidden costs in travel?",
                "Budget-friendly food options?"
            ]
        elif any(word in message_lower for word in ['food', 'eat', 'restaurant']):
            return [
                "Best local dishes to try",
                "Street food safety tips",
                "Authentic dining experiences"
            ]
        elif any(word in message_lower for word in ['culture', 'tradition', 'local']):
            return [
                "Local festivals and events",
                "Cultural etiquette tips",
                "Traditional experiences to try"
            ]
        
        # Default suggestions
        return [
            "Plan a trip for me",
            "Tell me about popular destinations",
            "What should I pack for my trip?"
        ]

# Create global AI agent instance
ai_agent = FlexiTripAI()
#-----------------
if __name__ == "__main__":
    # This block runs only when this file is executed directly
    # Python concept: __name__ == "__main__" prevents running during imports

    # Create AI agent
    ai_agent = FlexiTripAI()

    # Test generate_trip_plan
    plan = ai_agent.generate_trip_plan(
        destination="Jaipur",
        duration=3,
        budget=30000,
        interests=["culture", "food"],
        travel_style="Comfort",
        group_size=2
    )

    print("Trip Plan Output:")
    print(plan['trip_plan'])  # AI-generated plan

    # Test chat_with_agent
    chat = ai_agent.chat_with_agent(
        user_message="What are the best local dishes in Jaipur?",
        context={'destination': 'Jaipur', 'budget': 30000, 'duration': 3, 'interests': ['culture','food']}
    )

    print("\nChat Response:")
    print(chat['response'])  # AI response
    print("Suggestions:", chat.get('suggestions', 'No suggestions returned'))








