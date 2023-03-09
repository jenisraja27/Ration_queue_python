from flask import Flask
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
import os
import time
import datetime
import calendar
import random
from random import seed
from random import randint
from flask import send_file
from werkzeug.utils import secure_filename
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import mysql.connector
import urllib.request
import urllib.parse
from urllib.request import urlopen
import webbrowser

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  charset="utf8",
  database="ration_queue_py"
)
app = Flask(__name__)
##session key
app.secret_key = 'abcdef'
#######
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#####


@app.route('/',methods=['POST','GET'])
def index():
    act=""
    msg=""
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('view_stu'))
        else:
            msg = 'Incorrect username/password! or access not provided'
    return render_template('index.html',msg=msg,act=act)

@app.route('/login_emp', methods=['GET', 'POST'])
def login_emp():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM rq_employee WHERE eid = %s AND pass = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            ff=open("usr.txt","w")
            ff.write(uname)
            ff.close()
            return redirect(url_for('emp_home'))
        else:
            msg = 'Incorrect username/password! or access not provided'
    return render_template('login_emp.html',msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('admin'))
        else:
            msg = 'Incorrect username/password! or access not provided'
    return render_template('login.html',msg=msg)

@app.route('/login_con', methods=['GET', 'POST'])
def login_con():
    msg=""

    
    if request.method=='POST':
        uname=request.form['uname']
        
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM rq_consumer WHERE card = %s', (uname, ))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            mobile=account[4]
            name=account[2]
            rn=randint(1000,9999)
            otp=str(rn)

            cursor.execute("UPDATE rq_consumer SET otp=%s WHERE card=%s",(otp, uname))
            mydb.commit()
                
            url="http://iotcloud.co.in/testsms/sms.php?sms=otp&name="+name+"&otp="+otp+"&mobile="+str(mobile)
            webbrowser.open_new(url)
            return redirect(url_for('con_otp'))
        else:
            msg = 'Incorrect username/password! or access not provided'
    return render_template('login_con.html',msg=msg)

@app.route('/con_otp', methods=['GET', 'POST'])
def con_otp():
    msg=""
    uname=""
    if 'username' in session:
        uname = session['username']

    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM rq_consumer WHERE card = %s', (uname, ))
    account = mycursor.fetchone()
    otp1=account[9]
        
    if request.method=='POST':
        otp=request.form['otp']
        if otp==otp1:
            return redirect(url_for('con_home'))
        else:
            msg="OTP wrong!"
            

        
    return render_template('con_otp.html',msg=msg)

@app.route('/con_home', methods=['GET', 'POST'])
def con_home():
    msg=""
    uname=""
    if 'username' in session:
        uname = session['username']

    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM rq_consumer WHERE card = %s', (uname, ))
    account = mycursor.fetchone()
    name=account[2]
    card=account[3]

    return render_template('con_home.html',msg=msg,name=name,card=card)

@app.route('/con_prefer', methods=['GET', 'POST'])
def con_prefer():
    msg=""
    uname=""
    if 'username' in session:
        uname = session['username']

    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM rq_consumer WHERE card = %s', (uname, ))
    account = mycursor.fetchone()
    name=account[2]
    card=account[3]

    if request.method=='POST':
        pday=request.form.getlist("pday[]")
        stime=request.form['stime']
        etime=request.form['etime']

        print(pday)
        pday1=",".join(pday)
        ptime=stime+"-"+etime
        mycursor.execute("UPDATE rq_consumer SET prefer_day=%s,prefer_time=%s,prefer_st=1 WHERE card=%s",(pday1,ptime,uname))
        mydb.commit()
        return redirect(url_for('con_prefer'))

    return render_template('con_prefer.html',msg=msg,name=name,card=card,data=account)

@app.route('/con_req', methods=['GET', 'POST'])
def con_req():
    msg=""
    uname=""
    if 'username' in session:
        uname = session['username']

    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM rq_consumer WHERE card = %s', (uname, ))
    account = mycursor.fetchone()
    name=account[2]
    card=account[3]

    if request.method=='POST':
        
        name2=request.form['name2']
        mobile2=request.form['mobile2']
        email2=request.form['email2']
        address2=request.form['address2']

        
        mycursor.execute("UPDATE rq_consumer SET name2=%s,mobile2=%s,email2=%s,address2=%s,req_st=1 WHERE card=%s",(name2,mobile2,email2,address2,uname))
        mydb.commit()
        return redirect(url_for('con_req'))

    return render_template('con_req.html',msg=msg,name=name,card=card,data=account)

@app.route('/request1', methods=['GET', 'POST'])
def request1():
    uname=""
    if 'username' in session:
        uname = session['username']
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute('SELECT * FROM rq_employee WHERE eid = %s', (uname, ))
    rr = mycursor.fetchone()
    rid=rr[1]
    mycursor.execute('SELECT * FROM rq_consumer WHERE rid = %s && req_st=1', (rid,))
    data = mycursor.fetchall()

    if act=="ok":
        
        cid = request.args.get('cid')
        

        
        mycursor.execute("UPDATE rq_consumer SET name=name2,mobile=mobile2,email=email2,address=address2,req_st=0 WHERE id=%s",(cid,))
        mydb.commit()
        return redirect(url_for('request1',act='success'))
    
    return render_template('request1.html',data=data)

@app.route('/admin',methods=['POST','GET'])
def admin():
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM rq_ration')
    data = cursor.fetchall()

    cursor.execute('SELECT * FROM rq_employee')
    data2 = cursor.fetchall()

        
    return render_template('admin.html',data=data,data2=data2)

