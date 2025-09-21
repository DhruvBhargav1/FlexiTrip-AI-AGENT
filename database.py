"""
Database - Store and retrieve trip data
This file handles all data storage operations for FlexiTrip.
"""

import sqlite3   # For SQLite database operations
import json      # To store lists/dicts as text (JSON) inside DB columns
import logging   # For logging errors and info messages

logger = logging.getLogger(__name__)

class TripDatabase:
    """
    Handles all database operations.
    SQLite = lightweight database engine (no server needed, stored in a file).
    """

    def __init__(self, db_path="flexitrip.db"):
        """
        Initialize database connection.
        - db_path: path to the database file (default = flexitrip.db)
        """
        self.db_path = db_path
        self.init_database()   # Ensure tables are created before using

    def init_database(self):
        """
        Create all necessary tables if they don't exist yet.
        This sets up our "schema".
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # -----------------------------
                # Trips table (main trip data)
                # -----------------------------
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trips(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        destination TEXT NOT NULL,
                        duration INTEGER NOT NULL,
                        budget REAL NOT NULL,
                        interests TEXT NOT NULL,
                        travel_style TEXT NOT NULL,
                        group_size INTEGER DEFAULT 2,
                        trip_plan TEXT NOT NULL,
                        estimated_cost REAL,
                        total_cost REAL,
                        map_locations TEXT,
                        bookable_items TEXT,
                        booking_status TEXT DEFAULT 'planned',
                        confirmation_number TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # -----------------------------
                # Bookings table (linked to trips)
                # -----------------------------
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS bookings(
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER,
                        booking_id TEXT UNIQUE,
                        confirmation_number TEXT,
                        total_amount REAL,
                        payment_status TEXT DEFAULT 'pending',
                        payment_method TEXT,
                        booking_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        FOREIGN KEY (trip_id) REFERENCES trips (id)
                    )
                ''')

                # -----------------------------
                # Chat messages table
                # -----------------------------
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trip_id INTEGER,
                        message TEXT NOT NULL,
                        response TEXT NOT NULL,
                        suggestions TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (trip_id) REFERENCES trips (id)
                    )
                ''')

                # -----------------------------
                # Analytics table (logs for insights)
                # -----------------------------
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        destination TEXT,
                        data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("Enhanced database initialized")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def save_enhanced_trip(self, trip_data, ai_response):
        """
        Save a trip with AI-enhanced details into `trips` table.
        - trip_data: dictionary from user
        - ai_response: dictionary from AI model
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO trips
                    (title, destination, duration, budget, interests, travel_style,
                     group_size, trip_plan, estimated_cost, total_cost, map_locations,
                     bookable_items)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    f"{trip_data['destination']} Adventure",
                    trip_data['destination'],
                    trip_data['duration'],
                    trip_data['budget'],
                    json.dumps(trip_data['interests']),
                    trip_data['travel_style'],
                    trip_data['group_size'],
                    ai_response['trip_plan'],
                    ai_response.get('total_cost', trip_data['budget'] * 0.85),
                    ai_response.get('total_cost', trip_data['budget'] * 0.85),
                    json.dumps(ai_response.get('map_locations', [])),
                    json.dumps(ai_response.get('bookable_items', []))
                ))

                trip_id = cursor.lastrowid
                conn.commit()

                self.log_analytics('trip_created', trip_data['destination'], trip_data)

                logger.info(f"Enhanced trip saved with ID: {trip_id}")
                return trip_id

        except Exception as e:
            logger.error(f"Failed to save enhanced trip: {e}")
            return None

    def save_booking(self, booking_session):
        """
        Save booking information linked to a trip.
        - booking_session: dictionary containing booking details
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO bookings
                    (trip_id, booking_id, confirmation_number, total_amount, payment_status,
                     payment_method, booking_data, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    booking_session.get('trip_id'),
                    booking_session['booking_id'],
                    booking_session.get('confirmation_number', ''),
                    booking_session['total_cost'],
                    booking_session.get('payment_status', 'pending'),
                    booking_session.get('payment_method', ''),
                    json.dumps(booking_session),
                    booking_session.get('completed_at')
                ))

                conn.commit()
                logger.info(f"Booking saved: {booking_session['booking_id']}")

        except Exception as e:
            logger.error(f"Failed to save booking: {e}")

    def get_all_trips(self):
        """Fetch all trips from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM trips ORDER BY created_at DESC")
                rows = cursor.fetchall()

                trips = []
                for row in rows:
                    trips.append({
                        "id": row["id"],
                        "title": row["title"],
                        "destination": row["destination"],
                        "duration": row["duration"],
                        "budget": row["budget"],
                        "interests": json.loads(row["interests"]) if row["interests"] else [],
                        "travel_style": row["travel_style"],
                        "group_size": row["group_size"],
                        "trip_plan": row["trip_plan"],
                        "estimated_cost": row["estimated_cost"],
                        "total_cost": row["total_cost"],
                        "map_locations": json.loads(row["map_locations"]) if row["map_locations"] else [],
                        "bookable_items": json.loads(row["bookable_items"]) if row["bookable_items"] else [],
                        "booking_status": row["booking_status"],
                        "confirmation_number": row["confirmation_number"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"]
                    })
                return trips
        except Exception as e:
            logger.error(f"Failed to fetch all trips: {e}")
            return []

    def save_trip(self, title, destination, duration, budget, interests,
                  travel_style, group_size, trip_plan, estimated_cost):
        """
        Save a basic trip to database.

        Parameters:
        - All trip details as separate parameters

        Returns:
        - trip_id if successful, None if failed
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                interests_json = json.dumps(interests)

                cursor.execute('''
                    INSERT INTO trips 
                    (title, destination, duration, budget, interests, travel_style, 
                     group_size, trip_plan, estimated_cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (title, destination, duration, budget, interests_json,
                      travel_style, group_size, trip_plan, estimated_cost))

                trip_id = cursor.lastrowid
                conn.commit()

                logger.info(f"Trip saved with ID: {trip_id}")
                return trip_id

        except Exception as e:
            logger.error(f"Failed to save trip: {e}")
            return None

    def get_trip_with_booking_data(self, trip_id):
        """
        Get a trip and its linked booking info (join trips + bookings).
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT t.*, b.confirmation_number, b.payment_status, b.total_amount
                    FROM trips t
                    LEFT JOIN bookings b ON t.id = b.trip_id
                    WHERE t.id = ?
                ''', (trip_id,))
                row = cursor.fetchone()

                if row:
                    return {
                        'id': row[0],
                        'title': row[1],
                        'destination': row[2],
                        'duration': row[3],
                        'budget': row[4],
                        'interests': json.loads(row[5]),
                        'travel_style': row[6],
                        'group_size': row[7],
                        'trip_plan': row[8],
                        'estimated_cost': row[9],
                        'total_cost': row[10],
                        'map_locations': json.loads(row[11]) if row[11] else [],
                        'bookable_items': json.loads(row[12]) if row[12] else [],
                        'booking_status': row[13],
                        'confirmation_number': row[14],
                        'created_at': row[15],
                        'updated_at': row[16],
                        'payment_status': row[17] if len(row) > 17 else None,
                        'paid_amount': row[18] if len(row) > 18 else None
                    }
                return None

        except Exception as e:
            logger.error(f"Failed to get trip with booking data: {e}")
            return None

    def log_analytics(self, event_type, destination, data):
        """
        Log an analytics event (for dashboard insights).
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO analytics (event_type, destination, data)
                    VALUES (?, ?, ?)
                ''', (event_type, destination, json.dumps(data)))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to log analytics: {e}")

    def get_analytics_dashboard_data(self):
        """
        Fetch insights for dashboard:
        - popular destinations
        - budget stats
        - recent activities
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                destinations = conn.execute('''
                    SELECT destination, COUNT(*) as count
                    FROM trips
                    GROUP BY destination
                    ORDER BY count DESC
                    LIMIT 10
                ''').fetchall()

                budget_analysis = conn.execute('''
                    SELECT
                        AVG(budget) as avg_budget,
                        AVG(total_cost) as avg_actual_cost,
                        COUNT(*) as total_trips
                    FROM trips
                ''').fetchone()

                recent_activity = conn.execute('''
                    SELECT event_type, destination, created_at
                    FROM analytics
                    ORDER BY created_at DESC
                    LIMIT 10
                ''').fetchall()

                return {
                    'popular_destination': destinations,
                    'budget_analysis': budget_analysis,
                    'recent_activity': recent_activity
                }
        except Exception as e:
            logger.error(f"Failed to get analytics data: {e}")
            return {}

# -------------------------------
# Global database instance
# -------------------------------
db = TripDatabase()
