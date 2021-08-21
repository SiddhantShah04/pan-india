from flaskr.db import get_db

def activity(userId,table,description,event):
        db = get_db()
        cur = db.cursor()
        print((table,description,event))
        sql = "INSERT INTO activityLog(table) VALUES (%s)"
    
        cur.execute("INSERT INTO activityLog(userId,tableName,description,event) VALUES (%s,%s,%s,%s)",(userId,table,description,event))        
        db.commit()
        