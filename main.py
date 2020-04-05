import requests
import sqlite3
import re
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
        "cmd": 20,
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

details = dict()
for entry in all_homework:
    while True:
        try:
            print("get detail..." + str(entry['hw_id']))
            r = requests.post("https://qun.qq.com/cgi-bin/homework/hw/get_hw_detail.fcg",
                              data={
                                  "need_fb_detail": 1,
                                  "group_id": group,
                                  "hw_id": entry['hw_id'],
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
            details[entry['hw_id']] = r
            break
        except Exception as e:
            print(e)

print("write to db...")

db = sqlite3.connect("homework.db")
c = db.cursor()
c.execute("""
CREATE TABLE HOMEWORK(
   ID VARCHAR(30) PRIMARY KEY NOT NULL,
   CONTENT VARCHAR NOT NULL,
   DETAIL VARCHAR NOT NULL
);
""")
db.commit()

for entry in all_homework:
    c.execute("""
    INSERT INTO HOMEWORK VALUES (?, ?, ?);
    """, (entry['hw_id'], str(entry), str(details[entry['hw_id']])))

db.commit()

print("start download...")
urls = set()
r = re.compile(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')

for i in r.finditer(str(all_homework)):
    urls.add(i.group())
for i in r.finditer(str(details)):
    urls.add(i.group())

print("total url: " + str(len(urls)))

os.mkdir("downloaded")
url_map = dict()
for i in urls:
    while True:
        try:
            print("downloading... " + i)
            random_id = str(uuid.uuid1())
            r = requests.get(i, verify=False)
            with open("./downloaded/" + random_id, 'wb') as f:
                f.write(r.content)
            url_map[random_id] = i
            break
        except Exception as e:
            print(e)


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
db.close()