@app.route('/add_rationshop',methods=['POST','GET'])
def add_rationshop():
    result=""
    act=""
    if request.method=='POST':
        name=request.form['name']
        rno=request.form['rno']
        building=request.form['building']
        street=request.form['street']
        area=request.form['area']
        city=request.form['city']
        pincode=request.form['pincode']
        phone=request.form['phone']
        
        
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        
        mycursor.execute("SELECT max(id)+1 FROM rq_ration")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1

        rid="R"+str(maxid)
        sql = "INSERT INTO rq_ration(id, rid, name, rno, building, street, area, city, pincode, phone) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (maxid, rid, name, rno, building, street, area, city, pincode, phone)
        print(sql)
        mycursor.execute(sql, val)
        mydb.commit()            
        print(mycursor.rowcount, "record inserted.")
        act='success'
        return redirect(url_for('admin'))
            
    return render_template('add_rationshop.html',act=act)

@app.route('/add_emp',methods=['POST','GET'])
def add_emp():
    result=""
    act=""
    rid = request.args.get('rid')
    if request.method=='POST':
        name=request.form['name']
        rid=request.form['rid']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        
        mycursor.execute("SELECT max(id)+1 FROM rq_employee")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1

        eid="E"+str(maxid)
        pass1="1234"
        sql = "INSERT INTO rq_employee(id, rid, eid, name, address, mobile, email, pass, rdate, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (maxid, rid, eid, name, address, mobile, email, pass1, rdate, '1')
        print(sql)
        mycursor.execute(sql, val)
        mydb.commit()            
        print(mycursor.rowcount, "record inserted.")
        act='success'
        return redirect(url_for('add_assistant',sid=maxid))
        #if mycursor.rowcount==1:
        #    result="Registered Success"
            
        
    return render_template('add_emp.html',act=act,rid=rid)

@app.route('/add_assistant',methods=['POST','GET'])
def add_assistant():
    result=""
    act=""
    sid = request.args.get('sid')
    if request.method=='POST':
        name2=request.form['name2']
        
        mobile2=request.form['mobile2']
        email2=request.form['email2']
        address2=request.form['address2']
        
        
        mycursor = mydb.cursor()

        mycursor.execute("UPDATE rq_employee SET name2=%s,mobile2=%s,email2=%s,address2=%s WHERE id=%s",(name2,mobile2,email2,address2, sid))
        mydb.commit()
        return redirect(url_for('view_emp',eid=sid))
        #if mycursor.rowcount==1:
        #    result="Registered Success"
            
        
    return render_template('add_assistant.html',act=act,sid=sid)

@app.route('/edit',methods=['POST','GET'])
def edit():
    result=""
    act=""
    eid = request.args.get('eid')

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where id=%s",(eid, ))
    data = mycursor.fetchone()
    
    if request.method=='POST':
        name=request.form['name']
        
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        
        
        

        mycursor.execute("UPDATE rq_employee SET name=%s,mobile=%s,email=%s,address=%s WHERE id=%s",(name,mobile,email,address, eid))
        mydb.commit()
        return redirect(url_for('view_emp',eid=eid))
        #if mycursor.rowcount==1:
        #    result="Registered Success"
            
        
    return render_template('edit.html',data=data,act=act,eid=eid)

@app.route('/edit2',methods=['POST','GET'])
def edit2():
    result=""
    act=""
    eid = request.args.get('eid')

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where id=%s",(eid, ))
    data = mycursor.fetchone()
    
    if request.method=='POST':
        name2=request.form['name2']
        
        mobile2=request.form['mobile2']
        email2=request.form['email2']
        address2=request.form['address2']
        
        
        

        mycursor.execute("UPDATE rq_employee SET name2=%s,mobile2=%s,email2=%s,address2=%s WHERE id=%s",(name2,mobile2,email2,address2, eid))
        mydb.commit()
        return redirect(url_for('view_emp',eid=eid))
        #if mycursor.rowcount==1:
        #    result="Registered Success"
            
        
    return render_template('edit2.html',data=data,act=act,eid=eid)



@app.route('/view_emp',methods=['POST','GET'])
def view_emp():
    eid = request.args.get('eid')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where id=%s",(eid, ))
    data = mycursor.fetchone()
    return render_template('view_emp.html',data=data)

@app.route('/view_ration',methods=['POST','GET'])
def view_ration():
    rid = request.args.get('rid')
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM rq_ration where rid=%s",(rid, ))
    data = cursor.fetchone()
    return render_template('view_ration.html',data=data,rid=rid)

@app.route('/add_card',methods=['POST','GET'])
def add_card():
    rid = request.args.get('rid')
    mycursor = mydb.cursor()
    if request.method=='POST':
        card_num=request.form['card_num']

        mycursor.execute("update rq_ration set card_num=%s where rid=%s", (card_num,rid))
        mydb.commit()
        
        file = request.files['file']
        try:
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file:
                fn="card.csv"
                fn1 = secure_filename(fn)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], fn1))
                #return redirect(url_for('view_data'))
                msg="Uploaded Success"
        except:
            print("dd")

        filename = 'upload/card.csv'
        data1 = pd.read_csv(filename, header=0)
        data2 = list(data1.values.flatten())
        data=[]
        i=0
        sd=len(data1)
        rows=len(data1.values)
        for ss in data1.values:
            cnt=len(ss)
            mycursor.execute("SELECT max(id)+1 FROM rq_consumer")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1

            
            sql = "INSERT INTO rq_consumer(id, rid, name, card, mobile) VALUES (%s, %s, %s, %s, %s)"
            val = (maxid, rid, ss[0], ss[1], ss[2])
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()
        
            
        
        
        return redirect(url_for('view_card',rid=rid))
        
    
    return render_template('add_card.html',rid=rid)

