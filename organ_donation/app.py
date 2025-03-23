from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import logging

app = Flask(__name__)  # Corrected __name__
CORS(app, resources={r"/*": {"origins": "*"}})

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Function to connect to SQLite database
def connect_db():
    conn = sqlite3.connect('organ_donation.db')
    return conn

# Initialize database tables if they don't exist
def init_db():
    conn = connect_db()
    c = conn.cursor()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS Donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        bloodType TEXT NOT NULL,
        organs TEXT NOT NULL
    )
    ''')
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS Recipients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        bloodType TEXT NOT NULL,
        neededOrgan TEXT NOT NULL,
        urgency INTEGER NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Register a new donor
@app.route('/donors', methods=['POST'])
def add_donor():
    try:
        data = request.get_json()
        name = data['donorName']
        age = data['donorAge']
        bloodType = data['donorBloodType']
        organs = data['donorOrgans']

        logging.debug(f"Adding donor: {name}, Age: {age}, Blood Type: {bloodType}, Organs: {organs}")

        conn = connect_db()
        c = conn.cursor()
        c.execute('''
        INSERT INTO Donors (name, age, bloodType, organs)
        VALUES (?, ?, ?, ?)
        ''', (name, age, bloodType, organs))
        conn.commit()
        donor_id = c.lastrowid
        conn.close()
        return jsonify({'id': donor_id}), 201
    except Exception as e:
        logging.error(f"Error adding donor: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Register a new recipient
@app.route('/recipients', methods=['POST'])
def add_recipient():
    try:
        data = request.get_json()
        name = data['recipientName']
        age = data['recipientAge']
        bloodType = data['recipientBloodType']
        neededOrgan = data['neededOrgan']
        urgency = data['urgency']

        logging.debug(f"Adding recipient: {name}, Age: {age}, Blood Type: {bloodType}, Needed Organ: {neededOrgan}, Urgency: {urgency}")

        conn = connect_db()
        c = conn.cursor()
        c.execute('''
        INSERT INTO Recipients (name, age, bloodType, neededOrgan, urgency)
        VALUES (?, ?, ?, ?, ?)
        ''', (name, age, bloodType, neededOrgan, urgency))
        conn.commit()
        recipient_id = c.lastrowid
        conn.close()
        return jsonify({'id': recipient_id}), 201
    except Exception as e:
        logging.error(f"Error adding recipient: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Get list of donors
@app.route('/donors', methods=['GET'])
def get_donors():
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute('SELECT * FROM Donors')
        donors = c.fetchall()
        conn.close()
        logging.debug(f"Retrieved donors: {donors}")
        return jsonify(donors), 200
    except Exception as e:
        logging.error(f"Error retrieving donors: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Get list of recipients
@app.route('/recipients', methods=['GET'])
def get_recipients():
    try:
        conn = connect_db()
        c = conn.cursor()
        c.execute('SELECT * FROM Recipients')
        recipients = c.fetchall()
        conn.close()
        logging.debug(f"Retrieved recipients: {recipients}")
        return jsonify(recipients), 200
    except Exception as e:
        logging.error(f"Error retrieving recipients: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Match donors to recipients
@app.route('/match', methods=['GET'])
def match_organ():
    try:
        conn = connect_db()
        c = conn.cursor()
        
        # Get all donors and recipients
        c.execute('SELECT * FROM Donors')
        donors = c.fetchall()

        c.execute('SELECT * FROM Recipients')
        recipients = c.fetchall()
        
        matches = []

        # Iterate over each recipient and find matching donors
        for recipient in recipients:
            recipient_id, recipient_name, recipient_age, recipient_bloodType, needed_organ, urgency = recipient
            needed_organ = needed_organ.lower().strip()  # Normalize

            for donor in donors:
                donor_id, donor_name, donor_age, donor_bloodType, donor_organs = donor
                donor_organs_list = [organ.strip().lower() for organ in donor_organs.split(',')]  # Split and normalize

                if recipient_bloodType == donor_bloodType and needed_organ in donor_organs_list:
                    matches.append({
                        'RecipientName': recipient_name,
                        'DonorName': donor_name,
                        'Organs': donor_organs
                    })

        conn.close()

        logging.debug(f"Retrieved matches: {matches}")
        return jsonify(matches), 200
    except Exception as e:
        logging.error(f"Error matching organs: {str(e)}")
        return jsonify({'error': str(e)}), 400

# Delete a donor
@app.route('/donors/<int:donor_id>', methods=['DELETE'])
def delete_donor(donor_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute('DELETE FROM Donors WHERE id = ?', (donor_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Donor deleted successfully'})

# Delete a recipient
@app.route('/recipients/<int:recipient_id>', methods=['DELETE'])
def delete_recipient(recipient_id):
    conn = connect_db()
    c = conn.cursor()
    c.execute('DELETE FROM Recipients WHERE id = ?', (recipient_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Recipient deleted successfully'})

if __name__ == '__main__':  # Corrected main check
    app.run(debug=True)

