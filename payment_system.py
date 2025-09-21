"""
Essential Booking and Payment System with MCP Integration
---------------------------------------------------------
This module manages:
1. Booking creation and sessions (like a cart/order).
2. Fetching dynamic details about items (e.g., hotels, activities) using MCP.
3. Payment validation and processing (simulated).
4. Cost breakdown and booking summaries.

Concepts involved:
- Classes and Objects (OOP in Python).
- Dictionaries to represent structured data (like JSON).
- Exception handling (try/except).
- Async/await for non-blocking API calls.
- Logging for error tracking.
- UUID for unique booking IDs.
- Global instance pattern (shared object).
"""

import json                  # Built-in library for handling JSON data (serialize/deserialize).
from datetime import datetime # For timestamps (booking created, payment completed).
import uuid                  # For generating unique booking IDs.
import asyncio               # For async operations (non-blocking tasks).
import logging               # For logging errors/info/debug.

# Configure a logger for this module
logger = logging.getLogger(__name__)


# -------------------------------
# Main Booking System Class
# -------------------------------
class BookingSystem:
    """
    BookingSystem:
    - Stores booking sessions (in-memory).
    - Handles booking creation, item details, payments, and cost summaries.
    """
    
    def __init__(self):
        # Dictionary to keep all active booking sessions {booking_id: session_data}
        self.booking_sessions = {}
        
        # Supported payment methods (acts like an enum/list of valid choices)
        self.payment_methods = ["Credit/Debit Card", "UPI", "Net Banking", "Digital Wallet"]
    

    # -------------------------------
    # 1. Booking creation
    # -------------------------------
    def initiate_booking(self, trip_data, bookable_items):
        """Start a new booking session with trip details + items."""
        try:
            # Generate a short unique booking ID (UUID -> string -> first 8 chars)
            booking_id = str(uuid.uuid4())[:8].upper()
            
            # Calculate total cost from all items (default 0 if missing 'cost')
            total_cost = sum([item.get('cost', 0) for item in bookable_items])
            
            # Booking session (dict acts like a JSON object)
            booking_session = {
                'booking_id': booking_id,
                'trip_data': trip_data,        # Metadata about trip (destination, duration, etc.)
                'items': bookable_items,       # List of hotels/activities/etc.
                'total_cost': total_cost,      # Total price
                'status': 'pending',           # Booking not confirmed yet
                'payment_status': 'pending',   # Payment not completed yet
                'created_at': datetime.now()   # Timestamp for session creation
            }
            
            # Save session in memory (in booking_sessions dictionary)
            self.booking_sessions[booking_id] = booking_session
            
            # Return booking session for confirmation
            return {'success': True, 'booking_id': booking_id, 'session': booking_session}
        
        except Exception as e:
            # If something fails, return error
            return {'success': False, 'error': str(e)}
    

    # -------------------------------
    # 2. Get Item Details (dynamic via MCP)
    # -------------------------------
    async def get_item_details(self, item, location=None):
        """
        Fetch enriched item details:
        - If location is provided, query MCP server for real-time data.
        - Else, return fallback static data.
        """
        if location:
            try:
                # Import MCP server here (lazy import to avoid circular imports)
                from mcp_server import FlexiTripMCPServer
                mcp = FlexiTripMCPServer()
                
                # Case 1: Hotel item -> fetch hotel data
                if item['type'] == 'hotel':
                    hotels = await mcp.get_hotel_data(location)
                    if hotels and not hotels.get('error') and len(hotels) > 0:
                        hotel = hotels[0]  # Pick first hotel (demo)
                        return {
                            'name': hotel.get('name', item.get('name')),
                            'description': f"Real hotel with coordinates: {hotel.get('lat')}, {hotel.get('lon')}",
                            'features': ['Live availability', 'Real location data']
                        }
                
                # Case 2: Activity item -> fetch weather data
                elif item['type'] == 'activity':
                    weather = await mcp.get_weather(location, "")
                    if not weather.get('error'):
                        return {
                            'name': item.get('name'),
                            'description': f"Weather-optimized for {weather.get('conditions', 'good weather')}",
                            'features': [f"Current temp: {weather.get('temperature', 'N/A')}°C"]
                        }
            
            except Exception as e:
                # If MCP call fails, log error and fallback to static
                logger.error(f"MCP failed: {e}")
        
        # Fallback static item details
        return {
            'name': item.get('name', 'Service'),
            'description': f"{item['type'].title()} service included",
            'features': ['Standard service', 'Customer support']
        }
    

    # -------------------------------
    # 3. Payment Validation
    # -------------------------------
    def validate_payment(self, payment_method, payment_data):
        """
        Validate payment details based on chosen method.
        Example:
        - UPI requires a UPI ID.
        - Card requires number, expiry, cvv.
        """
        if payment_method not in self.payment_methods:
            return {'valid': False, 'error': 'Invalid payment method'}
        
        # Validation per method
        if payment_method == "UPI" and not payment_data.get('upi_id'):
            return {'valid': False, 'error': 'UPI ID required'}
        
        if payment_method == "Credit/Debit Card":
            required = ['card_number', 'expiry', 'cvv']
            for field in required:
                if not payment_data.get(field):
                    return {'valid': False, 'error': f'{field} required'}
        
        return {'valid': True}
    

    # -------------------------------
    # 4. Process Payment
    # -------------------------------
    def process_payment(self, booking_id, payment_method, payment_data):
        """Validate and mark booking as paid (simulation)."""
        try:
            # Fetch session by booking_id
            booking_session = self.booking_sessions.get(booking_id)
            if not booking_session:
                return {'success': False, 'error': 'Booking not found'}
            
            # Validate payment details
            validation = self.validate_payment(payment_method, payment_data)
            if not validation['valid']:
                return {'success': False, 'error': validation['error']}
            
            # Simulate payment processing (in real-world -> call payment gateway)
            confirmation_number = f"FT{booking_session['booking_id']}"
            
            # Update booking session with payment details
            booking_session.update({
                'payment_status': 'completed',
                'payment_method': payment_method,
                'confirmation_number': confirmation_number,
                'completed_at': datetime.now(),
                'status': 'confirmed'
            })
            
            return {
                'success': True,
                'confirmation_number': confirmation_number,
                'booking_session': booking_session,
                'message': 'Payment successful! Booking confirmed.'
            }
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    

    # -------------------------------
    # 5. Cost Breakdown
    # -------------------------------
    def get_cost_breakdown(self, items):
        """
        Calculate cost per category (hotel, activity, restaurant, transport).
        Returns a dictionary of breakdown totals.
        """
        breakdown = {'hotel': 0, 'activity': 0, 'restaurant': 0, 'transport': 0}
        
        # Add cost per category
        for item in items:
            item_type = item.get('type', 'other')
            if item_type in breakdown:
                breakdown[item_type] += item.get('cost', 0)
        
        # Total cost
        breakdown['total'] = sum(breakdown.values())
        return breakdown
    

    # -------------------------------
    # 6. Get Booking Session
    # -------------------------------
    def get_booking_session(self, booking_id):
        """Retrieve full booking session by ID."""
        return self.booking_sessions.get(booking_id)
    

    # -------------------------------
    # 7. Get Booking Summary
    # -------------------------------
    def get_booking_summary(self, booking_session):
        """Return simplified summary for display/receipt."""
        return {
            'booking_id': booking_session['booking_id'],
            'destination': booking_session['trip_data'].get('destination'),
            'total_cost': booking_session['total_cost'],
            'items_count': len(booking_session['items']),
            'status': booking_session.get('status'),
            'confirmation_number': booking_session.get('confirmation_number')
        }


# -------------------------------
# Global Instance
# -------------------------------
# A single shared instance for the entire app (Singleton-like pattern).
# So any module can import and use the same booking system.
booking_system = BookingSystem()