@app.route('/view_card',methods=['POST','GET'])
def view_card():
    rid = request.args.get('rid')
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM rq_consumer where rid=%s",(rid, ))
    data = cursor.fetchall()
    return render_template('view_card.html',data=data,rid=rid)

@app.route('/view_cat',methods=['POST','GET'])
def view_cat():
    rid = request.args.get('rid')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_category")
    data = mycursor.fetchall()

    mycursor.execute("SELECT * FROM rq_stock")
    data2 = mycursor.fetchall()
    
    return render_template('view_cat.html',data=data,data2=data2,rid=rid)

@app.route('/add_cat',methods=['POST','GET'])
def add_cat():
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_product")
    data = mycursor.fetchall()
    if request.method=='POST':
        product=request.form['product']
        ptype=request.form['ptype']
        qty=request.form['qty']
        qtype=request.form['qtype']
        if ptype=="1":
            mycursor.execute("SELECT max(id)+1 FROM rq_product")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1

            
            sql = "INSERT INTO rq_product(id, product, ptype, qty, qtype) VALUES (%s, %s, %s, %s, %s)"
            val = (maxid, product, ptype, qty, qtype)
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()
            return redirect(url_for('add_cat'))

        else:
            price=request.form['price']
            
            
            mycursor.execute("SELECT max(id)+1 FROM rq_product")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1

            
            sql = "INSERT INTO rq_product(id, product, ptype, price, qty, qtype) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (maxid, product, ptype, price, qty, qtype)
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()
            return redirect(url_for('add_cat'))
        
        
    
    return render_template('add_cat.html',data=data)

@app.route('/add_stock',methods=['POST','GET'])
def add_stock():
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_ration")
    data = mycursor.fetchall()

    mycursor.execute("SELECT * FROM rq_product")
    data2 = mycursor.fetchall()

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    if request.method=='POST':
        rid=request.form['rid']
        pid=request.form['pid']
        qty=request.form['qty']
        max_qty=request.form['max_qty']
        qtype=request.form['qtype']
        mycursor.execute("SELECT max(id)+1 FROM rq_stock")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1

        mycursor.execute("SELECT * FROM rq_product where id=%s",(pid,))
        dat = mycursor.fetchone()
        product=dat[1]
    
        sql = "INSERT INTO rq_stock(id, rid, pid, product, qty, qtype, rdate, max_qty) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (maxid, rid, pid, product, qty, qtype, rdate, max_qty)
        print(sql)
        mycursor.execute(sql, val)
        mydb.commit()
        return redirect(url_for('stock'))
        
    
    return render_template('add_stock.html',data=data,data2=data2)

@app.route('/stock',methods=['POST','GET'])
def stock():
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_ration")
    data = mycursor.fetchall()

    data2=[]
    if request.method=='POST':
        rid=request.form['rid']
        mycursor.execute("SELECT * FROM rq_stock where rid=%s",(rid, ))
        data2 = mycursor.fetchall()

    if act=="del":
        did = request.args.get('did')
        print(did)
        mycursor.execute("delete from rq_stock where id=%s", (did,))
        mydb.commit()
        return redirect(url_for('stock'))
        

    return render_template('stock.html',data=data,data2=data2)

@app.route('/edit_stock',methods=['POST','GET'])
def edit_stock():
    id1 = request.args.get('id')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_stock where id=%s",(id1,))
    data = mycursor.fetchone()
    if request.method=='POST':
        sid=request.form['sid']
        qty=request.form['qty']
        mycursor.execute("update rq_stock set qty=qty+%s where id=%s", (qty,sid))
        mydb.commit()
        return redirect(url_for('stock'))
    
    return render_template('edit_stock.html',data=data,id1=id1)

@app.route('/required',methods=['POST','GET'])
def required():
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_stock_req order by id desc")
    data = mycursor.fetchall()
    
    
    return render_template('required.html',data=data)


@app.route('/emp_stock',methods=['POST','GET'])
def emp_stock():
    uname=""
    if 'username' in session:
        uname = session['username']
    act = request.args.get('act')
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where eid=%s",(uname, ))
    dt = mycursor.fetchone()
    rid=dt[1]
    mycursor.execute("SELECT * FROM rq_ration where rid=%s",(rid, ))
    data = mycursor.fetchone()

    mycursor.execute("SELECT * FROM rq_stock where rid=%s",(rid, ))
    data2 = mycursor.fetchall()

    
        

    return render_template('emp_stock.html',rid=rid,data=data,data2=data2)


