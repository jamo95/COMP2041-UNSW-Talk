#!/web/cs2041/bin/python3.6.3

# written by andrewt@cse.unsw.edu.au October 2017
# as a starting point for COMP[29]041 assignment 2
# https://cgi.cse.unsw.edu.au/~cs2041/assignments/UNSWtalk/

import os, re, glob, operator, datetime, sqlite3, smtplib, math
from flask import Flask, render_template, session, request, redirect
from random import randint

static =  "static"
token_dir =  "token"
pass_dir =  "password"
account_dir =  "account"
students_dir = "dataset-medium";

# Function takes in list of user details and removes titles i.e. "email: "
# Returns dict of values with titles removed
# If list is missing details dict value will be set to None

def formatInfo(details):
    formatted_details = {}
    for line in details:
        if re.match("full_name: ", line):
            formatted_details["full_name"] = line.replace("full_name: ", "")
        elif re.match("zid: ", line):
            formatted_details["zid"] = line.replace("zid: ", "")
            if os.path.isfile(os.path.join(static, students_dir,
                formatted_details["zid"], "img.jpg")):
                formatted_details["image"] = os.path.join(static, students_dir,
                    formatted_details["zid"], "img.jpg")
        elif re.match("home_suburb: ", line):
            formatted_details["home_suburb"] = line.replace("home_suburb: ", "")
        elif re.match("email: ", line):
            formatted_details["email"] = line.replace("email: ", "")
        elif re.match("program: ", line):
            formatted_details["program"] = line.replace("program: ", "")
        elif re.match("birthday: ", line):
            formatted_details["birthday"] = line.replace("birthday: ", "")
        elif re.match("password: ", line):
            formatted_details["password"] = line.replace("password: ", "")
        elif re.match("courses: ", line):
            line = line.replace("courses: (", "").replace(")", "")
            formatted_details["courses"] = line.split(", ")
        elif re.match("friends: ", line):
            line = line.replace("friends: (", "").replace(")", "")
            formatted_details["friends"] = line.split(", ")
        elif re.match("home_latitude: ", line):
            formatted_details["home_latitude"] = line.replace("home_latitude: ","")
        elif re.match("home_longitude: ", line):
            formatted_details["home_longitude"] = line.replace("home_longitude: ","")
        elif re.match("profile_text: ", line):
            formatted_details["profile_text"] = line.replace("profile_text: ","")
        if "full_name" not in formatted_details:
            formatted_details["full_name"] = "(Name Missing)"
        if "profile_text" not in formatted_details:
            formatted_details["profile_text"] = None
        if "zid" not in formatted_details:
            formatted_details["zid"] = None
        if "email" not in formatted_details:
            formatted_details["email"] = None
        if "image" not in formatted_details:
            formatted_details["image"] = os.path.join(static,"standard.jpg")
        if "home_suburb" not in formatted_details:
            formatted_details["home_suburb"] = None
        if "program" not in formatted_details:
            formatted_details["program"] = None
        if "birthday" not in formatted_details:
            formatted_details["birthday"] = None
        if "password" not in formatted_details:
            formatted_details["password"] = None
        if "courses" not in formatted_details:
            formatted_details["courses"] = []
        if "friends" not in formatted_details:
            formatted_details["friends"] = []
        if "home_latitude" not in formatted_details:
            formatted_details["home_latitude"] = None
        if "home_longitude" not in formatted_details:
            formatted_details["home_longitude"] = None
    return formatted_details

zids = {} #dictionary of every student zid contain dictionary of their details
names = {} #dictionary of every student name contain dictionary of their details

# the code below creates the two dictionaries above (zid and name)

stu_dir = os.path.join(static, students_dir, "*")
for student in glob.iglob(stu_dir):
    zid = student[22:] 
    details_filename = os.path.join(static, students_dir, zid, "student.txt")
    with open(details_filename) as f:
        all_details = f.read().splitlines()
        zids[zid] = formatInfo(all_details)
        names[zids[zid]["full_name"]] = zids[zid]

# Function to create a Post with the passed in message

