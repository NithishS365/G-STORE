
from flask import Flask, render_template, request, redirect, session , flash
import mysql.connector
from db import get_connection
import random 
app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        gender = request.form['gender']
        dob = request.form['dob']
        address = request.form['address']
        password = request.form['password']
        role = request.form['role']

        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (full_name, username, email, phone, gender, dob, address, password, role)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (full_name, username, email, phone, gender, dob, address, password, role))

            conn.commit()
            return redirect('/login')
        except mysql.connector.Error as err:
            return f"Error: {err}"
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error=None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = user
            if user['role'] == 'customer':
                return redirect('/customer')
            elif user['role'] == 'seller':
                return redirect('/seller') 
        else:
            error = "Invalid username or password"  
    return render_template('login.html', error=error)

    
# @app.route('/error')
# def error():
#     return render_template('error.html')
    
@app.route('/customer',methods=['GET', 'POST'])
def customer_dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template("customer_dashboard.html", products=products)

@app.route('/buy/<int:id>',methods=['GET', 'POST'])
def buy_now(id):
    user = session.get('user')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products WHERE id=%s", (id,))
    product = cursor.fetchone()
    conn.close()
    return render_template("buy_now.html", user=user, product=product)

@app.route('/seller')
def seller_dashboard():
    if session['user']['role'] != 'seller':
        return redirect('/')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return render_template("seller_dashboard.html", products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        image_url = request.form['image_url']
        price = float(request.form['price'])
        seller_name = request.form['seller_name']
        offer = random.randint(10, 50)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (name, description, image_url, price, seller_name, offer_percentage) VALUES (%s, %s, %s, %s, %s, %s)",
                       (name, description, image_url, price, seller_name, offer))
        conn.commit()
        return redirect('/seller')
    return render_template('add_product.html')

@app.route('/delete_product/<int:id>', methods=['POST'])
def delete_product(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect('/seller')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
