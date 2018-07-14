import os
import sqlite3

import robobrowser

FATHER_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
BASE_DIR = os.path.normpath("%s/%s" % (FATHER_DIR, "banzhu_data"))

CREATE_TABLE = '''
    create table if not exists novel (
        id integer primary key autoincrement,
        novel_id text,
        title text,
        author text,
        last_update text,
        content_lenght integer
    )
'''

def read(cursor, param):
    query = 'select content_lenght from novel where novel_id = ?'
    cursor.execute(query, param)
    records = cursor.fetchall()
    return records

def insert(cursor, param):
    query = '''
        insert into novel
        (novel_id, title, author, content_lenght, last_update)
        values
        (?, ?, ?, ?, ?)
    '''
    cursor.execute(query, param)
    

def update(cursor, param):
    query = 'update novel set content_lenght = ? where novel_id = ?'
    cursor.execute(query, param)
    print('have new novel content, update it')

def output(title, novel_id='0_0', author='unkown', last_update='unkown', content='unkown'):
    novel = {
        'title': title,
        'id': novel_id,
        'author': author,
        'last_update': last_update,
        'content': content
    }
    match = to_sql(novel)
    if match:
        to_api(novel)

def write_novel_file(path, novel):
    with open(path, 'w', encoding='utf-8') as f:
        f.writelines([
            "标题：" + novel['title'] + "\n",
            "作者：" + novel['author'] + "\n",
            "日期：" + novel['last_update'] + "\n",
            novel['content'] + "\n"
        ])

def to_sql(novel):
    title = novel['title'].replace("'", "''")
    author = novel['author'].replace("'", "''")
    novel_id = novel['id'].replace("'", "''")
    last_update = novel['last_update'].replace("'", "''")
    content = novel['content'].replace("'", "''")
    path = os.path.join(BASE_DIR, novel['title'] + ".txt")

    conn = sqlite3.connect('banzhu.db')
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE)
    conn.commit()
    
    records = read(cursor, (novel_id,))
    if len(records) != 0:
        if records[0][0] < len(content):
            update(cursor, (len(content), novel_id))
            write_novel_file(path, novel)
            cursor.close()
            conn.commit()
            conn.close
            return True
        else:
            print('the novel', title, 'has load in database')
            cursor.close()
            conn.commit()
            conn.close()
            return False
    
    param = (novel_id, title, author, len(content), last_update)
    insert(cursor, param)
    write_novel_file(path, novel)
    cursor.close()
    conn.commit()
    conn.close
    return True



def to_api(novel):
    browser = robobrowser.RoboBrowser(history=True, parser="html.parser", timeout=60, tries=5)
    url = 'http://apanr.net/'
    # open anyview a panel
    browser.open(url)
    # login form
    login_form = browser.get_form(id='log-in')
    login_form['account'].value = 'yanghe2008'
    login_form['password'].value = '8443658y'
    browser.submit_form(login_form)
    # access account
    open_account = browser.find(href='/account')
    try:
        browser.follow_link(open_account)
    except:
        print('open anyview website is failed')
        return
    # upload form
    upload_form = browser.get_form()
    # add upload action field
    upload_action_str = '\<input type="hidden" name="action" value="upload_file_post" \/\>'
    upload_action = robobrowser.forms.fields.Input(upload_action_str)
    upload_form.add_field(upload_action)
    # add upload file field
    # path = BASE_DIR + title + ".txt"
    path = os.path.join(BASE_DIR, novel['title'] + ".txt")
    with open(path, 'r', encoding='utf-8') as f:
        upload_form['file_to_upload'].value = f
        browser.submit_form(upload_form)