def createPost(message):
    count = 0
    post_regex = os.path.join(static, students_dir, session["zid"]) + r"/[0-9]+.txt"
    for curr_file in glob.glob(os.path.join(static, students_dir, session["zid"],
     "*.txt")): # count the number of potential posts in directiry
        if re.match(post_regex, curr_file):
            count += 1
    for x in range(count):
        if not os.path.exists(os.path.join(static, students_dir, session["zid"],
         str(x)+".txt")): # checks for possible deleted post numbers
            count = str(x)
            break
    # the code below creates the post including time, zid and message
    f= open(os.path.join(static, students_dir, session['zid'], str(count)) + ".txt","w+")
    f.write("from: " + session["zid"] + "\n")
    time = str(datetime.datetime.utcnow()).replace(" ", "T").replace(r".", "+")[:-6]+"0000"
    f.write("time: " + time  + "\n")
    f.write("message: " + message + "\n")
    # add the post the database
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO posts (post_id, zid, message, time) VALUES (?,?,?,?)",
            (count,session["zid"],message,time))
        con.commit()
    except:
        con.rollback()
    con.close()
    f.close() 

# Function to create a Post with the passed in message

def createComment(message, order):
    order = order.split("-")
    post_zid = order[0]
    post_id = order[1]
    post_regex = os.path.join(static, students_dir, post_zid, post_id) + r"-[0-9]+"+".txt"
    count = 0
    for curr_file in glob.glob(os.path.join(static, students_dir, post_zid, "*.txt")):
        if re.match(post_regex, curr_file): # count the number of potential comments in directiry
            count += 1
    for x in range(count):
        if not os.path.exists(os.path.join(static, students_dir, post_zid, 
            post_id+"-"+str(x)+".txt")):
            count = str(x)  # checks for possible deleted comments numbers
            break
    # the code below creates the comments including time, zid and message
    f= open(os.path.join(static, students_dir, post_zid, post_id + "-" + 
        str(count)) + ".txt","w+")
    f.write("from: " + session["zid"] + "\n")
    time = str(datetime.datetime.utcnow()).replace(" ", "T").replace(r".", "+")[:-6]+"0000"
    f.write("time: " + time  + "\n")
    f.write("message: " + message + "\n")
    con = sqlite3.connect('database.db') # add to the database
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO comments (comment_id,to_post,post_zid,zid,message,time) VALUES (?,?,?,?,?,?)",
            (count,post_id,post_zid,session["zid"],message,time))
        con.commit()
    except:
        con.rollback()
    con.close()
    f.close() 

# function to create replies

def createReply(message, order):
    order = order.split("-")
    post_zid = order[0]
    post_id = order[1]
    comment_id = order[2]
    post_regex = os.path.join(static, students_dir, post_zid, post_id + "-" + 
        comment_id) + r"-[0-9]+"+".txt"
    count = 0
    for curr_file in glob.glob(os.path.join(static, students_dir, post_zid, "*.txt")):
        if re.match(post_regex, curr_file): #check number of replies in directory
            count += 1
    for x in range(count):
        if not os.path.exists(os.path.join(static, students_dir, post_zid, post_id+"-"+comment_id+"-"+str(x)+".txt")):
            count = str(x) # check for deletion
            break
    # create reply file
    f= open(os.path.join(static, students_dir, post_zid, post_id + "-" + comment_id +"-" + str(count)) + ".txt","w+")
    f.write("from: " + session["zid"] + "\n")
    time = str(datetime.datetime.utcnow()).replace(" ", "T").replace(r".", "+")[:-6]+"0000"
    f.write("time: " + time  + "\n")
    f.write("message: " + message + "\n")
    # add to db
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO replies (reply_id,to_comment,to_post,post_zid,zid,message,time) " + 
            "VALUES (?,?,?,?,?,?,?)",
            (count,comment_id,post_id,post_zid,session["zid"],message,time))
        con.commit()
    except:
        con.rollback()
    con.close()
    f.close() 

# function to delete message
# also deletes all dependent messages i.e. comments and replies on posts
# also updates database

