import requests
import sqlite3
import re
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import wait as pool_wait
import uuid
import os


group = input("Group: ")
cookie = input("Cookie: ")
bkn = input("bkn: ")


all_homework = []

for i in range(1, 9999):
    print("get homework list... page " + str(i))
    r = requests.post("https://qun.qq.com/cgi-bin/homework/hw/get_hw_list.fcg", data={
        "num": i,
        "group_id": group,
        "cmd": 21,
        "page_size": 20,
        "client_type": 1,
        "bkn": bkn
    }, headers={
        "Referer": "https://qun.qq.com/homework/p/features/index.html",
        "Origin": "https://qun.qq.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) QQ/9.2.3.26683 Chrome/43.0.2357.134 Safari/537.36 QBCore/3.43.1297.400 QQBrowser/9.0.2524.400",
        "Cookie": cookie
    }, verify=False)
    r = r.json()
    print(r)
    for entry in r['data']['homework']:
        all_homework.append(entry)
    if r['data']['end_flag'] == 1:
        break

print("total: " + str(len(all_homework)))
print(all_homework)

# get all students' homework status
details_notyet = dict()
details_finish = dict()

for entry in all_homework:
    while True:
        try:
            print("get detail..." + str(entry['hw_id']))
            r = requests.post("https://qun.qq.com/cgi-bin/homework/fb/get_hw_feedback.fcg",
                              data={
                                  "group_id": group,
                                  "hw_id": entry['hw_id'],
                                  "status": "[0,1]",
                                  "page": 1,
                                  "page_size": 2000,
                                  "need_userinfo": 1,
                                  "type": "notyet",
                                  "client_type": 1,
                                  "bkn": bkn
                              },
                              headers={
                                  "Referer": "https://qun.qq.com/homework/p/features/index.html",
                                  "Origin": "https://qun.qq.com",
                                  "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) QQ/9.2.3.26683 Chrome/43.0.2357.134 Safari/537.36 QBCore/3.43.1297.400 QQBrowser/9.0.2524.400",
                                  "Cookie": cookie
                              }, verify=False)
            r = r.json()
            print(r)
            details_notyet[entry['hw_id']] = r

            r = requests.post("https://qun.qq.com/cgi-bin/homework/fb/get_hw_feedback.fcg",
                              data={
                                  "group_id": group,
                                  "hw_id": entry['hw_id'],
                                  "status": "[2,3]",
                                  "page": 1,
                                  "page_size": 2000,
                                  "need_userinfo": 1,
                                  "type": "finish",
                                  "client_type": 1,
                                  "bkn": bkn
                              },
                              headers={
                                  "Referer": "https://qun.qq.com/homework/p/features/index.html",
                                  "Origin": "https://qun.qq.com",
                                  "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) QQ/9.2.3.26683 Chrome/43.0.2357.134 Safari/537.36 QBCore/3.43.1297.400 QQBrowser/9.0.2524.400",
                                  "Cookie": cookie
                              }, verify=False)
            r = r.json()
            print(r)
            details_finish[entry['hw_id']] = r
            break
        except Exception as e:
            print(e)

# write to db
print("write to db...")

db = sqlite3.connect("homework.db")
c = db.cursor()

for homework_id in details_notyet:
    c.execute("""
    CREATE TABLE HOMEWORK_""" + str(homework_id) + """(
       NAME VARCHAR(30) PRIMARY KEY NOT NULL,
       FINISHED INTEGER,
       CONTENT VARCHAR NOT NULL
    );
    """)
    db.commit()

for homework_id in details_notyet:
    try:
        for stu in details_notyet[homework_id]['data']['feedback']:
            c.execute("""
            INSERT INTO HOMEWORK_""" + str(homework_id) + """ VALUES (?, 0, ?);
            """, (stu['nick'], str(stu)))
        db.commit()
    except Exception as e:
        print("no notyet " + str(e))

    try:
        for stu in details_finish[homework_id]['data']['feedback']:
            c.execute("""
            INSERT INTO HOMEWORK_""" + str(homework_id) + """ VALUES (?, 1, ?);
            """, (stu['nick'], str(stu)))
        db.commit()
    except Exception as e:
        print("no finish " + str(e))


# find urls
all_urls = set()
regex = re.compile(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
for i in details_notyet:

    for i2 in regex.finditer(str(details_notyet[i])):
        all_urls.add(i2.group())
    for i2 in regex.finditer(str(details_finish[i])):
        all_urls.add(i2.group())

print("total urls: " + str(len(all_urls)))

# start download
os.mkdir("downloaded")
url_map = dict()
pool = ThreadPoolExecutor(max_workers=20)


def download_and_save(filename, target_url):
    while True:
        try:
            print("downloading... " + target_url)
            r1 = requests.get(target_url, verify=False, timeout=20)
            with open("./downloaded/" + filename, 'wb') as f:
                f.write(r1.content)
            break
        except Exception as e:
            print(e)


all_tasks = []
for i in all_urls:
    random_name = str(uuid.uuid4())
    url_map[random_name] = i
    all_tasks.append(pool.submit(download_and_save, random_name, i))


c.execute("""
CREATE TABLE DOWNLOADED(
   URL VARCHAR PRIMARY KEY NOT NULL,
   CONTENT_UUID VARCHAR NOT NULL
);
""")
db.commit()

for i in url_map:
    c.execute("""
    INSERT INTO DOWNLOADED VALUES (?, ?);
    """, (url_map[i], i))
db.commit()
print("db write done.")
db.close()


pool_wait(all_tasks)
print("done.")

