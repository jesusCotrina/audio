from flask import Flask, json, jsonify, request,Response
import pymysql
import logging
import sshtunnel
from sshtunnel import SSHTunnelForwarder

app = Flask(__name__)
ssh_host = 'premium284.web-hosting.com'
ssh_username = 'promokmf'
ssh_password = 'Jesus121212$*'
database_username = 'promokmf_jesus_cotrina_123'
database_password = 'julio121212#'
database_name = 'promokmf_audio_transcript'
localhost = '127.0.0.1'

tunnel = SSHTunnelForwarder(
        (ssh_host, 21098),
        ssh_username = ssh_username,
        ssh_password = ssh_password,
        remote_bind_address = ('127.0.0.1', 3306)
    )
    
tunnel.start()

db = pymysql.connect(
        host='127.0.0.1',
        user=database_username,
        passwd=database_password,
        db=database_name,
        port=tunnel.local_bind_port
    )

print("start")
@app.route('/minutes', methods= ['POST']) 
def minutes():
    db.commit()
    json_post=request.json
    json_post = json.dumps(json_post)
    json_post  = json.loads(json_post)
    id_key=json_post["id_key"]
    minutes=json_post["minutes"]
    query="""select total_hours from clients where id_key=%s"""
    tuple1=(id_key,)
    cursor=db.cursor()
    cursor.execute(query,tuple1)
    result=cursor.fetchall()
    for data in result:
        actual_minutes=data[0]

    print("-------",actual_minutes)
    total_minutes=actual_minutes+minutes
    query2="""update clients set total_hours=%s where id_key=%s"""
    tuple2=(total_minutes,id_key)
    cursor=db.cursor()
    cursor.execute(query2,tuple2)
    db.commit()

    if total_minutes >= 600:
        query3="""update clients set hours_state=%s where id_key=%s"""
        tuple3=(False,id_key)
        cursor=db.cursor()
        cursor.execute(query3,tuple3)
        db.commit()

    return "True"


@app.route('/', methods= ['GET']) 
def get():
    return "hello"


@app.route('/identification', methods= ['POST']) 
def identification():
    db.commit()
    json_post=request.json
    json_post = json.dumps(json_post)
    json_post  = json.loads(json_post)
    id_key=json_post["id_key"]
    mac_post=json_post["mac"]
    query="""select * from clients where id_key=%s""" 
    tuple1=(id_key,)
    cursor=db.cursor()
    cursor.execute(query,tuple1)
    result=cursor.fetchall()
    mac_real=""
    state_bill=False
    hours_state=False
    state={}
    for data in result:
        mac_real=data[2]
        state_bill=data[3]
        hours_state=data[5]
    print("mac real",mac_real)
    print("bill",state_bill)

    if mac_post==mac_real:
        if state_bill:
            if hours_state:
                state={"state":"True"}
            else:
                state={"state":"Esta cuenta ya superó los 10 horas limites de transcripción"}
        else:
            state={"state":"Esta cuenta no esta al dia con el pago, pongase en contacto con el administrador"}
    else:
        state={"state":"Esta computadora no esta habilitada para correr el programa"}

    return state


if __name__ == "__main__":
    #app.run(host="localhost")
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(("localhost", 5000), app)
    http_server.serve_forever() 

    db.close()
    print("closing db")