def deleteMessage(order):
    order = order.split("-")
    message_type = order[0]
    post_zid = order[1]
    post_id = order[2]
    if message_type == "post":
        os.remove(os.path.join(static,students_dir,post_zid,post_id+".txt"))
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM posts WHERE zid = ? and post_id = ?",
                [post_zid, post_id])
            con.commit()
        except:
            con.rollback()
        con.close()
        for message_file in glob.glob(os.path.join(static, students_dir, post_zid, 
            post_id+"-"+"*.txt")):
            os.remove(message_file)
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            try:
                cur.execute("DELETE FROM comments, replies WHERE post_zid = ? and to_post = ?",
                    [post_zid, post_id])
                con.commit()
            except:
                con.rollback()
            con.close()
    if message_type == "comment":
        comment_id = order[3]
        os.remove(os.path.join(static,students_dir,post_zid,post_id+"-"+comment_id+".txt"))
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM comments WHERE post_zid = ? and to_post = ? and comment_id = ?",
                [post_zid, post_id, comment_id])
            con.commit()
        except:
            con.rollback()
        con.close()
        for message_file in glob.glob(os.path.join(static, students_dir, post_zid, 
            post_id+"-"+comment_id+"-"+"*.txt")):
            os.remove(message_file)
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            try:
                cur.execute("DELETE FROM replies WHERE post_zid = ? and to_post = ? and to_comment = ?",
                    [post_zid, post_id, comment_id])
                con.commit()
            except:
                con.rollback()
            con.close()
    if message_type == "reply":
        comment_id = order[3]
        reply_id = order[4]
        os.remove(os.path.join(static, students_dir, post_zid, post_id + "-" + 
        comment_id + "-" + reply_id + ".txt"))
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        try:
            cur.execute("DELETE FROM replies WHERE post_zid = ? and to_post = ? and to_comment = ? and reply_id = ?",
                [post_zid, post_id, comment_id, reply_id])
            con.commit()
        except:
            con.rollback()
        con.close()
        f.close() 

# replace zid with full name in html link tag

def replace_zid(match):
    match = match.group()
    name =  "<a href='profile?zid=" + match + "'>" + zids[match]["full_name"] + "</a>"
    return name

# add friend to list of friends in zid dictionary and database

def addFriend(new_friend):
    zids[session["zid"]]["friends"].append(new_friend)
    student_file = os.path.join(static, students_dir, session["zid"], "student.txt")
    f = open(student_file, 'w')
    f.close()
    f= open(student_file,"w+")

    for detail in zids[session["zid"]]:
        if zids[session["zid"]][detail] is None:
            continue
        if detail == "image":
            continue
        elif detail == "friends":
            friends = detail + ": (" + ", ".join(zids[session["zid"]][detail]) + ")\n"
            f.write(friends)
        elif detail == "courses":
            courses = detail + ": (" + ", ".join(zids[session["zid"]][detail]) + ")\n"
            f.write(courses)
        else:
            f.write(detail + ": " + zids[session["zid"]][detail] + "\n")
    f.close()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    try:
        cur.execute("UPDATE students SET friends = ? where zid = ? ", 
            [", ".join(zids[session["zid"]]["friends"]), session["zid"]])
        con.commit()
    except:
        con.rollback()
    con.close()

# delete friend from list of friends in zid dictionary and database

def deleteFriend(friend):
    zids[session["zid"]]["friends"].remove(friend)
    student_file = os.path.join(static, students_dir, session["zid"], "student.txt")
    f = open(student_file, 'w')
    f.close()
    f= open(student_file,"w+")
    for detail in zids[session["zid"]]:
        if zids[session["zid"]][detail] is None:
            continue
        if detail == "image":
            continue
        elif detail == "friends":
            friends = detail + ": (" + ", ".join(zids[session["zid"]][detail]) + ")\n"
            f.write(friends)
        elif detail == "courses":
            courses = detail + ": (" + ", ".join(zids[session["zid"]][detail]) + ")\n"
            f.write(courses)
        else:
            f.write(detail + ": " + zids[session["zid"]][detail] + "\n")
    f.close()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    try:
        cur.execute("UPDATE students SET friends = ? where zid = ? ", 
            [", ".join(zids[session["zid"]]["friends"]), session["zid"]])
        con.commit()
    except:
        con.rollback()
    con.close()