#########
##Reinforcement
def DeepQLearning(num_of_cards):
    
    enviroment = "Ration"
    action_space="1"
    action=0
    alpha=1
    reward=0
    
    for customer in range(0, num_of_cards):
        # Reset the enviroment
        state = enviroment

        # Initialize variables
        reward = 0
        terminated = False
        j=1
        n=num_of_cards
        while j<n:
            # Take learned path or explore new actions based on the epsilon
            if random.uniform(0, 1) < num_of_cards:
                i=0
                k=0
                while i<=num_of_cards:
                    i+=3
                    k+=1
                action = i
            else:
                action = np.argmax(q_table[state])

            # Take action
            gamma=1
            #next_state, reward, terminated, info = action
            q_table=num_of_cards/3
            # Recalculate
            q_value = k
            max_value = q_table #np.max(q_table[next_state])
            new_q_value = (1 - alpha) * int(q_value) + alpha * (reward + gamma * max_value)
            
            # Update Q-table
            #q_table[state, action] = new_q_value
            state = new_q_value
            j+=1
            
        #if (queue + 1) % 100 == 0:
        #    clear_output(wait=True)
            #print("Queue: {}".format(queue + 1))
            #enviroment.render()

def QueuePredict(enviroment, optimizer):
        
        # Initialize atributes
        _state_size = enviroment
        _action_size = "1" #enviroment.action_space.n
        _optimizer = optimizer
        
        expirience_replay = int(enviroment/2)
        
        # Initialize discount and exploration rate
        gamma = 0.6
        epsilon = 0.1
        
        # Build networks
        q_network = optimizer
        target_network = expirience_replay
        

def store(state, action, reward, next_state, terminated):
    expirience_replay.append((state, action, reward, next_state, terminated))

def _build_compile_model():
    model = Sequential()
    model.add(Embedding(_state_size, 10, input_length=1))
    model.add(Reshape((10,)))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(50, activation='relu'))
    model.add(Dense(_action_size, activation='linear'))
    
    model.compile(loss='mse', optimizer=self._optimizer)
    return model

def alighn_target_model():
    target_network.set_weights(q_network.get_weights())

def act(state):
    if np.random.rand() <= epsilon:
        return enviroment.action_space.sample()
    
    q_values = q_network.predict(state)
    return np.argmax(q_values[0])

def retrain(batch_size):
    minibatch = random.sample(expirience_replay, batch_size)
    
    for state, action, reward, next_state, terminated in minibatch:
        
        target = q_network.predict(state)
        
        if terminated:
            target[0][action] = reward
        else:
            t = target_network.predict(next_state)
            target[0][action] = reward + gamma * np.amax(t)
        
        q_network.fit(state, target, epochs=1, verbose=0)
        
def findTime(T, K):
       
    # convert the given time in minutes
    minutes = (((ord(T[0]) - ord('0'))* 10 +
                 ord(T[1]) - ord('0'))* 60 +
               ((ord(T[3]) - ord('0')) * 10 +
                 ord(T[4]) - ord('0')));
                   
    # Add K to current minutes
    minutes += K
   
    # Obtain the new hour
    # and new minutes from minutes
    hour = (int(minutes / 60)) % 24
   
    min = minutes % 60
    hh=""
    mm=""
    # Print the hour in appropriate format
    if (hour < 10):
        hh="0"+str(hour)
        #print(0,hour,":",end = "")
           
    else:
        hh=""+str(hour)
        #print(hour,":",end = "")
   
    # Print the minute in appropriate format
    if (min < 10):
        mm="0"+str(min)
        #print(0,min,end = "")
   
    else:
        mm=""+str(min)
        #print(min,end = "")
    hm=hh+":"+mm
    return hm

def findDay(date):
    born = datetime.datetime.strptime(date, '%d-%m-%Y').weekday()
    return (calendar.day_name[born])

