import sqlite3
import json
import csv

observations = []

with open("data.csv", "w", newline='') as f:
    field_names = ['作业ID', '学生用户名', '学生QQ', '是否完成', '提交时间', '是否批改', '批改结果', '批改时间', '批改人QQ']
    writer = csv.DictWriter(f, fieldnames=field_names)
    writer.writeheader()
    db = sqlite3.connect("homework.db")
    c = db.cursor()
    c.execute(r"select name from sqlite_master where type='table' order by name;")
    for i in c.fetchall():
        if i[0][:9] == "HOMEWORK_":
            print(i[0][9:])
            for i2 in c.execute("select * from " + i[0]):

                data = json.loads(i2[2].replace("\'", "\"").replace("None", "null").replace("\\xa0", ""))

                homework_id = i[0][9:]
                stu_name = i2[0]
                stu_uin = data['uin']
                finished = i2[1]
                if finished:
                    commit_time = data['content']['main'][0]['create_ts']
                    if data['content']['comment'] is not None:
                        comment = "1"
                        result = data['content']['comment'][0]['text']['score']
                        comment_time = data['content']['comment'][0]['create_ts']
                        comment_uin = data['content']['comment'][0]['uin']
                    else:
                        comment = "0"
                        result = "-"
                        comment_time = ""
                        comment_uin = "-"
                else:
                    commit_time = "-"
                    comment = "-"
                    result = "-"
                    comment_time = ""
                    comment_uin = "-"

                writer.writerow({'作业ID': homework_id,
                                 '学生用户名': stu_name,
                                 '学生QQ': stu_uin,
                                 '是否完成': finished,
                                 '提交时间': commit_time,
                                 '是否批改': comment,
                                 '批改结果': result,
                                 '批改时间': commit_time,
                                 '批改人QQ': comment_uin})
