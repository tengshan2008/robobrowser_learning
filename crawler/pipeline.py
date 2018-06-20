import os
import sqlite3

import robobrowser

FATHER_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BASE_DIR = os.path.normpath("%s/%s" % (FATHER_DIR, "data"))

def output(title, novel_id=0, author="unkown", novel_type="unkown", content="unkown", date="unkown"):
    match = to_sql(title, novel_id, author, novel_type, content, date)
    if match:
        try:
            to_api(title, novel_id, author, novel_type, content, date)
        except Exception as e:
            print(e)
            print("novel title", title, "id", novel_id, " not upload")
        else:
            print("novel", title, "has upload")

def to_sql(title, novel_id, author, novel_type, content, date):
    title = title.replace("'", "''")
    author = author.replace("'", "''")
    novel_type = novel_type.replace("'", "''")
    content = content.replace("'", "''")
    date = date.replace("'", "''")

    conn = sqlite3.connect('novel.db')

    cursor = conn.cursor()

    cursor.execute(
        '''
        create table if not exists novel (
            id integer primary key autoincrement,
            novel_id int,
            title text,
            author text,
            type text,
            content text,
            date text
        )
        '''
    )

    query = '''
        select content from novel where novel_id = ?
    '''
    param = (novel_id,)
    cursor.execute(query, param)
    if len(cursor.fetchall()) != 0:
        if cursor.fetchone() is None:
            query = '''
                update novel
                set content = ?
                where novel_id = ?
            '''
            param = (content, novel_id)
            cursor.execute(query, param)
            print('novel content in database is None, update it')
        elif len(cursor.fetchone()[0]) < len(content):
            query = '''
                update novel
                set content = ?
                where novel_id = ?
            '''
            param = (content, novel_id)
            cursor.execute(query, param)
            print('have new novel content, update it')
        else:
            print('the novel', title, 'has load in database')
            cursor.close()
            conn.commit()
            conn.close()
            return False

    query = '''
        insert into novel
        (novel_id, title, author, type, content, date)
        values
        (?, ?, ?, ?, ?, ?)
    '''
    param = (novel_id, title, author, novel_type, content, date)

    cursor.execute(query, param)
    cursor.close()
    conn.commit()
    conn.close()
    return True

def to_api(title, novel_id, author, novel_type, content, date):
    browser = robobrowser.RoboBrowser(history=True)
    url = 'http://apanr.net/'
    # open anyview a panel
    browser.open(url)
    # login form
    login_form = browser.get_form(id='log-in')
    login_form['account'].value = 'tengshan2008'
    login_form['password'].value = '8443658y'
    browser.submit_form(login_form)
    # access account
    open_account = browser.find(href='/account')
    browser.follow_link(open_account)
    # upload form
    upload_form = browser.get_form()
    # add upload action field
    upload_action_str = '\<input type="hidden" name="action" value="upload_file_post" \/\>'
    upload_action = robobrowser.forms.fields.Input(upload_action_str)
    upload_form.add_field(upload_action)
    # add upload file field
    # path = BASE_DIR + title + ".txt"
    path = os.path.join(BASE_DIR, title + ".txt")
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines([
            "标题：" + title + "\n",
            "作者：" + author + "\n",
            "类型：" + novel_type + "\n",
            "日期：" + date + "\n",
            content + "\n"
        ])
    with open(path, 'r', encoding='utf-8') as f:
        upload_form['file_to_upload'].value = f
        browser.submit_form(upload_form)


if __name__ == "__main__":
    novel_id = 3183073
    title = "测试3"
    author = "傻瓜"
    content = "一个晴朗的早晨，主人公死了。"
    date = "2018-01-02 15:16:22"
    output(title, author=author, novel_id=novel_id, content=content, date=date)
    print(BASE_DIR)
    print(os.path.join(BASE_DIR, title + ".txt"))