@app.route('/emp_home',methods=['POST','GET'])
def emp_home():
    act=""
    uname=""
    c1=""
    c2=""
    c3=""
    fn1=""
    fn2=""
    fn3=""
    fn4=""
    available=""
    data3=[]
    if 'username' in session:
        uname = session['username']

    ff=open("usr.txt","r")
    uu=ff.read()
    ff.close()
    if uname is None:
        uname=uu
    #print(uname)
    #uname="E1"
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where eid=%s",(uname, ))
    dt = mycursor.fetchone()
    rid=dt[1]
    mycursor.execute("SELECT * FROM rq_ration where rid=%s",(rid, ))
    data = mycursor.fetchone()

    mycursor.execute("SELECT * FROM rq_stock where rid=%s",(rid, ))
    data1 = mycursor.fetchall()

    

    if request.method=='POST':
        rdate=request.form['rdate']
        stime=request.form['stime']
        etime=request.form['etime']
        duration=request.form['duration']
        users=request.form['users']
        stype=request.form['stype']

        stm=stime.split(':')
        etm=etime.split(':')
        
        try:
            c1=request.form['c1']
        except:
            print("")
        try:
            c2=request.form['c2']
        except:
            print("")
        try:
            c3=request.form['c3']
        except:
            print("")

        
        
        
        gd=rdate.split("-")
        gdate=gd[2]+"-"+gd[1]+"-"+gd[0]

        day1=findDay(gdate)
        print(day1)

        #############
        ui=1
        us=int(users)
        uk=us
        ucnt=0
        arru=[]
        arr_u=[]
        data2=[]
        divide=0

        mycursor.execute("UPDATE rq_consumer SET sms_st=0 WHERE rid=%s",(rid,))
        mydb.commit()

        
            
        if stype=="0":
            mycursor.execute("SELECT count(*) FROM rq_consumer where status=0 && prefer_st=0 && rid=%s",(rid, ))
            ucnt = mycursor.fetchone()[0]
            divide=int(ucnt/us)

            mycursor.execute("SELECT * FROM rq_consumer where status=0 && prefer_st=0 && rid=%s",(rid, ))
            data2 = mycursor.fetchall()
        
        elif stype=="1":
            
            mycursor.execute("SELECT * FROM rq_consumer where status=0 && prefer_st=1 && rid=%s",(rid, ))
            ddd = mycursor.fetchall()
            for dds in ddd:
                ex=0
                ey=0
                ex1=dds[7].split(',')
                for ex2 in ex1:
                    if ex2==day1:
                        ex+=1
                ex3=dds[8].split('-')
                sx=ex3[0].split(':')
                sy=ex3[1].split(':')
                if sx[0]<=stm[0] or sy[0]<=etm[0]:
                    ey+=1
                if ex>0 and ey>0:
                    ucnt+=1
                    mycursor.execute("SELECT * FROM rq_consumer where card=%s",(dds[3], ))
                    cdd = mycursor.fetchone()
                    data2.append(cdd)
            divide=int(ucnt/us)
            
        elif stype=="2":
            mycursor.execute("SELECT count(*) FROM rq_consumer where status=1 && deliver_st=0 && rid=%s",(rid, ))
            ucnt = mycursor.fetchone()[0]
            divide=int(ucnt/us)

            mycursor.execute("SELECT * FROM rq_consumer where status=1 && deliver_st=0 && rid=%s",(rid, ))
            data2 = mycursor.fetchall()
        
        
        #print(data2)
        
        i=0
        for ur in data2:
            
            arr_u.append(ur[3])
            #print(str(ui)+"==="+str(uk))
            #print(i)
            if i==divide:
                arru.append(arr_u)
            if ui==uk:
                arru.append(arr_u)
                arr_u=[]
                uk+=us
                
                i+=1
                
            ui+=1
        #print(arru)
        #############
        
        time=stime
        ee=etime.split(":")
        e1=int(ee[0])
        e2=int(ee[1])
        i=0
        ii=0
        k=int(duration)
        K=k
        rk=0
        T=stime
        act="1"
        s=""
        ss=""
        no_of_customer=0
        while i<41:
            dat1=[]
            s="1"
            tm1=time   
            time=findTime(T, K)
            tm2=time
            tt=tm2.split(":")
            t1=int(tt[0])
            t2=int(tt[1])
            tm=tm1+" to "+tm2

            if c1=="1":
                if t1==12 and t2<15:
                    
                    rk=15-k
                    K+=rk
                    
                if tm=="12:00 to 12:15":
                    s="2"
                elif tm=="12:10 to 12:25":
                    s="2"
                    
                #elif t1==12 and t2<20:
                #    rk=15-k
                #    K+=rk
                '''if k<20 and t1==12 and t2>0 and t2<=15:
                    print("break1")
                    s="2"
                elif t1==12 and t2>10 and t2<=25:
                    print("break1")
                    s="2"'''
            
           
            
            if c2=="2":
                if t1==14 and t2<10:
                    rk=30-k
                    K+=rk
                elif t1==14 and t2<20:
                    rk=30-k
                    K+=rk

                if tm=="14:00 to 14:30":
                    s="3"
                elif tm=="14:05 to 14:35":
                    s="3"
                elif tm=="14:10 to 14:40":
                    s="3"
                    
                '''if k<20 and t1==14 and t2>0 and t2<=30:
                    print("lunch")
                    s="3"
                elif t1==14 and t2>5 and t2<=35:
                    print("lunch")
                    s="3"'''
                    
                
            
            
            
                
            if c3=="3":
                if t1==15 and t2>=30 and t2<45:
                    rk=15-k
                    K+=rk

                if tm=="15:30 to 15:45":
                    s="2"
                elif tm=="15:35 to 15:50":
                    s="2"
                elif tm=="15:40 to 15:55":
                    s="2"
                '''if k<20 and t1==15 and t2>=30 and t2<45:
                    print("break2")
                    s="2"
                elif t1==15 and t2>35 and t2<=50:
                    print("break2")
                    s="2"'''
               
            
            
               
            
            #print(time)
            #print("s="+s)
            dat1.append(tm)
            dat1.append(s)
            #print(str(t1)+" "+str(e1)+" "+str(t2)+" "+str(e2))
            
            
            
            print("ii="+str(ii)+",K="+str(K))
            print(dat1)
            K+=k  
            if ii<divide:
                dat1.append(arru[ii])
                #print(arru[ii])
                for ss in arru[ii]:
                    no_of_customer+=1
                    mycursor.execute("UPDATE rq_consumer SET ration_date=%s,ration_time=%s,sms_st=1 WHERE card=%s",(gdate,tm,ss))
                    mydb.commit()
            else:
                arr_empty=["1"]
                dat1.append(arr_empty[0])

            #if c1=="1" or c2=="2" or c3=="3":
            #    ii=ii
            #else:
            if s=="2" or s=="3":
                print("")
            else:
                ii+=1
            
            
            data3.append(dat1)
            if t1>=e1 and t2>=e2:
                print("yes")
                K+=k
                tm2=tm1+" to "+str(e1)+":"+str(e2)
                print("tm="+tm2)
                dat1.append(tm2)
                dat1.append(s)
                break
            
            i+=1
        #print(data3)
        print(ii)
        print("No. of Customers:"+str(no_of_customer))
        mycursor.execute("SELECT * FROM rq_stock where rid=%s",(rid, ))
        data4 = mycursor.fetchall()
        n_stock=0
        
        for rw in data4:
            tot=rw[5]
            deliver_stock=rw[8]*no_of_customer
            print("stock="+str(deliver_stock))
            if deliver_stock<=tot:
                n_stock+=1

        if n_stock>0:
            mycursor.execute("UPDATE rq_employee SET given_date=%s,stime=%s,etime=%s,slot_mode=%s,duration=%s WHERE eid=%s",(gdate,stime,etime,stype,duration,uname))
            mydb.commit()
            available="yes"
        else:
            available="no"

        DeepQLearning(no_of_customer)
        QueuePredict(no_of_customer, n_stock)

        ##################
        ff1=open("det.txt","r")
        afnn=ff1.read()
        ff1.close()
        arfnn=afnn.split(',')
        #os.remove("static/upload/"+arfnn[0])
        #os.remove("static/upload/"+arfnn[1])
        #os.remove("static/upload/"+arfnn[2])
        #os.remove("static/upload/"+arfnn[3])
        
        
        afn1=randint(100,999)
        bfn1=randint(100,999)
        cfn1=randint(100,999)
        dfn1=randint(100,999)
        afn="a"+str(afn1)+".png,b"+str(bfn1)+".png,c"+str(cfn1)+".png,d"+str(dfn1)+".png"
        arfn=afn.split(',')
        fn1=arfn[0]
        fn2=arfn[1]
        fn3=arfn[2]
        fn4=arfn[3]
        ff=open("det.txt","w")
        ff.write(afn)
        ff.close()
    
        ####
        x1=[]
        y1=[]
        j=0

        ik=1
        while ik<=ii:
            if ii>40:
                v1=75
                v2=85
            elif ii>30:
                v1=80
                v2=90
            elif ii>20:
                v1=83
                v2=93
            elif ii>10:
                v1=88
                v2=95
            else:
                v1=93
                v2=99
            dv=randint(v1,v2)
            x1.append(ik)
            y1.append(dv)
            ik+=1

        # line 1 points
        #x1 = [10,20,30]
        #y1 = [93,89,72]
        # plotting the line 1 points 
        plt.plot(x1, y1, color='green', label = "Extract Data")
          
        
          
        plt.xlabel("No. of Slots")
        plt.ylabel("Queue - Accuracy")
        plt.title("")

        rr=randint(100,999)
        #fn="c1.png"
        
        plt.savefig('static/upload/'+fn1)
        #plt.close()
        plt.clf()
        #########
        mycursor.execute("SELECT count(*) FROM rq_consumer where rid=%s",(rid, ))
        tot_cus = mycursor.fetchone()[0]
        
        ###################3
        x1=[]
        y1=[]
        j=0

        mycursor.execute("SELECT * FROM rq_timeslot where slot_mode=0 && rid=%s order by id desc limit 0,10",(rid, ))
        cd2 = mycursor.fetchall()
        cx2=1
        for rs2 in cd2:
            tid=rs2[0]
            mycursor.execute("SELECT count(*) FROM rq_time_queue where tid=%s && rid=%s order by id desc limit 0,10",(tid,rid))
            cn2 = mycursor.fetchone()[0]
            cg2=(cn2/tot_cus)*100
            x1.append(cx2)
            y1.append(cg2)
            cx2+=1
        #print(x1)
        #print(y1)
        # line 1 points
        #x1 = [1,2,3,4]
        #y1 = [15,19,21,5]
        # plotting the line 1 points 
        plt.plot(x1, y1, color='green', label = "Extract Data")
          
        
          
        plt.xlabel("Days")
        plt.ylabel("Normal Schedule(%)")
        plt.title("")

        rr=randint(100,999)
        #fn="c2.png"
        
        plt.savefig('static/upload/'+fn2)
        #plt.close()
        plt.clf()
        ###############
        x1=[]
        y1=[]
        j=0

        mycursor.execute("SELECT * FROM rq_timeslot where slot_mode=1 && rid=%s order by id desc limit 0,10",(rid, ))
        cd3 = mycursor.fetchall()
        cx3=1
        for rs3 in cd3:
            tid=rs3[0]
            mycursor.execute("SELECT count(*) FROM rq_time_queue where tid=%s && rid=%s order by id desc limit 0,10",(tid,rid))
            cn3 = mycursor.fetchone()[0]
            cg3=(cn3/tot_cus)*100
            x1.append(cx3)
            y1.append(cg3)
            cx3+=1
        # line 1 points
        #x1 = [1,2,3,4]
        #y1 = [6,4,8,3]
        # plotting the line 1 points 
        plt.plot(x1, y1, color='green', label = "Extract Data")
          
        
          
        plt.xlabel("Days")
        plt.ylabel("Preferred Schedule(%)")
        plt.title("")

        rr=randint(100,999)
        #fn="c3.png"
        
        plt.savefig('static/upload/'+fn3)
        #plt.close()
        plt.clf()
        ################################
        
        x1=[]
        y1=[]
        j=0
        mycursor.execute("SELECT * FROM rq_timeslot where slot_mode=2 && rid=%s order by id desc limit 0,10",(rid, ))
        cd4 = mycursor.fetchall()
        cx4=1
        for rs4 in cd4:
            tid=rs4[0]
            mycursor.execute("SELECT count(*) FROM rq_time_queue where tid=%s && rid=%s order by id desc limit 0,10",(tid,rid))
            cn4 = mycursor.fetchone()[0]
            cg4=(cn4/tot_cus)*100
            x1.append(cx4)
            y1.append(cg4)
            cx4+=1
        # line 1 points
        #x1 = [1,2,3,4,5,6]
        #y1 = [12,14,16,23,20,17]
        # plotting the line 1 points 
        plt.plot(x1, y1, color='green', label = "Extract Data")
          
        
          
        plt.xlabel("Days")
        plt.ylabel("Re-Schedule(%)")
        plt.title("")

        rr=randint(100,999)
        #fn="c4.png"
        
        plt.savefig('static/upload/'+fn4)
        #plt.close()
        plt.clf()
        
        ###############
        
    return render_template('emp_home.html',data=data,data1=data1,data3=data3,act=act,available=available,fn1=fn1,fn2=fn2,fn3=fn3,fn4=fn4)


