import mysql.connector


def connection():
    conn = mysql.connector.connect(user='crushyna@flaskappmysqlserver', password='AllsoP1234',
                                   host='flaskappmysqlserver.mysql.database.azure.com', database='flaskapp')

    c = conn.cursor(buffered=True)

    return c, conn
