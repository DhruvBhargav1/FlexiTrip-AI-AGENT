"""
Interactive maps integration for FlexiTrip
"""
import folium
import streamlit as st
from folium import plugins
import json

class TripMaps:
    def __init__(self):
        self.india_center = [20.5937, 78.9629]  # India center coordinates
    
    def create_trip_map(self, destination, locations_data):
        """Create interactive map for trip"""
        try:
            # Get destination coordinates
            dest_coords = self.get_destination_coordinates(destination)
            
            # Create map centered on destination
            trip_map = folium.Map(
                 location=dest_coords,
                 zoom_start=12,
                 tiles='OpenStreetMap',
                 width='90%',      # restrict width
                 height='500px'    # restrict height
            )
            
            # Add markers for each location
            for location in locations_data:
                self.add_location_marker(trip_map, location)
            
            # Add route between locations
            self.add_route_line(trip_map, locations_data)
            
            # Add trip overview
            self.add_trip_overview(trip_map, destination, locations_data)
            
            return trip_map
            
        except Exception as e:
            st.error(f"Failed to create map: {e}")
            return None
    
    def get_destination_coordinates(self, destination):
        """Get coordinates for major Indian destinations"""
        coordinates = {
            'Rajasthan': [26.9124, 75.7873],  # Jaipur
            'Kerala': [9.9312, 76.2673],      # Kochi
            'Goa': [15.2993, 74.1240],        # Panaji
            'Himachal Pradesh': [32.2432, 77.1892],  # Shimla
            'Tamil Nadu': [13.0827, 80.2707],  # Chennai
            'Karnataka': [12.9716, 77.5946],  # Bangalore
            'Uttarakhand': [30.0668, 79.0193], # Dehradun
            'Maharashtra': [19.0760, 72.8777], # Mumbai
            'Gujarat': [23.0225, 72.5714],     # Ahmedabad
            'Punjab': [30.7333, 76.7794]      # Chandigarh
        }
        return coordinates.get(destination, self.india_center)
    
    def add_location_marker(self, map_obj, location):
        """Add marker for each location"""
        try:
            # Different icons for different types
            icon_map = {
                'hotel': 'bed',
                'restaurant': 'cutlery', 
                'attraction': 'star',
                'activity': 'play',
                'transport': 'bus'
            }
            
            # Different colors for different types
            color_map = {
                'hotel': 'blue',
                'restaurant': 'green',
                'attraction': 'red',
                'activity': 'orange',
                'transport': 'purple'
            }
            
            location_type = location.get('type', 'attraction')
            
            # Create popup content
            popup_content = f"""
            <div style="width: 200px;">
                <h4>{location['name']}</h4>
                <p><strong>Type:</strong> {location_type.title()}</p>
                <p><strong>Cost:</strong> ₹{location.get('cost', 'Free')}</p>
                <p><strong>Timing:</strong> {location.get('timing', 'Flexible')}</p>
                <button onclick="alert('Booking {location['name']}')">Book Now</button>
            </div>
            """
            
            folium.Marker(
                location=[location['lat'], location['lng']],
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=location['name'],
                icon=folium.Icon(
                    color=color_map.get(location_type, 'blue'),
                    icon=icon_map.get(location_type, 'info-sign'),
                    prefix='fa'
                )
            ).add_to(map_obj)
            
        except Exception as e:
            st.error(f"Failed to add marker for {location.get('name', 'Unknown')}: {e}")
    
    def add_route_line(self, map_obj, locations):
        """Add route line connecting locations"""
        try:
            # Extract coordinates
            coordinates = [[loc['lat'], loc['lng']] for loc in locations]
            
            # Add route line
            folium.PolyLine(
                locations=coordinates,
                color='blue',
                weight=3,
                opacity=0.8,
                popup='Suggested Route'
            ).add_to(map_obj)
            
            # Add route distance (estimated)
            total_distance = len(coordinates) * 5  # Rough estimate
            folium.Marker(
                location=coordinates[0],
                popup=f"Total Route: ~{total_distance} km",
                icon=folium.Icon(color='green', icon='road', prefix='fa')
            ).add_to(map_obj)
            
        except Exception as e:
            st.error(f"Failed to add route: {e}")
    
    def add_trip_overview(self, map_obj, destination, locations):
        """Add trip overview to map"""
        try:
            # Count different types of locations
            location_types = {}
            total_cost = 0
            
            for loc in locations:
                loc_type = loc.get('type', 'other')
                location_types[loc_type] = location_types.get(loc_type, 0) + 1
                total_cost += loc.get('cost', 0)
            
            # Create overview popup
            overview_html = f"""
            <div style="width: 300px;">
                <h3>🗺️ {destination} Trip Overview</h3>
                <hr>
                <p><strong>📍 Locations:</strong> {len(locations)} places</p>
                <p><strong>🏨 Hotels:</strong> {location_types.get('hotel', 0)}</p>
                <p><strong>🎯 Attractions:</strong> {location_types.get('attraction', 0)}</p>
                <p><strong>🍽️ Restaurants:</strong> {location_types.get('restaurant', 0)}</p>
                <p><strong>💰 Estimated Cost:</strong> ₹{total_cost:,}</p>
                <hr>
                <button style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;" 
                        onclick="alert('Starting booking process...')">
                    📱 Book Entire Trip
                </button>
            </div>
            """
            
            # Add overview marker at destination center
            dest_coords = self.get_destination_coordinates(destination)
            folium.Marker(
                location=dest_coords,
                popup=folium.Popup(overview_html, max_width=350),
                tooltip=f"{destination} Trip Overview",
                icon=folium.Icon(
                    color='red',
                    icon='info-sign',
                    prefix='fa'
                )
            ).add_to(map_obj)
            
        except Exception as e:
            st.error(f"Failed to add trip overview: {e}")
    
    def create_destination_selector_map(self):
        """Create map for destination selection"""
        # Create India map
        india_map = folium.Map(
            location=self.india_center,
            zoom_start=5,
            tiles='OpenStreetMap'
        )
        
        # Popular destinations with coordinates
        destinations = {
            'Rajasthan': {'coords': [26.9124, 75.7873], 'desc': 'Royal palaces and desert adventures'},
            'Kerala': {'coords': [9.9312, 76.2673], 'desc': 'Backwaters and spice plantations'},
            'Goa': {'coords': [15.2993, 74.1240], 'desc': 'Beaches and Portuguese heritage'},
            'Himachal Pradesh': {'coords': [32.2432, 77.1892], 'desc': 'Mountains and hill stations'},
            'Tamil Nadu': {'coords': [13.0827, 80.2707], 'desc': 'Ancient temples and culture'},
            'Karnataka': {'coords': [12.9716, 77.5946], 'desc': 'Tech hub and historical sites'},
        }
        
        for dest, info in destinations.items():
            folium.Marker(
                location=info['coords'],
                popup=f"<b>{dest}</b><br>{info['desc']}<br><button onclick=\"selectDestination('{dest}')\">Select This Destination</button>",
                tooltip=dest,
                icon=folium.Icon(color='green', icon='plane', prefix='fa')
            ).add_to(india_map)
        
        return india_map

# Global maps instance
trip_maps = TripMaps()
