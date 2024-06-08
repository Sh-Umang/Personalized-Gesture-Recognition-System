import sqlite3 as sq

class DBConnector:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None
        
    def connect(self):
        self.connection = sq.connect(self.db_path)

    def close(self):
        if self.connection:
            self.connection.close()

    def execute(self, query, parameters = None):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("pragma foreign_keys = on")
            # print(parameters)
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            # fetching once clears the cursor i.e. once fetched, cursor is empty
            result = cursor.fetchall()

            #if its a read query, return result of read
            if query.strip().lower().startswith("select"):
                return result 

        
db_connector = DBConnector('D:/Programming/db_gesture.db')
db_connector.connect()
# print("DB")
# result = db_connector.execute("select * from Gesture")
# for row, row_item in enumerate(result):
#     for col, col_item in enumerate(row_item):
#         print(col_item)
query = "select gesture_name from Gesture where gesture_id = ?"
parameter = (10,)
result = db_connector.execute(query, parameter)
print(result)
