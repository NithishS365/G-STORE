import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="nith@123",
        database="ecommerce_db",
        auth_plugin='mysql_native_password'
    )
    print("Connection successful!")
except mysql.connector.Error as err:
    print(f"Error: {err}")