# add summary to dictionary and database

def updateSummary(profile_summary):
    zids[session["zid"]]["profile_text"] = profile_summary
    student_file = os.path.join(static, students_dir, session["zid"], "student.txt")
    f = open(student_file, 'w')
    f.close()
    f= open(student_file,"w+")
    for detail in zids[session["zid"]]:
        if zids[session["zid"]][detail] is None:
            continue
        if detail == "image":
            continue
        elif detail == "friends":
            friends = detail + ": (" + ", ".join(zids[session["zid"]][detail]) + ")\n"
            f.write(friends)
        elif detail == "courses":
            courses = detail + ": (" + ", ".join(zids[session["zid"]][detail]) + ")\n"
            f.write(courses)
        else:
            f.write(detail + ": " + zids[session["zid"]][detail] + "\n")
    f.close()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    try:
        cur.execute("UPDATE students SET profile_text = ? where zid = ? ",
         [", ".join(zids[session["zid"]]["profile_summary"]), session["zid"]])
        con.commit()
    except:
        con.rollback()
    con.close()

# reset password

def resetPass(zid, password):
    zids[zid]["password"] = password
    student_file = os.path.join(static, students_dir, zid, "student.txt")
    f = open(student_file, 'w')
    f.close()
    f= open(student_file,"w+")
    for detail in zids[zid]:
        if zids[zid][detail] is None:
            continue
        if detail == "image":
            continue
        elif detail == "friends":
            friends = detail + ": (" + ", ".join(zids[zid][detail]) + ")\n"
            f.write(friends)
        elif detail == "courses":
            courses = detail + ": (" + ", ".join(zids[zid][detail]) + ")\n"
            f.write(courses)
        else:
            f.write(detail + ": " + str(zids[zid][detail]) + "\n")
    f.close()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    try:
        cur.execute("UPDATE students SET password = ? where zid = ? ", [password, str(zid)])
        con.commit()
    except:
        con.rollback()
    con.close()

#create account

def createAccount(zid, email, password):
    new_student_dir = static+"/"+ students_dir+"/"+ zid
    if not os.path.exists(new_student_dir):
        os.makedirs(new_student_dir)
    new_student_file = static+"/"+students_dir+"/"+zid +"/"+"student.txt"
    f = open(new_student_file, 'w')
    f.write("zid: " + zid + "\n")
    f.write("email: " + email + "\n")
    f.write("password: " + password + "\n")
    f.close()
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    try:
        cur.execute("INSERT INTO students (zid, email, password, full_name) VALUES (?,?,?)", 
            (zid, email, password))
        con.commit()
    except:
        con.rollback()
    con.close()

# send password to email of zid

def recoverPassword(zid):

    file = open(static+"/"+token_dir+"/"+pass_dir+"/"+zid + ".txt","w")
    token = str(randint(100000, 999999))
    file.write(token)
    # python emailing instructions from: http://www.instructables.com/id/Send-Email-Using-Python/
    serv = smtplib.SMTP('smtp.gmail.com' , 587)
    serv.starttls()
    email = zids[zid]["email"]
    message = "Your UNSWtalk password token is " + token  + "\n\n" + "Create new password at: " + request.url_root + 'recover'
    serv.login("UNSWtalk.assignment@gmail.com" , "testabc123")
    serv.sendmail("UNSWtalk.assignment@gmail.com", email , message)
    serv.quit()

# send email with token for account creation

def createAccountEmail(zid, email, password):
    file = open(static+"/"+token_dir+"/"+account_dir+"/"+zid + ".txt","w")
    token = str(randint(100000, 999999))
    file.write(token + "\n")
    file.write(email + "\n")
    file.write(password + "\n")
    # python emailing instructions from: http://www.instructables.com/id/Send-Email-Using-Python/
    serv = smtplib.SMTP('smtp.gmail.com' , 587)
    serv.starttls()
    message = "Your UNSWtalk account token is " + token  + "\n\n" + "Create new account at: " + request.url_root + 'create'
    serv.login("UNSWtalk.assignment@gmail.com" , "testabc123")
    serv.sendmail("UNSWtalk.assignment@gmail.com", email , message)
    serv.quit()

