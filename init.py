#!/web/cs2041/bin/python3.6.3
import sqlite3, re, os, glob

static =  "static"
students_dir = "dataset-medium";


# Function takes in list of user details and removes titles i.e. "email: "
#missing values set to none

def formatInfo(details):
    formatted_details = {}
    for line in details:
        if re.match("full_name: ", line):
            formatted_details["full_name"] = line.replace("full_name: ", "")
        elif re.match("zid: ", line):
            formatted_details["zid"] = line.replace("zid: ", "")
            if os.path.isfile(os.path.join(static, students_dir, formatted_details["zid"], 
                "img.jpg")):
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
            formatted_details["courses"] = line.replace("courses: ", "")
        elif re.match("friends: ", line):
            formatted_details["friends"] = line.replace("friends: (", "").replace(")", "")
        elif re.match("home_latitude: ", line):
            formatted_details["home_latitude"] = line.replace("home_latitude: ", "")
        elif re.match("home_longitude: ", line):
            formatted_details["home_longitude"] = line.replace("home_longitude: ", "")
        elif re.match("profile_text: ", line):
            formatted_details["profile_text"] = line.replace("profile_text: ", "")

        if "full_name" not in formatted_details:
            formatted_details["full_name"] = None
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
            formatted_details["courses"] = None
        if "friends" not in formatted_details:
            formatted_details["friends"] = None
        if "home_latitude" not in formatted_details:
            formatted_details["home_latitude"] = None
        if "home_longitude" not in formatted_details:
            formatted_details["home_longitude"] = None
    return formatted_details

#format message details
#missing values set to none

def formatMessage(details):
    formatted_details = {}
    for line in details:
        if re.match("from: ", line):
            formatted_details["zid"] = line.replace("from: ", "")
        elif re.match("time: ", line):
            formatted_details["time"] = line.replace("time: ", "")
        elif re.match("message: ", line):
            formatted_details["message"] = line.replace("message: ", "")
        if "zid" not in formatted_details:
            formatted_details["zid"] = None
        if "time" not in formatted_details:
            formatted_details["time"] = None
        if "message" not in formatted_details:
            formatted_details["message"] = None
    return formatted_details

# get all message from zid and insert into database

def getMessages(zid):
    for message_file in sorted(glob.glob(os.path.join(static, students_dir, zid, "*.txt"))):
        if message_file == os.path.join(static, students_dir, zid, "student.txt"):
            continue
        with open(message_file) as f:
            message = f.read().splitlines()
            message = formatMessage(message)
            post_regex = os.path.join(static, students_dir, zid) + r"/[0-9]+.txt"
            comment_regex = os.path.join(static, students_dir, zid) + r"/[0-9]+\-[0-9]+.txt"
            reply_regex = os.path.join(static, students_dir, zid) + r"/[0-9]+\-[0-9]+\-[0-9]+.txt"
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            try:
                if re.match(post_regex, message_file):
                    post_code = message_file[31:].replace(".txt", "")
                    cur.execute("INSERT INTO posts (post_id, zid, message, time) VALUES (?,?,?,?)",
                        (post_code, message["zid"],message["message"],message["time"]))
                    con.commit()
                elif re.match(comment_regex, message_file):
                    comment_code = message_file[31:].replace(".txt", "")
                    comment_code = comment_code.split("-")
                    cur.execute("INSERT INTO comments (comment_id, to_post, post_zid, zid, message, time) " + 
                        "VALUES (?,?,?,?,?,?)",
                        (comment_code[1],comment_code[0],zid,message["zid"],message["message"],message["time"]))
                    con.commit()
                elif re.match(reply_regex, message_file):
                    reply_code = message_file[31:].replace(".txt", "")
                    reply_code = reply_code.split("-")
                    cur.execute("INSERT INTO replies (reply_id, to_comment, to_post, post_zid, zid, message, " + 
                        "time) VALUES (?,?,?,?,?,?,?)", (reply_code[2], reply_code[1], reply_code[0],zid,
                        message["zid"],message["message"],message["time"]))
                    con.commit()
            except:
                con.rollback()
            con.close()

# from tutorialspoint
# setup database
con = sqlite3.connect('database.db')
print("Opened database successfully")
if con.execute('drop table if exists students'):
    print("Student table deleted successfully")
if con.execute('drop table if exists posts'):
    print("Post table deleted successfully")
if con.execute('drop table if exists comments'):
    print("Comment table deleted successfully")
if con.execute('drop table if exists replies'):
    print("Reply table deleted successfully")
if con.execute("CREATE TABLE IF NOT EXISTS students (zid TEXT PRIMARY KEY, full_name TEXT, " + 
    "profile TEXT, email TEXT, image TEXT, home_suburb TEXT, program TEXT, birthday TEXT, " + 
    "password TEXT, courses TEXT, friends TEXT, home_longitude TEXT, home_latitude TEXT)"):
    print("Student table created successfully")
if con.execute("CREATE TABLE IF NOT EXISTS posts (post_id TEXT, zid TEXT, message TEXT, " + 
    "time TEXT, FOREIGN KEY (zid) REFERENCES students (zid))"):
    print("Post table created successfully")
if con.execute("CREATE TABLE IF NOT EXISTS comments (comment_id TEXT, to_post TEXT, post_zid " + 
    "TEXT, zid TEXT, message TEXT, time TEXT, FOREIGN KEY (to_post) REFERENCES posts (post_id))"):
    print("Comment table created successfully")
if con.execute("CREATE TABLE IF NOT EXISTS replies (reply_id TEXT, to_comment TEXT, " + 
    "to_post TEXT, post_zid TEXT, zid TEXT, message TEXT, time TEXT, FOREIGN KEY (to_comment) " +
    "REFERENCES comments (comment_id))"):
    print("Reply table created successfully")
con.close()

zids = {}
names = {} 

# insert data into database

stu_dir = os.path.join(static, students_dir, "*")
for student in glob.iglob(stu_dir):
    zid = student[22:] 
    details_filename = os.path.join(static, students_dir, zid, "student.txt")
    with open(details_filename) as f:
        all_details = f.read().splitlines()
        zids[zid] = formatInfo(all_details)
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        try:
            cur.execute("INSERT INTO students (zid, full_name, profile_text, email, image, " + 
                "home_suburb, program, birthday, password, courses, friends, home_longitude, home_latitude) " + 
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (zid,zids[zid]["full_name"],zids[zid]["profile_text"],zids[zid]["email"],
                zids[zid]["image"],zids[zid]["home_suburb"],zids[zid]["program"],
                zids[zid]["birthday"],zids[zid]["password"],zids[zid]["courses"],
                zids[zid]["friends"],zids[zid]["home_longitude"],zids[zid]["home_latitude"]) )
            con.commit()
        except:
            con.rollback()
        con.close()
        names[zids[zid]["full_name"]] = zids[zid]
    getMessages(zid)