import pymysql
from flask_bcrypt import Bcrypt
from flask import Flask, render_template, request, redirect, url_for, session
import uuid
import hashlib

app = Flask(__name__)

app.secret_key = 'session-key'
bcrypt = Bcrypt(app)

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='your-mysql-password',
    database='travel'
)


@app.route("/")
def index():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conpassword = request.form['confirm_password']
        if password != conpassword:
            return render_template('register.html', error="Password and Confirm Password do not match.")
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        email = request.form['email']
        phoneno = request.form['phoneno']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        if user:
            return render_template('register.html', error="Email already exists. Please use a different email.")
        cursor.execute("INSERT INTO user (username, password, email, phoneno) VALUES (%s, %s, %s, %s)", (username, hashed_password, email, phoneno))
        connection.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user[5] == 'admin':
            return redirect(url_for('admdashboard'))
        elif user and bcrypt.check_password_hash(user[2], password):
            session['user_data'] = user  
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('nouser'))

    # If the user is already logged in
    if 'user_data' in session:
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route("/dashboard", methods = ['POST', 'GET'])
def dashboard():
    if 'user_data' in session:
        user = session['user_data']
        user_id = user[0]
        
        cursor = connection.cursor()
        cursor.execute("SELECT b.bookid, t.tname, t.tdesc, b.num_travelers FROM booking b JOIN tour t ON b.tourid = t.tourid WHERE b.userid = %s", (user_id,))
        bookings = cursor.fetchall()

        return render_template('dashboard.html', user = user, bookings=bookings)
    else:
        return redirect(url_for('login'))

@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    if 'user_data' in session:
        user_id = session['user_data'][0]
        booking_id = int(request.form.get('booking_id'))

        # Delete the booking from the database
        cursor = connection.cursor()
        cursor.execute("DELETE FROM booking WHERE userid = %s AND bookid = %s", (user_id, booking_id))
        connection.commit()

        # Redirect back to the dashboard with the updated bookings
        return redirect(url_for('dashboard'))
    else:
        # Redirect to the login page if the user is not logged in
        return redirect(url_for('login'))


@app.route("/nouser", methods=['GET', 'POST'])
def nouser():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['user_data'] = user  
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('nouser'))
    return render_template('nouser.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']
        message = request.form['message']
        cursor = connection.cursor()
        cursor.execute("INSERT INTO contactus (mname, memail, maddress, message) VALUES (%s, %s, %s, %s)", (name, email, address, message))
        connection.commit()
        cursor.close()
        return redirect(url_for('index'))
    return render_template('contact.html')


@app.route("/about")
def about():
    return render_template('about.html')

from flask import render_template, redirect, url_for, session

@app.route('/packages', methods=['GET', 'POST'])
def packages():
    if 'user_data' in session:
        if request.method == 'POST':
            tour_id = int(request.form.get('tour_id'))
            num_people = int(request.form.get('num_people'))
            session['tour_id'] = tour_id
            session['num_people'] = num_people

            return redirect(url_for('transport'))
    else:
        return redirect(url_for('login'))

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tour")
    data = cursor.fetchall()
    cursor.close()
    return render_template('packages.html', pkg=data)

    
@app.route('/payment', methods=['GET','POST'])
def payment():
    user_data = session.get('user_data', {})
    user_id = user_data[0]
    tour_id = session.get('tour_id', {})
    num_people = session.get('num_people', {})
    transport_id = session.get('transport_id', {})
    cursor = connection.cursor()
    cursor.execute("INSERT INTO booking (userid, tourid, num_travelers, transportid) VALUES (%s, %s, %s, %s)", (user_id, tour_id, num_people, transport_id))
    cursor.execute("SELECT trprice FROM transportation WHERE transportid = %s",(transport_id,))
    trcost = cursor.fetchone()[0]
    cursor.execute("SELECT cost FROM tour WHERE tourid = %s", (tour_id,))
    tourcost = cursor.fetchone()[0]
    total_cost = int(tourcost) * int(num_people) + int(trcost)
    connection.commit()
    cursor.close()
    return render_template('payment.html', total_cost = total_cost)

