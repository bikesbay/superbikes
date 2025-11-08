import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from mysql.connector import pooling
from datetime import datetime, timedelta
import traceback
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import razorpay

# --------------------------
# Environment Variables
# --------------------------
os.environ['MYSQL_HOST'] = 'BikesBayy.mysql.pythonanywhere-services.com'
os.environ['MYSQL_USER'] = 'BikesBayy'
os.environ['MYSQL_PASSWORD'] = 'shrutiuttekar25neelshinde111125'
os.environ['MYSQL_DB'] = 'BikesBayy$superbikes_db'
os.environ['MYSQL_PORT'] = '3306'

os.environ['RAZORPAY_KEY_ID'] = 'rzp_test_Rc14F02CT2fPnH'
os.environ['RAZORPAY_KEY_SECRET'] = 'K2Mb1ObkXAbao1HOv9Dexf3I'

# --------------------------
# Flask App Initialization
# --------------------------
app = Flask(__name__)
app.secret_key = 'superbikes_secret_key'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --------------------------
# MySQL Config
# --------------------------
dbconfig = {
    "host": os.environ.get("MYSQL_HOST"),
    "user": os.environ.get("MYSQL_USER"),
    "password": os.environ.get("MYSQL_PASSWORD"),
    "database": os.environ.get("MYSQL_DB"),
    "port": int(os.environ.get("MYSQL_PORT", 3306))
}

# Use small pool size for PythonAnywhere
connection_pool = pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=2, **dbconfig)

def get_db_connection():
    return connection_pool.get_connection()

# --------------------------
# Initialize Razorpay client
# --------------------------
razorpay_client = razorpay.Client(auth=(
    os.environ.get("RAZORPAY_KEY_ID"),
    os.environ.get("RAZORPAY_KEY_SECRET")
))



# --------------------------
# Token Serializer (for password reset)
# --------------------------
s = URLSafeTimedSerializer(app.secret_key)

# --------------------------
# Forgot Password
# --------------------------
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            flash("Password reset link feature is disabled (email removed).", "info")
        else:
            flash("Email not found!", "danger")
        return redirect(url_for('show_login'))

    return render_template('forgot_password.html')

# --------------------------
# Reset Password
# --------------------------
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        return "The reset link has expired."
    except BadSignature:
        return "Invalid reset link."

    if request.method == 'POST':
        new_password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE users SET password=%s WHERE email=%s", (new_password, email))
        conn.commit()
        cur.close()
        conn.close()
        flash("Password updated successfully!", "success")
        return redirect(url_for('show_login'))

    return render_template('reset_password.html', token=token)

# --------------------------
# Authentication Routes
# --------------------------
@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        session['user_id'] = user['id']
        session['username'] = user['name']
        session['email'] = user['email']
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid credentials. Please try again.", "danger")
        return redirect(url_for('show_login'))

@app.route('/signup', methods=['POST'])
def signup():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cur.fetchone()

    if existing_user:
        cur.close()
        conn.close()
        return redirect(url_for('show_login', email_exists='true'))

    cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    conn.commit()
    cur.close()
    conn.close()

    flash("Account created successfully! You can now log in.", "success")
    return redirect(url_for('show_login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('show_login'))

# --------------------------
# Contact Us
# --------------------------
@app.route('/contactUs', methods=['GET', 'POST'])
def contactUs():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['mail']
        mob = request.form['mob']
        query = request.form['query']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO contact_messages (name, email, phone, query) VALUES (%s, %s, %s, %s)",
            (name, email, mob, query)
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Your message has been submitted successfully!", "success")
        return redirect(url_for('home'))

    return render_template('contactUs.html')

# --------------------------
# Book Appointment
# --------------------------
@app.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment_page():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            vehicle = request.form['vehicle']
            date_str = request.form['date']
            time = request.form['time']
            area = request.form['area']
            city = request.form['city']
            state = request.form['state']
            post_code = request.form['post_code']
            driving_license = request.form['driving_license']

            if driving_license != "Yes":
                flash("You need a driver's license to book an appointment.", "danger")
                return redirect(url_for('book_appointment_page'))

            appointment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            min_date = (datetime.today() + timedelta(days=3)).date()
            if appointment_date < min_date:
                flash(f'You can only book appointments from {min_date} onwards.', 'danger')
                return redirect(url_for('book_appointment_page'))

            # 💳 Create Razorpay Order (set amount in paise, e.g., ₹100 = 10000)
            order_amount = 200  # ₹2 appointment fee  # ₹100 appointment fee
            order_currency = 'INR'
            order = razorpay_client.order.create(dict(amount=order_amount, currency=order_currency, payment_capture=1))

            # Save appointment before payment
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO appointments (name, email, phone, vehicle, date, time, area, city, state, post_code, driving_license)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, email, phone, vehicle, date_str, time, area, city, state, post_code, driving_license))
            conn.commit()
            cur.close()
            conn.close()

            # Render Razorpay checkout page
            return render_template(
                'razorpay_payment.html',
                order=order,
                name=name,
                email=email,
                phone=phone,
                amount=order_amount,
                razorpay_key=os.environ.get("RAZORPAY_KEY_ID")
            )

        except Exception as e:
            print("Error booking appointment:", e)
            traceback.print_exc()
            flash('Error! Could not book appointment.', 'danger')
            return redirect(url_for('book_appointment_page'))

    return render_template('BookAppointment.html')


