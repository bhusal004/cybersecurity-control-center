import mysql.connector as db


# Database connection
conn = db.connect(
    host="localhost",
    user="root",
    password="Kimtaehyung23@",
    database="linuxproject"
   
)


# Create cursor
cursor = conn.cursor()
# create_database_query="create database linuxProject"

# cursor.execute(create_database_query)


# create_table = "CREATE TABLE register_form (s_no INT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(40) NOT NULL,email VARCHAR(50) NOT NULL,password VARCHAR(40),phone VARCHAR(20),gender VARCHAR(50),course VARCHAR(50))"
# cursor.execute(create_table)
# conn.commit()



# print("Database connected successfully!")
