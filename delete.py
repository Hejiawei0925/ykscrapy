import pymysql
import os

db =pymysql.connect('127.0.0.1','root','root',db='ykspider')
cursor = db.cursor()

table = 'video_info'

condition = 'vid >= 0'

sql = 'DELETE FROM {table} WHERE {condition}'.format(table=table,condition=condition)

try :
    cursor.execute(sql)
    db.commit()
    command = 'rmdir /s/q C:\\Users\\hjw\\Desktop\\videos'
    os.system(command)
    print(1)
except:
    db.rollback()
    print(0)
db.close()