@app.route('/payment-success', methods=['POST'])
def payment_success():
    data = request.form.to_dict()
    # Verify signature here if needed
    flash("Payment successful! Appointment confirmed.", "success")
    return redirect(url_for('dashboard'))


# --------------------------
# Sell Bike
# --------------------------
@app.route('/sell-bike', methods=['GET', 'POST'])
def sell_bike_page():
    if request.method == 'POST':
        try:
            # Get form fields (no file uploads)
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            chassis = request.form['chassis']
            plate = request.form['plate']
            years_used = request.form['years_used']
            owners = request.form['owners']

            # Save to database
            conn = get_db_connection()
            cur = conn.cursor()
            sql = """
                INSERT INTO resale_bikes
                (name, email, phone, address, chassis, plate, years_used, owners)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            val = (name, email, phone, address, chassis, plate, years_used, owners)
            cur.execute(sql, val)
            conn.commit()
            cur.close()
            conn.close()

            flash("Your bike details have been submitted successfully!", "success")
            return redirect(url_for('home'))

        except Exception as e:
            print("Error submitting bike:", e)
            flash("Something went wrong. Please try again.", "danger")
            return redirect(url_for('sell_bike_page'))

    # Render form for GET request
    return render_template('resale.html')


# --------------------------
# Dashboard
# --------------------------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, bike_name, bike_image, bike_link FROM wishlist WHERE user_email=%s", (session['email'],))
    wishlist_items = cur.fetchall()
    wishlist = [{"id": i[0], "bike_name": i[1], "bike_image": i[2], "bike_link": i[3]} for i in wishlist_items]

    cur.execute("SELECT id, vehicle, date, time, area, city FROM appointments WHERE email=%s", (session['email'],))
    appt_items = cur.fetchall()
    appointments = [{"id": i[0], "vehicle": i[1], "date": i[2], "time": i[3], "area": i[4], "city": i[5]} for i in appt_items]

    cur.close()
    conn.close()
    return render_template('Dashboard.html', username=session['username'], wishlist=wishlist, appointments=appointments)

# --------------------------
# Wishlist
# --------------------------
@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
    if 'email' not in session:
        return jsonify({'status': 'error', 'message': 'Please login first'})

    data = request.get_json()
    bike_name = data.get('bike_name')
    bike_image = data.get('bike_image')
    bike_link = data.get('bike_link')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM wishlist WHERE user_email=%s AND bike_name=%s", (session['email'], bike_name))
    exists = cur.fetchone()

    if exists:
        cur.close()
        conn.close()
        return jsonify({'status': 'exists', 'message': 'Already in wishlist'})

    cur.execute("INSERT INTO wishlist (user_email, bike_name, bike_image, bike_link) VALUES (%s, %s, %s, %s)",
                (session['email'], bike_name, bike_image, bike_link))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Added to wishlist'})

@app.route('/remove_from_wishlist', methods=['POST'])
def remove_from_wishlist():
    if 'email' not in session:
        return jsonify({"status": "error", "message": "User not logged in"}), 401

    data = request.get_json()
    bike_id = data.get("bike_id")

    if not bike_id:
        return jsonify({"status": "error", "message": "No bike ID provided"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM wishlist WHERE id=%s AND user_email=%s", (bike_id, session['email']))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"status": "success", "message": "Bike removed successfully"})
    except Exception as e:
        print("Error removing bike:", e)
        return jsonify({"status": "error", "message": "Database error"}), 500

# --------------------------
# Static Pages
# --------------------------
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/sportsbike')
def sportsbike():
    return render_template('SportsBike.html')

@app.route('/Naked')
def nacked():
    return render_template('Naked.html')

@app.route('/trourer')
def trourer():
    return render_template('trourer.html')

# --------------------------
# Bike Pages
# --------------------------
@app.route('/ApacheRR310')
def apache_rr310():
    return render_template('Apache RR310.html')

@app.route('/aprillia')
def aprillia():
    return render_template('aprillia.html')

@app.route('/Benelli')
def benelli():
    return render_template('Benelli.html')

@app.route('/BMWS1000RR')
def bmws1000rr():
    return render_template('BMWS1000RR.html')

@app.route('/Ducati916')
def ducati916():
    return render_template('Ducati916.html')

@app.route('/Hayabusa')
def hayabusa():
    return render_template('Hayabusa.html')

@app.route('/Kawasaki')
def kawasaki():
    return render_template('Kawasaki.html')

@app.route('/Ktm')
def ktm():
    return render_template('Ktm.html')

@app.route('/KTM2')
def ktm2():
    return render_template('KTM2.html')

@app.route('/re')
def re():
    return render_template('re.html')

@app.route('/Triumph')
def triumph():
    return render_template('Triumph.html')

@app.route('/YamahaMT07')
def yamaha_mt07():
    return render_template('YamahaMT07.html')

# --------------------------
# Run Flask App
# --------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
