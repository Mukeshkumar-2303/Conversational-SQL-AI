import sqlite3

# connection setup sql
connection = sqlite3.connect("student.db")

# cursor creation
cursor = connection.cursor()

# create the table
table_info = """
CREATE TABLE STUDENT(
    NAME VARCHAR(25),
    CLASS VARCHAR(25),
    SECTION VARCHAR(25),
    MARKS INT
)
"""

# execution sql query
cursor.execute(table_info)

## Insert some more records

cursor.execute('''INSERT INTO STUDENT values('Krish','Data Science','A',90)''')

cursor.execute('''INSERT INTO STUDENT values('John','Data Science','B',100)''')

cursor.execute('''INSERT INTO STUDENT values('Mukesh','Data Science','A',86)''')

cursor.execute('''INSERT INTO STUDENT values('Jacob','DEVOPS','A',50)''')

cursor.execute('''INSERT INTO STUDENT values('Dipesh','DEVOPS','A',35)''')

# display all the records

print("The inserted records are")

data = cursor.execute('''SELECT * FROM STUDENT''')

for row in data:
    print(row)

# commit changes in the db
connection.commit()

# close the db
connection.close()