app = Flask(__name__)

# renders login page
 
@app.route('/', methods=['GET','POST'])
@app.route('/login', methods=['GET','POST'])
def login():
    zid = request.form.get('zid', '')
    password = request.form.get('password', '')
    if zid and password and zid in zids and zids[zid]["password"] == password:
        session['logged_in'] = True
        session['zid'] = zid
        session['password'] = password
        return redirect('feed')
    elif request.form.get('recover_password'): # if recover password 
        zid = request.form.get('recover_password')
        recoverPassword(zid)
        return render_template('recover.html')
    elif request.form.get('create_email') and request.form.get('create_email') and request.form.get('create_password'): # create account 
        zid = request.form.get('create_zid')
        email = request.form.get('create_email')
        password = request.form.get('create_password')
        if zid not in zids:
            createAccountEmail(zid, email, password)
            return render_template('create.html')
        return render_template('login.html')
    else:
        return render_template('login.html') # reload login

# account creation page

@app.route('/', methods=['GET','POST'])
@app.route('/create', methods=['GET','POST'])
def create():
    success = False
    token = request.values.get("token")
    zid = request.values.get("zid")

    if token and zid:
        token_file = static+"/"+token_dir+"/"+account_dir+"/"+zid +".txt"
        if os.path.exists(token_file):
            file = open(token_file, "r")
            content = file.read().splitlines()
            real_token = content[0]
            email = content[1]
            password = content[2]
            if real_token == token:
                success = True
                createAccount(zid, email, password)
    if success:
        return render_template('login.html')
    else:
        return render_template('create.html')

# password recovery page

@app.route('/', methods=['GET','POST'])
@app.route('/recover', methods=['GET','POST'])
def recover():
    reset = False
    zid = request.values.get("zid")
    token = request.values.get("token")
    new_pass = request.values.get("new_password")
    if zid and token and new_pass:
        token_file = os.path.join(static, token_dir, pass_dir, zid +".txt")
        if os.path.exists(token_file):
            file = open(token_file, "r")
            real_token = file.read()
            if real_token == token:
                reset = True
                resetPass(zid,new_pass)
    if reset:
        return render_template('login.html')
    else:
        return render_template('recover.html')

@app.route('/', methods=['GET','POST'])
@app.route('/logout', methods=['GET','POST'])
def logout():
    if 'logged_in' not in session:
        return render_template('logout.html')
    elif not session['logged_in']:
        return render_template('logout.html')
    if request.values.get('log_out'): # turn session off when logging out
        session['logged_in'] = False
        session['zid'] = None
        session['password'] = None  
    return render_template('logout.html')

@app.route('/', methods=['GET','POST'])
@app.route('/settings', methods=['GET','POST'])
def settings(page=1):
    paginate = {}
    paginate["page"] = page
    paginate["total_suggestions"] = 0
    paginate["total_pages"] = 1
    if request.args.get("page"):
        paginate["page"] = int(request.args.get("page"))

    if 'logged_in' not in session:
        return render_template('settings.html')
    elif not session['logged_in']:
        return render_template('settings.html')
    zid = session["zid"]
    friends = zids[zid]["friends"]
    if request.values.get('new_friend'): # add new friend
        new_friend = request.values.get('new_friend')
        if new_friend not in friends:
            addFriend(new_friend)
    elif request.values.get('delete_friend'): # delete  friend
        friend_id = request.values.get('delete_friend')
        if friend_id in friends:
            deleteFriend(friend_id)
    elif request.values.get('profile_summary'): # add profile text
        profile_summary = request.values.get('profile_summary')
        updateSummary(profile_summary)

    # suggestion algorithm based on mutual courses and friends
    suggestions = {}
    for zid in zids:
        if not (zid == session["zid"] or zid in zids[session["zid"]]["friends"]): 
            suggestions[zid] = 0
            for course in zids[session["zid"]]["courses"]:
                if course in zids[zid]["courses"]:
                    suggestions[zid] += 1
            for friend in zids[session["zid"]]["friends"]:
                if course in zids[zid]["friends"]:
                    suggestions[zid] += 1
    suggestions = sorted(suggestions.items(), key=lambda x: x[1], reverse=True)

    paginate["total_posts"] = len(suggestions)
    paginate["total_pages"] = math.ceil(float(paginate["total_posts"])/float(5))
    return render_template('settings.html', zids=zids, suggestions=suggestions,
        paginate=paginate)

