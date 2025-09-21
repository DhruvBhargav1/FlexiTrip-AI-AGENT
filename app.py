"""
FlexiTrip AI Agent - Complete Application (Updated)
"""
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import time
import asyncio
from ai_agent import ai_agent
from maps import TripMaps

trip_maps = TripMaps()  # Create instance once


# Import our modules
from ai_agent import ai_agent
from database import db
from payment_system import booking_system

# Configure Streamlit
st.set_page_config(
    page_title="FlexiTrip AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .booking-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .cost-breakdown {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
    
    .payment-form {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function"""
    # Initialize session state
    if 'current_trip' not in st.session_state:
        st.session_state.current_trip = None
    if 'booking_session' not in st.session_state:
        st.session_state.booking_session = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/667eea/white?text=FlexiTrip+AI", width=200)
        
        page = st.radio(
            "🧭 Navigate",
            ["🏠 Home", "🗺️ AI Trip Planner", "💬 AI Assistant", "📊 My Trips", "💳 Booking Center"],
            index=0
        )
        
        # AI Status
        st.markdown("---")
        st.markdown("### 🤖 AI Status")
        try:
            test_response = ai_agent.chat_with_agent("Hello")
            if test_response.get('success'):
                st.success("🟢 AI Agent Online")
            else:
                st.error("🔴 AI Agent Offline")
        except Exception as e:
            st.error("🔴 Connection Failed")
        
        # Quick stats
        trips = db.get_all_trips()
        bookings = len([t for t in trips if t.get('booking_status') == 'confirmed'])
        
        st.markdown("### 📈 Quick Stats")
        st.metric("Trips Planned", len(trips))
        st.metric("Bookings Made", bookings)
        if trips:
            total_budget = sum([trip['budget'] for trip in trips])
            st.metric("Total Budget", f"₹{total_budget:,}")
    
    # Route to pages
    if page == "🏠 Home":
        show_home_page()
    elif page == "🗺️ AI Trip Planner":
        show_trip_planner()
    elif page == "💬 AI Assistant":
        show_ai_chat()
    elif page == "📊 My Trips":
        show_my_trips()
    elif page == "💳 Booking Center":
        show_booking_center()

def show_home_page():
    """Enhanced home page"""
    st.markdown('<h1 class="main-header">FlexiTrip AI Agent</h1>', unsafe_allow_html=True)
    
    # Hero section with live demo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### Your Complete AI Travel Companion
        
        From planning to booking to traveling - experience the future of intelligent travel assistance.
        Our AI agent creates personalized itineraries, finds the best deals, and books everything for you.
        """)
        
        # Live demo section
        st.markdown("### ⚡ Try It Now")
        demo_destination = st.selectbox("Quick Demo - Pick a destination:", 
            ["Rajasthan", "Kerala", "Goa", "Himachal Pradesh"])
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🤖 Generate AI Plan", type="primary", use_container_width=True):
                with st.spinner("AI generating your trip..."):
                    try:
                        # Quick demo generation
                        demo_response = ai_agent.generate_trip_plan(
                            destination=demo_destination,
                            duration=3,
                            budget=20000,
                            interests=["culture", "food"],
                            travel_style="comfort"
                        )
                        
                        if demo_response.get('success'):
                            st.success("🎉 AI Trip Plan Generated!")
                            with st.expander("📋 See Your AI-Generated Plan", expanded=True):
                                st.markdown(demo_response['trip_plan'][:500] + "...")
                                st.info("Complete plan available in Trip Planner section!")
                        else:
                            st.error("Failed to generate plan. Try the full Trip Planner.")
                    except Exception as e:
                        st.error(f"Demo error: {str(e)}")
        
        with col_b:
            if st.button("💬 Chat with AI", use_container_width=True):
                st.session_state.demo_chat = True
                st.info("💬 AI Chat activated! Go to AI Assistant section to continue.")

    # Feature showcase
    st.markdown("---")
    st.markdown("### 🌟 What Makes FlexiTrip Unique")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🧠 AI-Powered Intelligence</h4>
            <p>Advanced AI analyzes thousands of options to create your perfect itinerary in seconds.</p>
            <ul>
                <li>Real-time data integration</li>
                <li>Cultural context awareness</li>
                <li>Budget optimization</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🗺️ Interactive Planning</h4>
            <p>Visualize your journey with interactive maps and real-time booking capabilities.</p>
            <ul>
                <li>Live maps integration</li>
                <li>Route optimization</li>
                <li>Location-based recommendations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>💳 End-to-End Booking</h4>
            <p>Complete booking system from planning to payment - all in one place.</p>
            <ul>
                <li>Integrated payment gateway</li>
                <li>Real-time confirmations</li>
                <li>24/7 support system</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Success metrics
    st.markdown("---")
    st.markdown("### 📊 FlexiTrip Impact")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("AI Plans Generated", "15K+", "↗️ 300%")
    
    with col2:
        st.metric("Average Savings", "₹8,500", "↗️ 25%")
    
    with col3:
        st.metric("User Satisfaction", "98.5%", "↗️ 5%")
    
    with col4:
        st.metric("Bookings Completed", "12K+", "↗️ 450%")

def show_trip_planner():
    """AI Trip Planner Page"""
    st.markdown("# 🗺️ AI Trip Planner")
    st.markdown("Let our AI agent create your perfect trip with real-time data integration!")

    # Initialize variables safely
    trip_data = None
    trip_response = None
    locations_data = []

    # Trip Planning Form
    with st.form("trip_planning_form"):
        col1, col2 = st.columns(2)
        with col1:
            destination = st.selectbox(
                "🏞️ Destination",
                ["Rajasthan", "Kerala", "Goa", "Himachal Pradesh", "Tamil Nadu", 
                 "Karnataka", "Uttarakhand", "Maharashtra", "Gujarat", "Punjab"]
            )
            duration = st.slider("📅 Duration (days)", 2, 15, 5)
            budget = st.number_input("💰 Budget (₹)", min_value=5000, max_value=500000, value=25000, step=1000)
        with col2:
            interests = st.multiselect(
                "🎯 Your Interests",
                ["Heritage & Culture", "Adventure Sports", "Food & Cuisine", "Photography", 
                 "Nature & Wildlife", "Spiritual", "Art & Craft", "Nightlife", "Beach", "Mountains"]
            )
            travel_style = st.selectbox("✨ Travel Style", ["Budget", "Comfort", "Luxury", "Backpacking"])
            group_size = st.number_input("👥 Group Size", min_value=1, max_value=20, value=2)

        submitted = st.form_submit_button("🚀 Generate AI Trip Plan", type="primary", use_container_width=True)

    if submitted:
        if not interests:
            st.warning("Please select at least one interest!")
        else:
            with st.spinner("🤖 AI Agent analyzing options and creating your trip..."):
                try:
                    trip_response = ai_agent.generate_trip_plan(
                        destination=destination,
                        duration=duration,
                        budget=budget,
                        interests=interests,
                        travel_style=travel_style,
                        group_size=group_size
                    )

                    if trip_response.get('success'):
                        trip_data = {
                            'destination': destination,
                            'duration': duration,
                            'budget': budget,
                            'interests': interests,
                            'travel_style': travel_style,
                            'group_size': group_size
                        }

                        try:
                            trip_id = db.save_trip(
                                title=f"{destination} Adventure",
                                destination=destination,
                                duration=duration,
                                budget=budget,
                                interests=interests,
                                travel_style=travel_style,
                                group_size=group_size,
                                trip_plan=trip_response['trip_plan'],
                                estimated_cost=trip_response.get('estimated_cost', budget * 0.85)
                            )
                        except:
                            trip_id = 1

                        st.session_state.current_trip = {
                            'trip_id': trip_id,
                            'data': trip_data,
                            'ai_response': trip_response
                        }

                        st.success("🎉 Your AI-Generated Trip Plan is Ready!")

                        # Show AI Insights
                        if 'insights' in trip_response:
                            st.markdown("### 🧠 AI Insights")
                            for insight in trip_response['insights']:
                                st.info(insight)

                        # Show Itinerary
                        st.markdown("### 📋 Your Personalized Itinerary")
                        st.markdown(trip_response['trip_plan'])

                        # Cost summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Budget", f"₹{budget:,}")
                        with col2:
                            est_cost = trip_response.get('estimated_cost', 0)
                            st.metric("Estimated Cost", f"₹{est_cost:,}")
                        with col3:
                            savings = budget - trip_response.get('estimated_cost', budget)
                            st.metric("Estimated Savings", f"₹{savings:,}")

                    else:
                        st.error("Failed to generate trip plan. Please try again.")

                except Exception as e:
                    st.error(f"Error generating trip: {str(e)}")

    # Show map and actions only if a trip exists
    if st.session_state.get('current_trip'):
        trip_data = st.session_state.current_trip['data']
        trip_response = st.session_state.current_trip['ai_response']
        locations_data=[]
        # Extract locations safely
        try:
            if isinstance(trip_response.get('locations'), list):
                locations_data = trip_response['locations']
            elif isinstance(trip_response.get('locations'), str):
                locations_data = json.loads(trip_response['locations'])
        except Exception as e:
            st.warning(f"Failed to parse AI locations, using default. Error: {e}")

        if not locations_data:
            locations_data = [{
                'name': trip_data['destination'],
                'lat': 26.9124, 'lng': 75.7873,
                'type': 'attraction',
                'cost': 0,
                'timing': 'Flexible'
            }]
            # --- Display AI-generated trip text first ---
          st.markdown("### 📋 Your Personalized Itinerary")

          # Check if AI actually succeeded or fallback
         if trip_response.get('insights') and "⚠️ AI service unavailable" in trip_response['insights'][0]:
    # Show fallback with a warning
    st.warning("⚠️ AI service unavailable. Showing a sample trip plan instead.")
    st.markdown(trip_response['trip_plan'])
else:
    # Show real AI-generated plan
    st.markdown(trip_response['trip_plan'])

        # Render Map in a separate container
        trip_map = trip_maps.create_trip_map(trip_data['destination'], locations_data)
        if trip_map:
            with st.container():
                st.markdown("### 🗺️ Trip Map")
                from streamlit_folium import st_folium
                st_folium(trip_map, width=800, height=400)

        # Next steps buttons
        st.markdown("---")
        st.markdown("### Next Steps")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💬 Chat with AI about this trip", use_container_width=True):
                st.info("Go to AI Assistant to discuss your trip!")
        with col2:
            if st.button("💳 Proceed to Booking", type="primary", use_container_width=True):
                budget = trip_data['budget']
                destination = trip_data['destination']

                bookable_items = [
                    {'type': 'hotel', 'name': f'{destination} Heritage Hotel', 'cost': budget * 0.4, 'nights': trip_data['duration']},
                    {'type': 'activity', 'name': 'Cultural Experience Package', 'cost': budget * 0.3, 'duration': f'{trip_data["duration"]} days'},
                    {'type': 'restaurant', 'name': 'Local Cuisine Tour', 'cost': budget * 0.2, 'meal': 'multiple'},
                    {'type': 'transport', 'name': 'Complete Transport Package', 'cost': budget * 0.1, 'service': 'door-to-door'}
                ]

                booking_result = booking_system.initiate_booking(trip_data, bookable_items)
                if booking_result['success']:
                    st.session_state.booking_session = booking_result['session']
                    st.success("Booking initiated! Go to Booking Center to complete.")
                else:
                    st.error("Booking initiation failed.")
                    
def show_ai_chat():
    """AI Assistant Chat Page"""
    st.markdown("# 💬 AI Travel Assistant")
    st.markdown("Chat with your intelligent travel companion!")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, chat in enumerate(st.session_state.chat_history):
            if chat['type'] == 'user':
                st.markdown(f"""
                <div class="chat-message-user">
                    <strong>You:</strong> {chat['message']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message-bot">
                    <strong>AI Agent:</strong> {chat['message']}
                </div>
                """, unsafe_allow_html=True)
    
    # Chat input
    user_message = st.chat_input("Ask me anything about travel...")
    
    if user_message:
        # Add user message to history
        st.session_state.chat_history.append({
            'type': 'user',
            'message': user_message,
            'timestamp': datetime.now()
        })
        
        # Get AI response
        try:
            trip_context = None
            if st.session_state.current_trip:
                trip_context = st.session_state.current_trip['data']
            
            ai_response = ai_agent.chat_with_agent(user_message, trip_context)
            
            if ai_response.get('success'):
                # Add AI response to history
                st.session_state.chat_history.append({
                    'type': 'ai',
                    'message': ai_response['response'],
                    'timestamp': datetime.now()
                })
                
                # Save chat to database
                try:
                    db.save_chat_message(user_message, ai_response['response'])
                except:
                    pass  # If method doesn't exist, just skip
                
            else:
                st.error("AI Agent is temporarily unavailable.")
                
        except Exception as e:
            st.error(f"Chat error: {str(e)}")
        
        # Rerun to show new messages
        st.rerun()

def show_my_trips():
    """My Trips Dashboard"""
    st.markdown("# 📊 My Trips")
    
    try:
        trips = db.get_all_trips()
    except:
        trips = []
    
    if not trips:
        st.info("No trips planned yet. Visit the Trip Planner to get started!")
        return
    
    # Display trips
    for trip in trips:
            with st.expander(f"🗺️ {trip['title']} - {trip['destination']}", expanded=False):
             col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Duration:** {trip['duration']} days")
                st.write(f"**Budget:** ₹{trip['budget']:,}")
                st.write(f"**Travel Style:** {trip['travel_style']}")
                st.write(f"**Group Size:** {trip['group_size']}")
                
            with col2:
                st.write(f"**Created:** {trip['created_at']}")
                st.write(f"**Interests:** {', '.join(trip['interests'])}")
                if trip.get('estimated_cost'):
                    st.write(f"**Estimated Cost:** ₹{trip['estimated_cost']:,}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button(f"View Details", key=f"view_{trip['id']}"):
                    st.markdown(trip['trip_plan'])
            
            with col2:
                if st.button(f"Book This Trip", key=f"book_{trip['id']}"):
                    st.info("Redirect to booking...")
            
            with col3:
                if st.button(f"Chat About Trip", key=f"chat_{trip['id']}"):
                    st.info("Go to AI Assistant with this trip context!")

def show_booking_center():
    """Booking Center"""
    st.markdown("# 💳 Booking Center")
    
    if not st.session_state.booking_session:
        st.info("No active booking session. Plan a trip first to start booking!")
        return
    
    booking_session = st.session_state.booking_session
    
    # Display booking summary
    st.markdown("## 📋 Booking Summary")
    
    trip_data = booking_session['trip_data']
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Trip Details")
        st.info(f"""
        **Destination:** {trip_data['destination']}
        **Duration:** {trip_data['duration']} days
        **Travel Style:** {trip_data['travel_style']}
        **Group Size:** {trip_data['group_size']} people
        **Booking ID:** {booking_session['booking_id']}
        """)
        
        # Display items to book
        st.markdown("### Items to Book")
        for i, item in enumerate(booking_session['items']):
            with st.expander(f"{item['type'].title()}: {item['name']}", expanded=False):
                # Simplified details without async
                st.write(f"**Cost:** ₹{item['cost']:,}")
                st.write(f"**Type:** {item['type'].title()}")
                st.write(f"**Service:** Enhanced {item['type']} experience")
                
                # Basic features
                features = {
                    'hotel': ['Premium accommodation', 'Free breakfast', '24/7 room service'],
                    'activity': ['Expert guide included', 'All equipment provided', 'Insurance covered'],
                    'restaurant': ['Authentic local cuisine', 'Special dietary options', 'Private dining'],
                    'transport': ['Professional drivers', 'AC vehicles', 'Door-to-door service']
                }
                
                st.write("**Features:**")
                for feature in features.get(item['type'], ['Standard service', 'Customer support']):
                    st.write(f"• {feature}")
    
    with col2:
        st.markdown("### Cost Breakdown")
        cost_breakdown = booking_system.get_cost_breakdown(booking_session['items'])
        
        for category, cost in cost_breakdown.items():
            if category != 'total' and cost > 0:
                st.metric(category.title(), f"₹{cost:,}")
        
        st.markdown("---")
        st.metric("**Total Cost**", f"₹{booking_session['total_cost']:,}")
    
    # Payment section
    st.markdown("---")
    st.markdown("## 💳 Payment Details")
    
    payment_method = st.selectbox(
        "Payment Method",
        ["Credit/Debit Card", "UPI", "Net Banking", "Digital Wallet"]
    )
    
    # Payment form based on method
    payment_data = {}
    
    if payment_method == "Credit/Debit Card":
        col1, col2 = st.columns(2)
        with col1:
            payment_data['card_number'] = st.text_input("Card Number", placeholder="1234 5678 9012 3456")
            payment_data['cardholder_name'] = st.text_input("Cardholder Name")
        with col2:
            payment_data['expiry'] = st.text_input("Expiry (MM/YY)", placeholder="12/25")
            payment_data['cvv'] = st.text_input("CVV", type="password", placeholder="123")
    
    elif payment_method == "UPI":
        payment_data['upi_id'] = st.text_input("UPI ID", placeholder="yourname@upi")
    
    elif payment_method == "Net Banking":
        payment_data['bank'] = st.selectbox("Select Bank", 
            ["SBI", "HDFC", "ICICI", "Axis", "Kotak"])
    
    elif payment_method == "Digital Wallet":
        payment_data['wallet'] = st.selectbox("Select Wallet",
            ["Paytm", "PhonePe", "Google Pay", "Amazon Pay"])
    
    # Terms and payment
    agree_terms = st.checkbox("I agree to the terms and conditions")
    
    if agree_terms:
        if st.button(f"💳 Pay ₹{booking_session['total_cost']:,} & Confirm Booking", 
                    type="primary", use_container_width=True):
            
            # Process payment
            payment_result = booking_system.process_payment(
                booking_session['booking_id'],
                payment_method,
                payment_data
            )
            
            if payment_result['success']:
                st.success(f"🎉 Payment Successful!")
                st.success(f"Confirmation Number: {payment_result['confirmation_number']}")
                
                # Update session
                st.session_state.booking_session = payment_result['booking_session']
                
                # Display next steps
                st.markdown("### 📱 What's Next?")
                st.info("""
                1. Confirmation emails sent to your email
                2. Hotel vouchers available 24 hours before check-in
                3. Activity tickets sent via SMS 2 days before travel
                4. 24/7 customer support: +91-9999-FLEXITRIP
                """)
                
                # Clear booking session after successful payment
                st.balloons()
                
            else:
                st.error(f"Payment Failed: {payment_result['error']}")
    else:
        st.warning("Please accept terms and conditions to proceed")

if __name__ == "__main__":
    main()


