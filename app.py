from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pymysql
import os

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests, essential for testing from local files (file://)

# Database Configuration
# Inga unnoda MySQL server configurations-ai correct-ah update pannunga macha!
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'sathiya/suresh@5669') # Insert your MySQL Workbench password here
DB_NAME = os.environ.get('DB_NAME', 'goroute_db')
DB_PORT = int(os.environ.get('DB_PORT', 3306))

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )

def ensure_db_schema():
    try:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE 'bookings'")
                table_exists = cursor.fetchone()
                if table_exists:
                    cursor.execute("SHOW COLUMNS FROM bookings LIKE 'payment_method'")
                    column_exists = cursor.fetchone()
                    if not column_exists:
                        print("Adding 'payment_method' column to bookings table...")
                        cursor.execute("ALTER TABLE bookings ADD COLUMN payment_method VARCHAR(50) DEFAULT 'Cash'")
                        connection.commit()
                        print("'payment_method' column added successfully.")
        finally:
            connection.close()
    except Exception as e:
        print(f"Error checking database schema: {e}")

@app.route('/')
def home():
    return send_file('toorist.html')

@app.route('/admin')
def admin():
    return send_file('admin.html')

@app.route('/goroute-logo.jpg')
@app.route('/goroute-logo.png')
def serve_logo():
    return send_file('goroute-logo.jpg')

@app.route('/api/book', methods=['POST'])
def book_tour():
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "Payload empty! Data correct-ah send aagala macha."
            }), 400

        name = data.get('name')
        destination = data.get('destination')
        package_type = data.get('package')
        travel_date = data.get('date')
        guests = data.get('guests')
        payment_method = data.get('payment_method', 'Cash')

        # Simple validations
        if not name or not destination or not package_type or not travel_date or guests is None:
            return jsonify({
                "status": "error",
                "message": "Missing details! Ella forms columns-aiyum correct-ah fill pannunga."
            }), 400

        # MySQL database-il save seiyya pugirom
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO bookings (name, destination, package_type, travel_date, guests, payment_method)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (name, destination, package_type, travel_date, guests, payment_method))
            connection.commit()
            print(f"Success: Booking details saved for {name}")
        finally:
            connection.close()

        return jsonify({
            "status": "success",
            "message": "Booking successful! Data saved in MySQL Database."
        }), 200

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
        # Database connection error explanation in simple terms
        if e.args[0] == 1045:
            msg = "Access Denied: MySQL root password correct-ah app.py-la code check panni type pannunga!"
        elif e.args[0] == 1049:
            msg = "Unknown Database: MySQL Workbench-la 'schema.sql' execute panni database schema initialize pannunga!"
        else:
            msg = f"Database configuration error: {str(e)}"
        return jsonify({
            "status": "error",
            "message": msg
        }), 500
    except Exception as e:
        print(f"General Error: {e}")
        return jsonify({
            "status": "error",
            "message": f"Server issue: {str(e)}"
        }), 500

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    try:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM bookings ORDER BY created_at DESC")
                result = cursor.fetchall()
                # Serialize datetime / date fields to strings for JSON compatibility
                for row in result:
                    if 'created_at' in row and row['created_at']:
                        row['created_at'] = row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if 'travel_date' in row and row['travel_date']:
                        row['travel_date'] = row['travel_date'].strftime('%Y-%m-%d')
        finally:
            connection.close()

        return jsonify({
            "status": "success",
            "bookings": result
        }), 200
    except Exception as e:
        print(f"Error fetching bookings: {e}")
        return jsonify({
            "status": "error",
            "message": f"Could not fetch bookings: {str(e)}"
        }), 500

@app.route('/api/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    try:
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
            connection.commit()
            print(f"Success: Deleted booking ID {booking_id}")
        finally:
            connection.close()

        return jsonify({
            "status": "success",
            "message": f"Booking ID {booking_id} has been deleted successfully."
        }), 200
    except Exception as e:
        print(f"Error deleting booking: {e}")
        return jsonify({
            "status": "error",
            "message": f"Could not delete booking: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "running", "message": "Flask server alive!"})

if __name__ == '__main__':
    print("=" * 60)
    print("GoRoute Holidays Python Backend starting...")
    print(f"Connecting to MySQL: Host={DB_HOST}, Database={DB_NAME}, User={DB_USER}")
    print("Remember to check your password in app.py if connection fails!")
    print("=" * 60)
    ensure_db_schema()
    app.run(host='127.0.0.1', port=5000, debug=True)

