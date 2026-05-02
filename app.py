from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'kerala_vibe_secret_key_123' # Change this for security
@app.route('/test')
def test():
    return "Flask is working!"

# --- DATABASE CONNECTION ---
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root2005',
    'database': 'kerala_tourism',
    'auth_plugin':'mysql_native_password',# Forces a standard login method
    'raise_on_warnings': True
}

def get_db_connection():
    try:
        # This replaces the old mysql.connector line
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='root2005',
            database='kerala_tourism',
            cursorclass=pymysql.cursors.DictCursor  # This makes data act like a dictionary
        )
        print(">>> SUCCESS: Database Connected via PyMySQL!") 
        return conn
    except Exception as err:
        print("\n" + "!"*30)
        print(f"DATABASE ERROR: {err}")
        print("!"*30 + "\n")
        return None

# --- 1. ACCESS CONTROL (GATEKEEPER) ---
@app.route('/')
def index():
    # 1. Check if user is logged in
    if 'user_id' not in session and 'admin_id' not in session:
        return redirect(url_for('login'))
    
    conn = None
    try:
        # 2. Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 3. Get all the places the admin has added
        cursor.execute("SELECT * FROM destinations")
        all_destinations = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # 4. Send the data to your index.html
        # Note: we are passing 'destinations' so the HTML loop can find it
        return render_template('index.html', 
                               user_name=session.get('user_name', 'Traveler'),
                               destinations=all_destinations)

    except Exception as e:
        if conn:
            conn.close()
        print(f">>> HOME PAGE ERROR: {e}")
        # If there's an error, still show the page but with an empty list
        return render_template('index.html', destinations=[])
# --- 2. USER AUTHENTICATION ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('email') # This could be email or username
        password = request.form.get('password')

        conn = get_db_connection()
        cursor = conn.cursor()

        # --- 1. TRY ADMIN TABLE FIRST ---
        cursor.execute("SELECT * FROM admins WHERE username = %s", (identifier,))
        admin = cursor.fetchone()

        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['role'] = 'admin'
            cursor.close()
            conn.close()
            return redirect(url_for('admin_dashboard'))

        # --- 2. TRY USER TABLE SECOND ---
        cursor.execute("SELECT * FROM users WHERE email = %s", (identifier,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['role'] = 'user'
            cursor.close()
            conn.close()
            return redirect(url_for('index')) # Redirect to your regular website home

        # --- 3. FAIL CASE ---
        cursor.close()
        conn.close()
        flash("Invalid email/username or password")
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        # 1. Check if any fields are empty
        if not name or not email or not password:
            flash("All fields are required!")
            return redirect(url_for('signup'))

        hashed_pw = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # 2. Check if the email is already in the database
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                flash("Email already registered. Try logging in!")
                return redirect(url_for('signup'))

            # 3. Insert new user if everything is fine
            cursor.execute("INSERT INTO users (full_name, email, password_hash) VALUES (%s, %s, %s)", 
                           (name, email, hashed_pw))
            conn.commit()
            flash("Registration successful! Please login.")
            return redirect(url_for('login'))
            
        except Exception as err:
            print(f"Signup Error: {err}")
            flash("Database error! Please try again later.")
            return redirect(url_for('signup'))
        finally:
            cursor.close()
            conn.close()

    # 4. Show the page if they are just visiting the URL
    return render_template('signup.html')

# --- 3. ADMIN AUTHENTICATION ---

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        print("\n" + "="*30)
        print("BUTTON CLICK DETECTED!")
        print("="*30 + "\n")
        try:
            # 1. Get data from the form
            username = request.form.get('username')
            password = request.form.get('password')
            
            # 2. Connect to Database
            conn = get_db_connection()
            if conn is None:
                return "Database connection failed! Check your MySQL service."
                
            cursor = conn.cursor()
            
            # 3. Look for the Admin
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            admin = cursor.fetchone()
            
            cursor.close()
            conn.close()

            # 4. Check Password
            if admin and check_password_hash(admin['password_hash'], password):
                session['admin_id'] = admin['id']
                session['admin_username'] = admin['username']
                return redirect(url_for('admin_dashboard'))
            else:
                return "Invalid username or password"

        except Exception as e:
            # This will print to your terminal AND stop the crash
            import traceback
            print(traceback.format_exc()) 
            return f"<h1>Internal Error</h1><p>{e}</p><pre>{traceback.format_exc()}</pre>"
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    # 1. Security Check
    if session.get('role') != 'admin':
        flash("Admins only! Please log in.")
        return redirect(url_for('login')) 
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 2. Fetch Total User Count
        cursor.execute("SELECT COUNT(*) as total FROM users")
        user_stats = cursor.fetchone()
        total_users = user_stats['total'] if user_stats else 0

        # 3. Fetch Recent Users (to show in your table)
        # Assuming your table has 'name', 'email', and 'id' columns
        cursor.execute("SELECT full_name, email FROM users ORDER BY id DESC LIMIT 5")
        recent_users = cursor.fetchall()

        cursor.close()
        conn.close()

        # 4. Send this real data to your HTML template
        return render_template('admin_dashboard.html', 
                               total_users=total_users, 
                               users=recent_users)

    except Exception as e:
        if conn:
            conn.close()
        print(f">>> DASHBOARD ERROR: {e}")
        return f"Database Error: {str(e)}"
    
# --- 4. CORE FEATURES (API) ---

@app.route('/api/destinations')
def get_destinations():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM destinations")
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(data)

@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '').lower()
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT answer FROM chatbot_data WHERE %s LIKE CONCAT('%%', question, '%%')", (user_msg,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    reply = result['answer'] if result else "That's a great question! Explore our destinations to learn more."
    return jsonify({'reply': reply})

# --- 5. LOGOUT ---
@app.route('/logout')
def logout():
    session.clear()
    print(">>> Session cleared. User logged out.")
    return redirect(url_for('login'))


@app.route('/admin/add_place', methods=['POST'])
def add_place():
    # Security check: Only admins can add places
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    # Get data from the form fields
    name = request.form.get('name')
    category = request.form.get('category')
    description = request.form.get('description')
    location = request.form.get('location')
    image_url = request.form.get('image_url')
    best_time = request.form.get('best_time')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # SQL query matching your table structure
        query = """
            INSERT INTO destinations (name, category, description, location, image_url, best_time) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, category, description, location, image_url, best_time))
        
        conn.commit()
        cursor.close()
        conn.close()
        flash(f"Successfully added {name} to the database!")
    except Exception as e:
        print(f">>> ADD PLACE ERROR: {e}")
        flash(f"Error adding place: {e}")

    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    try:
        print("--- Starting Server ---")
        app.run(debug=True, port=5001) # Try port 5001 to avoid conflicts
    except Exception as e:
        print("\n" + "="*40)
        print("CRITICAL ERROR DURING STARTUP:")
        print(e)
        print("="*40 + "\n")
    
    # This line prevents the terminal from closing immediately
    input("The script has finished. Press Enter to exit...")