@app.route('/', methods=['GET','POST'])
@app.route('/feed', methods=['GET','POST'])
@app.route('/feed/<int:page>', methods=['GET','POST'])
def feed(page=1):

    if 'logged_in' not in session:
        return render_template('feed.html')
    elif not session['logged_in']:
        return render_template('feed.html')

    # paginate setup
    paginate = {}
    paginate["page"] = page
    if request.args.get("page"):
        paginate["page"] = int(request.args.get("page"))

    # create and delete messages
    order = ""
    if request.values.get('new_post'):
        message = request.values.get('new_post')
        createPost(message)
    comment_regex = r"z[0-9]{7}"
    if request.values.get('comment_message') and request.values.get('comment_order'):
        message = request.values.get('comment_message')
        order = request.values.get('comment_order')
        createComment(message,order)
    if request.values.get('reply_message') and request.values.get('reply_order'):
        message = request.values.get('reply_message')
        order = request.values.get('reply_order')
        createReply(message,order)
    if request.values.get('delete'):
        order = request.values.get('delete')
        deleteMessage(order)

    # open database
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    friends = zids[session["zid"]]["friends"]
    cur = con.cursor() 
    # query for posts
    cur.execute("select * from posts where zid = ? union " + 
            "select * from posts where zid = ? union " * len(friends) +
            "select * from posts where posts.message like ? union " + 
            "select posts.* from posts inner join comments on posts.zid = comments.post_zid " + 
            "and posts.post_id = comments.to_post where comments.message like ?  and " + 
            "posts.zid = comments.post_zid and posts.post_id = comments.to_post union " +
            "select posts.* from posts inner join comments on posts.zid = comments.post_zid " + 
            "and posts.post_id = comments.to_post inner join replies on posts.zid = replies.post_zid " + 
            "and comments.comment_id = replies.to_comment and posts.post_id = replies.to_post " + 
            "where replies.message like ? and posts.zid = comments.post_zid and " + 
            "posts.post_id = comments.to_post and posts.zid = replies.post_zid and " + 
            "comments.comment_id = replies.to_comment and posts.post_id = replies.to_post order by time desc",
                    [session['zid']] + friends + ["%"+session['zid']+"%"]*3)
    my_posts = {}
    posts = cur.fetchall()
    paginate["total_posts"] = len(posts)
    paginate["total_pages"] = math.ceil(float(paginate["total_posts"])/float(20))
    for post in posts:
        my_posts[post] = {}
        # query for comments
        cur.execute("select * from comments where post_zid = ? and to_post = ? order by time desc",
            [post['zid'], post["post_id"]])
        message = post["message"]
        message = re.sub(r"(z[0-9]{7})",replace_zid,str(message))
        my_posts[post]["message"] = message
        my_posts[post]["comments"] = {}
        comments = cur.fetchall()
        for comment in comments:
            my_posts[post]["comments"][comment] = {}
            message = comment["message"]
            message = re.sub(r"(z[0-9]{7})",replace_zid,str(message))
            my_posts[post]["comments"][comment]["message"] = message
            my_posts[post]["comments"][comment]["replies"] ={}
            # query for replies
            cur.execute("select * from replies where post_zid = ? and to_post = ? and " + 
                "to_comment= ? order by time desc", [post['zid'], post["post_id"], 
                comment["comment_id"]])
            replies = cur.fetchall()
            for reply in replies:
                my_posts[post]["comments"][comment]["replies"][reply] = {}
                message = reply["message"]
                message = re.sub(r"(z[0-9]{7})",replace_zid,str(message))
                my_posts[post]["comments"][comment]["replies"][reply]["message"] = message
    con.close()
    return render_template('feed.html', zids=zids, my_posts=my_posts, paginate=paginate)