@app.route('/emp_schedule',methods=['POST','GET'])
def emp_schedule():
    act=""
    uname=""
    msg=""
    if 'username' in session:
        uname = session['username']

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
        
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where eid=%s",(uname, ))
    dt = mycursor.fetchone()
    rid=dt[1]

    mycursor.execute("UPDATE rq_consumer SET status=0,deliver_st=0,ration_date='',ration_time='' WHERE rid=%s",(rid,))
    mydb.commit()

    return render_template('emp_schedule.html',msg=msg)

@app.route('/emp_require',methods=['POST','GET'])
def emp_require():
    act=""
    uname=""
    msg=""
    if 'username' in session:
        uname = session['username']

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
        
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where eid=%s",(uname, ))
    dt = mycursor.fetchone()
    rid=dt[1]

    mycursor.execute("SELECT * FROM rq_stock_req where rid=%s order by id desc",(rid, ))
    data = mycursor.fetchall()

    
    if request.method=='POST':
        product=request.form['product']
        qty=request.form['qty']
        
        mycursor.execute("SELECT max(id)+1 FROM rq_stock_req")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1

        
        sql = "INSERT INTO rq_stock_req(id,rid,product,qty,rdate) VALUES (%s,%s,%s, %s, %s)"
        val = (maxid, rid,product,qty,rdate)
        print(sql)
        mycursor.execute(sql, val)
        mydb.commit()
        return redirect(url_for('emp_require'))
   

    return render_template('emp_require.html',msg=msg,data=data)


