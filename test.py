#!/web/cs2041/bin/python3.6.3
# import sqlite3, re, os, glob, smtplib
# from email.mime.text import MIMEText
# static =  "static"
# students_dir = "dataset-medium";
# count = 0
# post_regex = os.path.join(static, students_dir, "z5190009") + r"/[0-9]+.txt"
# for f in glob.glob(os.path.join(static, students_dir, "z5190009", "*.txt")):
# 	if re.match(post_regex, f):
# 		count += 1
# 		print(f)
# post_id = str(len(glob.glob(os.path.join(static, students_dir, "z5190009", "[0-9]+.txt"))))

# print("length is " + str(count))


import smtplib 
gmailaddress = "UNSWtalk.assignment@gmail.com"
gmailpassword = "testabc123"
mailto = "jamison.tsai@gmail.com"
msg = "test again"
mailServer = smtplib.SMTP('smtp.gmail.com' , 587)
mailServer.starttls()
mailServer.login(gmailaddress , gmailpassword)
mailServer.sendmail(gmailaddress, mailto , msg)
print(" \n Sent!")
mailServer.quit()