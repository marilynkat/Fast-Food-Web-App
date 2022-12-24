from flask import Flask, render_template, request, make_response, redirect
from flask_mysql_connector import MySQL, Params
from google.oauth2 import id_token
from google.auth.transport import requests
import json

app = Flask(__name__)
app.config[Params.MYSQL_USER] = '' 
app.config[Params.MYSQL_PASSWORD] = '' 
app.config[Params.MYSQL_DATABASE] = '' 
app.config[Params.MYSQL_HOST] = '' 
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/vote')
def vote():
    return render_template('vote.html')
 
@app.route('/random')
def random():
    return render_template('random.html')

@app.route('/login', methods = ['POST'])
def login():
    # After user logs in with their google account, a cookie is set with their account ID
    tokenid = request.form['credential']
    clientid = '' # Google Auth ClientID
    idinfo = id_token.verify_oauth2_token(tokenid, requests.Request(), clientid)
    user_data = {'username': idinfo['email'], 'name': idinfo['name'], 'id': idinfo['sub']}
    resp = make_response(redirect('/bucketlist'))
    resp.set_cookie('fastfood_userID', user_data['id'])
    print(user_data)
        
    return resp

@app.route('/bucketlist', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def bucketlist():
    if request.method == 'GET':
        userId = request.cookies.get('fastfood_userID')
        print(userId)
        if userId:
            conn = mysql.connection
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM BucketList WHERE userID = %s", (userId,))
            data = cursor.fetchall()
            print(data)
            return render_template('bucketList.html', data=data)
        else:
            return render_template('bucketList_login.html')

    if request.method == 'POST':
        userId = request.cookies.get('fastfood_userID')
        json = request.json
        addBucket = json['resInput']
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("INSERT INTO BucketList (restNameBucket, review, checkedBool, userID)" +
                        " VALUES (%s, %s, %s, %s);", (addBucket, "review", 0, userId))
        mysql.connection.commit()
        cursor.close()
        print(addBucket)
        return json
    
    if request.method == 'PUT':
        userId = request.cookies.get('fastfood_userID')
        json = request.json
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("UPDATE BucketList SET checkedBool = %s WHERE idBucketList = %s AND userID = %s", 
                       (json['checkStatus'], json['id'], userId))
        mysql.connection.commit()
        cursor.close()
        return json

    if request.method == 'DELETE':
        userId = request.cookies.get('fastfood_userID')
        json = request.json
        deleteBucket = json['resID']
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("DELETE FROM BucketList WHERE idBucketList = %s AND userID = %s;", (deleteBucket, userId))
        mysql.connection.commit()
        cursor.close()
        return json
    
if __name__ == '__main__':
    app.run()