# Show unformatted details for student "n"
# Increment n and store it in the session cookie

@app.route('/', methods=['GET','POST'])
@app.route('/profile', methods=['GET','POST'])
def profile(zid=None):
    if 'logged_in' not in session:
        return render_template('profile.html')
    elif not session['logged_in']:
        return render_template('profile.html')

    # iterate through profiles
    n = 0
    if "n" not in session:
        session["n"] = 0
    else :
        session["n"] += 1
        n = session["n"]

    # create and delete messages
    order = ""
    if request.values.get('new_post'):
        message = request.values.get('new_post')
        createPost(message)
    comment_regex = r"z[0-9]{7}"
    if request.values.get('comment_message') and request.values.get('comment_order'):
        message = request.values.get('comment_message')
        order = request.values.get('comment_order')
        createComment(message,order)
    if request.values.get('reply_message') and request.values.get('reply_order'):
        message = request.values.get('reply_message')
        order = request.values.get('reply_order')
        createReply(message,order)
    if request.values.get('delete'):
        order = request.values.get('delete')
        deleteMessage(order)

    # get my details
    students = sorted(os.listdir(os.path.join(static, students_dir)))
    zid = request.args.get('zid')
    if zid:
        student_to_show = zid
    else:
        student_to_show = students[n % len(students)]
    details_filename = os.path.join(static, students_dir, student_to_show, "student.txt")
    with open(details_filename) as f:
      all_details = f.read()
    student_details = formatInfo(all_details.splitlines())

    # get friend details
    friends = {}
    friend_ids = student_details["friends"]
    for friend_id in friend_ids:
        friends[friend_id] = []
        friend_file = os.path.join(static, students_dir, friend_id, "student.txt")
        with open(friend_file) as ff:
            friend_details = ff.read()
        friend_details = friend_details.splitlines()
        name = ""
        for friend_detail in friend_details:
            if re.match("full_name: ", friend_detail):
                name = friend_detail.replace("full_name: ", "")
                print(name)
        friends[friend_id].append(name)
        if os.path.isfile(os.path.join(static, students_dir, friend_id, "img.jpg")):
            img_file = os.path.join(static, students_dir, friend_id, "img.jpg")
            friends[friend_id].append(img_file)
        else:
            friends[friend_id].append(os.path.join(static, "standard.jpg"))

    # get posts
    con = sqlite3.connect("database.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    my_posts = {}
    cur.execute("select * from posts where zid = ? order by time desc",[student_details['zid']])
    posts = cur.fetchall()
    for post in posts:
        my_posts[post] = {}
        # query for comments
        cur.execute("select * from comments where post_zid = ? and to_post = ? order by time desc",
            [post['zid'], post["post_id"]])
        message = post["message"]
        message = re.sub(r"(z[0-9]{7})",replace_zid,str(message))
        my_posts[post]["message"] = message
        my_posts[post]["comments"] = {}
        comments = cur.fetchall()
        for comment in comments:
            my_posts[post]["comments"][comment] = {}
            message = comment["message"]
            message = re.sub(r"(z[0-9]{7})",replace_zid,str(message))
            my_posts[post]["comments"][comment]["message"] = message
            my_posts[post]["comments"][comment]["replies"] ={}
            # query for replies
            cur.execute("select * from replies where post_zid = ? and to_post = ? and " + 
                "to_comment= ? order by time desc", [post['zid'], post["post_id"], 
                comment["comment_id"]])
            replies = cur.fetchall()
            for reply in replies:
                my_posts[post]["comments"][comment]["replies"][reply] = {}
                message = reply["message"]
                message = re.sub(r"(z[0-9]{7})",replace_zid,str(message))
                my_posts[post]["comments"][comment]["replies"][reply]["message"] = message
    con.close()
    return render_template('profile.html', zids=zids, student_details=student_details,
        my_posts=my_posts, friends=friends)

@app.route('/', methods=['GET','POST'])
@app.route('/faq', methods=['GET','POST'])
def faq():
    if 'logged_in' not in session:
        return render_template('faq.html')
    elif not session['logged_in']:
        return render_template('faq.html')
    return render_template('faq.html')

@app.route('/', methods=['GET','POST'])
@app.route('/search', methods=['GET','POST'])
def search(page=1,searched_post=""):

    if 'logged_in' not in session:
        return render_template('search.html')
    elif not session['logged_in']:
        return render_template('search.html')

    searched_post = None
    searched_name = None

    #setup paginate
    paginate = {}
    paginate["page"] = page
    if request.args.get("page"):
        paginate["page"] = int(request.args.get("page"))
    paginate["total_posts"] = 0

    pos_names = []
    pos_posts = {}

    order = ""
    if request.values.get('new_post'):
        message = request.values.get('new_post')
        createPost(message)
    comment_regex = r"z[0-9]{7}"
    if request.values.get('comment_message') and request.values.get('comment_order'):
        message = request.values.get('comment_message')
        order = request.values.get('comment_order')
        createComment(message,order)
    if request.values.get('reply_message') and request.values.get('reply_order'):
        message = request.values.get('reply_message')
        order = request.values.get('reply_order')
        createReply(message,order)
    if request.values.get('delete'):
        order = request.values.get('delete')
        deleteMessage(order)

    #get seached names
    if request.values.get('searched_name') or request.args.get('searched_name'):
        if request.values.get('searched_name'):
            searched_name = request.values.get('searched_name')
        else: 
            searched_name = request.args.get('searched_name')
        for name in names:
            if searched_name in name:
                pos_names.append(names[name])
        paginate["total_posts"] = len(pos_names)

    #get seached posts
    elif request.values.get('searched_post') or request.args.get('searched_post'):
        if request.values.get('searched_post'):
            searched_post = request.values.get('searched_post')
        else: 
            searched_post = request.args.get('searched_post')
        con = sqlite3.connect("database.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        #get posts
        cur.execute("select * from posts where message like ? order by time desc", 
            ["%"+searched_post+"%"])
        posts = cur.fetchall()
        for post in posts:
            pos_posts[post] = {}
            #get comments
            cur.execute("select * from comments where post_zid = ? and to_post = ? order by time desc",
                [post['zid'], post["post_id"]])
            message = post["message"]
            message = re.sub(r"(z[0-9]{7})",replace_zid,str(message))
            pos_posts[post]["message"] = message
            pos_posts[post]["comments"] = {}
            comments = cur.fetchall()
            for comment in comments:
                pos_posts[post]["comments"][comment] = {}
                message = comment["message"]
                message = re.sub(r"(z[0-9]{7})",replace_zid,str(message))
                pos_posts[post]["comments"][comment]["message"] = message
                pos_posts[post]["comments"][comment]["replies"] ={}
                #get replies
                cur.execute("select * from replies where post_zid = ? and to_post = ? " +
                    "and to_comment= ? order by time desc", 
                    [post['zid'], post["post_id"], comment["comment_id"]])
                replies = cur.fetchall()
                for reply in replies:
                    pos_posts[post]["comments"][comment]["replies"][reply] = {}
                    message = reply["message"]
                    message = re.sub(r"(z[0-9]{7})",replace_zid,str(message))
                    pos_posts[post]["comments"][comment]["replies"][reply]["message"] = message
        con.close()
        paginate["total_posts"] = len(pos_posts)
    paginate["total_pages"] = math.ceil(float(paginate["total_posts"])/float(20))
    return render_template('search.html', zids=zids, pos_names=pos_names, 
        pos_posts=pos_posts, paginate=paginate, searched_post=searched_post,
        searched_name=searched_name)

if __name__ == '__main__':
    app.secret_key = os.urandom(12)
    app.run(debug=True, port=9997)