@app.route('/transport', methods=['GET', 'POST'])
def transport():
    if request.method == 'POST':
        transport_id = int(request.form.get('transport_id'))
        session['transport_id'] = transport_id
        return redirect(url_for('payment'))
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM transportation")
    data = cursor.fetchall()
    return render_template('transport.html', vehicle=data)

@app.route('/logout')
def logout():
    session.pop('user_data', None)  

    return redirect(url_for('login'))


# @app.route('/admin/login', methods=['GET', 'POST'])
# def adlogin():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if username == 'admin' and password == 'admin':
#             session['admin'] = True  
#             return redirect(url_for('admdashboard'))
#         else:
#             return redirect(url_for('nouser'))
#     return render_template('admin_login.html')

@app.route("/admin/dashboard")
def admdashboard():
    return render_template('admin_dashboard.html')


@app.route("/allbookings", methods = ['POST', 'GET'])
def allbookings():
    cursor = connection.cursor()
    #join
    cursor.execute("SELECT b.bookid, t.tname, u.username, b.num_travelers, b.total_cost, tr.trname FROM booking b JOIN tour t ON b.tourid = t.tourid JOIN user u ON b.userid = u.userid JOIN transportation tr ON b.transportid = tr.transportid")
    bookings = cursor.fetchall()
    #procedure
    cursor.execute('CALL generate_booking_stats()')
    stats = cursor.fetchone()
    #aggregate
    cursor.execute("SELECT user.userid, user.username, IFNULL(COUNT(booking.tourid), 0) AS number_booked FROM user LEFT JOIN booking ON user.userid = booking.userid WHERE user.userid <> 1 GROUP BY user.userid, user.username")
    result = cursor.fetchall()
    #nested query
    cursor.execute("SELECT trname AS transport, number_of_tours AS tours_per_transport FROM (SELECT t.trname, COUNT(b.tourid) AS number_of_tours FROM transportation t LEFT JOIN booking b ON t.transportid = b.transportid GROUP BY t.trname) AS transport_stats GROUP BY transport")
    tresult = cursor.fetchall()
    return render_template('all_bookings.html', stats=stats, bookings=bookings, result = result, tresult = tresult)    

@app.route('/cancel_tour', methods=['POST'])
def cancel_tour():
    tour_id = int(request.form.get('tour_id'))
    cursor = connection.cursor()
    cursor.execute("DELETE FROM booking WHERE tourid = %s", (tour_id,))
    connection.commit()

    cursor.execute("DELETE FROM tour WHERE tourid = %s", (tour_id,))
    connection.commit()
    return redirect(url_for('admdashboard'))

@app.route('/admin/messages')
def admin_messages():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM contactus")
    messages = cursor.fetchall()
    return render_template('admin_messages.html', messages=messages)

@app.route('/deltours', methods=['GET', 'POST'])
def deltours():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tour")
    data = cursor.fetchall()
    return render_template('del_book.html', pkg=data)


@app.route('/addtours', methods=['GET', 'POST'])
def addtours():
    if request.method == 'POST':
        tname = request.form['tourname']
        tdesc = request.form['tourdesc']
        price = request.form['price']
        tourimg = request.form['img']
        duration = request.form['duration']
        cursor = connection.cursor()
        cursor.execute("INSERT INTO tour (tname, tdesc, cost, imgsrc, duration) VALUES (%s, %s, %s, %s, %s)", (tname, tdesc, price, tourimg, duration))
        connection.commit()
        cursor.close()
        return redirect(url_for('admdashboard'))
    return render_template('add_tour.html')


if __name__ == "__main__":
  app.run(host = '0.0.0.0', debug = True)