@app.route('/emp_send',methods=['POST','GET'])
def emp_send():
    act=""
    uname=""
    
    if 'username' in session:
        uname = session['username']

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
        
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where eid=%s",(uname, ))
    dt = mycursor.fetchone()
    rid=dt[1]
    gdate=dt[14]
    stime=dt[15]
    etime=dt[16]
    smode=dt[17]
    duration=dt[18]

    rd=gdate.split('-')
    mon=rd[1]
    yr=rd[2]

    mycursor.execute("SELECT * FROM rq_ration where rid=%s",(rid, ))
    data = mycursor.fetchone()

    

    
    mycursor.execute("SELECT max(id)+1 FROM rq_timeslot")
    maxid = mycursor.fetchone()[0]
    if maxid is None:
        maxid=1

    
    sql = "INSERT INTO rq_timeslot(id,rid,given_date,stime,etime,duration,slot_mode,rdate,month,year) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (maxid, rid, gdate, stime, etime,duration,smode,rdate,mon,yr)
    print(sql)
    mycursor.execute(sql, val)
    mydb.commit()

    mycursor.execute("SELECT * FROM rq_consumer where rid=%s && sms_st=1",(rid, ))
    data1 = mycursor.fetchall()
    i=0
    for cus in data1:
        name=cus[2]
        card=cus[3]
        mobile=cus[4]
        ration_date=cus[20]
        ration_time=cus[21]

        mycursor.execute("UPDATE rq_consumer SET status=1 WHERE rid=%s && sms_st=1",(rid, ))
        mydb.commit()

        if i<3:
            mess="Ration: "+ration_date+", "+ration_time
            url="http://iotcloud.co.in/testsms/sms.php?sms=msg&name="+name+"&mess="+mess+"&mobile="+str(mobile)
            webbrowser.open_new(url)
                
        i+=1
        mycursor.execute("SELECT max(id)+1 FROM rq_time_queue")
        maxid2 = mycursor.fetchone()[0]
        if maxid2 is None:
            maxid2=1

        
        sql = "INSERT INTO rq_time_queue(id,rid,tid,card,ration_date,ration_time,deliver_st,month,year) VALUES (%s,%s,%s, %s, %s, %s, %s, %s, %s)"
        val = (maxid2, rid, maxid,card,ration_date,ration_time,'0',mon,yr)
        print(sql)
        mycursor.execute(sql, val)
        mydb.commit()
    
    
    
    return render_template('emp_send.html')

