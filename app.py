import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import datetime, timedelta
import threading
import traceback
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

# --------------------------
# Flask App Initialization
# --------------------------
app = Flask(__name__)
app.secret_key = 'superbikes_secret_key'

mysql = MySQL(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MYSQL_POOL_NAME'] = 'mypool'
app.config['MYSQL_POOL_SIZE'] = 5

# --------------------------
# MySQL Config (from env vars)
# --------------------------
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')

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
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()
        cur.close()

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
        cur = mysql.connection.cursor()
        cur.execute("UPDATE users SET password=%s WHERE email=%s", (new_password, email))
        mysql.connection.commit()
        cur.close()
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

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cur.fetchone()
    cur.close()

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

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cur.fetchone()

    if existing_user:
        cur.close()
        return redirect(url_for('show_login', email_exists='true'))

    cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    mysql.connection.commit()
    cur.close()

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

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO contact_messages (name, email, phone, query) VALUES (%s, %s, %s, %s)",
            (name, email, mob, query)
        )
        mysql.connection.commit()
        cur.close()

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

            cursor = mysql.connection.cursor()
            query = """
                INSERT INTO appointments 
                (name, email, phone, vehicle, date, time, area, city, state, post_code, driving_license)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, email, phone, vehicle, date_str, time, area, city, state, post_code, driving_license))
            mysql.connection.commit()
            cursor.close()

            flash('Appointment booked successfully!', 'success')
            return redirect(url_for('home'))

        except Exception as e:
            print("Error booking appointment:", e)
            traceback.print_exc()
            flash('Error! Could not book appointment.', 'danger')
            return redirect(url_for('book_appointment_page'))

    return render_template('BookAppointment.html')

# --------------------------
# Sell Bike
# --------------------------
@app.route('/sell-bike', methods=['GET', 'POST'])
def sell_bike_page():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            chassis = request.form['chassis']
            plate = request.form['plate']
            years_used = request.form['years_used']
            owners = request.form['owners']
            rc_image = request.files['rc_image']
            bike_image = request.files['bike_image']

            rc_path = os.path.join(app.config['UPLOAD_FOLDER'], rc_image.filename)
            bike_path = os.path.join(app.config['UPLOAD_FOLDER'], bike_image.filename)
            rc_image.save(rc_path)
            bike_image.save(bike_path)

            cursor = mysql.connection.cursor()
            sql = """
                INSERT INTO resale_bikes 
                (name, email, phone, address, chassis, plate, rc_image, bike_image, years_used, owners)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            val = (name, email, phone, address, chassis, plate, rc_path, bike_path, years_used, owners)
            cursor.execute(sql, val)
            mysql.connection.commit()
            cursor.close()

            flash("Your bike details have been submitted successfully!", "success")
            return redirect(url_for('home'))

        except Exception as e:
            print("Error submitting bike:", e)
            flash("Something went wrong. Please try again.", "danger")
            return redirect(url_for('sell_bike_page'))

    return render_template('resale.html')

# --------------------------
# Dashboard
# --------------------------
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('show_login'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, bike_name, bike_image, bike_link FROM wishlist WHERE user_email=%s", (session['email'],))
    wishlist_items = cur.fetchall()
    wishlist = [{"id": i[0], "bike_name": i[1], "bike_image": i[2], "bike_link": i[3]} for i in wishlist_items]

    cur.execute("SELECT id, vehicle, date, time, area, city FROM appointments WHERE email=%s", (session['email'],))
    appt_items = cur.fetchall()
    appointments = [{"id": i[0], "vehicle": i[1], "date": i[2], "time": i[3], "area": i[4], "city": i[5]} for i in appt_items]

    cur.close()
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

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM wishlist WHERE user_email=%s AND bike_name=%s", (session['email'], bike_name))
    exists = cur.fetchone()

    if exists:
        cur.close()
        return jsonify({'status': 'exists', 'message': 'Already in wishlist'})

    cur.execute("INSERT INTO wishlist (user_email, bike_name, bike_image, bike_link) VALUES (%s, %s, %s, %s)",
                (session['email'], bike_name, bike_image, bike_link))
    mysql.connection.commit()
    cur.close()
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
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM wishlist WHERE id=%s AND user_email=%s", (bike_id, session['email']))
        mysql.connection.commit()
        cur.close()
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