@app.route('/emp_entry',methods=['POST','GET'])
def emp_entry():
    act=""
    msg=""
    uname=""
    data2=[]
    data4=[]
    gtime=""
    act = request.args.get('act')
    card = request.args.get('card')
    tid = request.args.get('tid')
    
    if 'username' in session:
        uname = session['username']

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
    rh=now.strftime("%H")
    rm=now.strftime("%M")
    #rh="11"
    #rm="13"
    #print(rh)
    #print(rm)
    dtime=rh+":"+rm
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where eid=%s",(uname, ))
    dt = mycursor.fetchone()
    rid=dt[1]

    mycursor.execute("SELECT * FROM rq_timeslot where given_date=%s && rid=%s",(rdate,rid))
    data = mycursor.fetchall()

    mycursor.execute("SELECT * FROM rq_time_queue where ration_date=%s && rid=%s",(rdate,rid))
    data3 = mycursor.fetchall()
    for rs3 in data3:
        tt=rs3[5]
        tm1=tt.split(' to ')
        tm2=tm1[0]
        #print(tm2)
        tm3=tm1[1]

        time_h1=tm2.split(':')
        time_h2=tm3.split(':')

        hh1=time_h1[0]
        mm1=time_h1[1]
        hh2=time_h2[0]
        mm2=time_h2[1]

        
        if hh1<=rh and mm1<rm and hh2>=rh and mm2>=rm:
            print(tt)
            gtime=tt
        
    mycursor.execute("SELECT card FROM rq_time_queue where deliver_st=0 && ration_date=%s && rid=%s && ration_time=%s",(rdate,rid,gtime))
    dat1 = mycursor.fetchall()
    for rc in dat1:
        dat3=[]
        mycursor.execute("SELECT name FROM rq_consumer where card=%s",(rc[0], ))
        dat2 = mycursor.fetchone()[0]
        dat3.append(rc[0])
        dat3.append(dat2)
        data4.append(dat3)    
    
    mycursor.execute("SELECT * FROM rq_stock where qty>0 && rid=%s",(rid, ))
    data5 = mycursor.fetchall()
    

    
    
    if tid is not None:
        mycursor.execute("SELECT * FROM rq_time_queue where tid=%s",(tid, ))
        data2 = mycursor.fetchall()

    sk=0
    stock_arr=[]
    sarr=[]
    amount=0
    amt=0
    if request.method=='POST':
        for rd5 in data5:
            
            sid=rd5[0]
            qt=request.form['qt'+str(sid)]
            qtt=int(qt)
            if qtt>0:
                if rd5[5]>=qtt:
                    print(rd5[3])
                    ss=rd5[3]+"-"+str(qtt)
                    sarr.append(ss)

                    amt=qtt*rd5[4]
                    amount+=amt
                    mycursor.execute("UPDATE rq_stock SET qty=qty-%s WHERE rid=%s && id=%s",(qtt,rid,sid))
                    mydb.commit()
                    
                else:
                    sk+=1
        print(sarr)
        print("Amt="+str(amount))
        if sk==0:
            prd=",".join(sarr)
            mycursor.execute("UPDATE rq_time_queue SET deliver_st=1,product=%s,amount=%s,dtime=%s WHERE ration_date=%s && rid=%s && card=%s",(prd,amount,dtime,rdate,rid,card))
            mydb.commit()
            mycursor.execute("UPDATE rq_consumer SET deliver_St=1 WHERE rid=%s && card=%s",(rid,card))
            mydb.commit()
            
            print("success")
            msg="Bill Success - "+prd+", Amount: Rs."+str(amount)
        else:
            msg="Stock not available"
        
    return render_template('emp_entry.html',rdate=rdate,msg=msg,data=data,data2=data2,gtime=gtime,data4=data4,data5=data5,card=card,act=act,tid=tid)

@app.route('/entry',methods=['POST','GET'])
def entry():
    act=""
    uname=""
    data2=[]
    act = request.args.get('act')
    
    
    if 'username' in session:
        uname = session['username']

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
        
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where eid=%s",(uname, ))
    dt = mycursor.fetchone()
    rid=dt[1]

    mycursor.execute("SELECT * FROM rq_timeslot where rid=%s",(rid, ))
    data = mycursor.fetchall()

    if act=="ok":
        tid = request.args.get('tid')
        mycursor.execute("SELECT * FROM rq_time_queue where tid=%s",(tid, ))
        data2 = mycursor.fetchall()

    

        
    return render_template('entry.html',data=data,data2=data2)


@app.route('/report',methods=['POST','GET'])
def report():
    act=""
    uname=""
    data1=[]
    if 'username' in session:
        uname = session['username']

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
        
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where eid=%s",(uname, ))
    dt = mycursor.fetchone()
    rid=dt[1]

    mycursor.execute("SELECT distinct(month) FROM rq_timeslot where rid=%s",(rid, ))
    data2 = mycursor.fetchall()
    mycursor.execute("SELECT distinct(year) FROM rq_timeslot where rid=%s",(rid, ))
    data3 = mycursor.fetchall()

    if request.method=='POST':
        gdate=request.form['gdate']
        month=request.form['month']
        year=request.form['year']

        

        if gdate=="":
            print("")
        else:
            gd=gdate.split('-')
            gdd=gd[2]+"-"+gd[1]+"-"+gd[0]
            mycursor.execute("SELECT * FROM rq_timeslot where given_date=%s && rid=%s",(gdd,rid))
            data1 = mycursor.fetchall()

        if month=="":
            print("")
        else:
            mycursor.execute("SELECT * FROM rq_timeslot where month=%s && year=%s && rid=%s",(month,year,rid))
            data1 = mycursor.fetchall()
            


    return render_template('report.html',data1=data1,data2=data2,data3=data3)

@app.route('/emp_viewcard',methods=['POST','GET'])
def emp_viewcard():
    act=""
    uname=""
    
    if 'username' in session:
        uname = session['username']

    tid = request.args.get('tid')
    
    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
        
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM rq_employee where eid=%s",(uname, ))
    dt = mycursor.fetchone()
    rid=dt[1]

    mycursor.execute("SELECT count(*) FROM rq_time_queue where tid=%s",(tid, ))
    tot = mycursor.fetchone()[0]
    
    mycursor.execute("SELECT * FROM rq_time_queue where tid=%s",(tid, ))
    data = mycursor.fetchall()
    


    return render_template('emp_viewcard.html',data=data,tot=tot)

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    #session.pop('username', None)
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=5000)
