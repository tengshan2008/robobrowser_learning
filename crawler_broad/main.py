import datetime
import random
import re
import time

import records
import requests
from robobrowser import RoboBrowser

from pipeline import to_api, to_sql, update_content

NEXT_PAGE = '下一頁'
TODAY = '今天'
YESTERDAY = '昨天'
PATTERN = '草榴官方客戶端|來訪者必看的內容|发帖前必读|关于论坛的搜索功能|文学区违规举报专贴'
R_START = 5
R_END = 10

host = 'https://cl.cbcb.us/'
start_url = host + 'thread0806.php?fid=20'

def is_end_page(browser):
    """
    lookup the end page
    return bool
    """
    # print(browser.url)
    # print(browser.find(class_='pages'))
    if browser.find(class_='pages') is None:
        return True
    for label_a in browser.find_all('a'):
        if label_a.string == NEXT_PAGE:
            if label_a.get('href') == 'javascript:#':
                return True
    return False

def next_page(browser):
    """
    get next page url
    return url string
    """
    pages = browser.find(class_='pages')
    for page in pages:
        if page.string == NEXT_PAGE:
            return page
    return None

def get_all_novels(url):
    """
    get all novel link
    return links list [link1, link2, link3]
    """
    novels = list()
    browser = RoboBrowser(history=True)
    browser.open(url)
    while not is_end_page(browser):
        print(browser.url)
        for tr in browser.select('tr.tr3.t_one.tac'):
            if re.search(PATTERN, tr.h3.a.string) is None:
                novels.append(tr)
        time.sleep(5)
        browser.follow_link(next_page(browser))
    return novels

def get_id(novel):
    """
    return novel's id for drop duplicates
    """
    href = novel.find('td', class_='tal').a['href']
    novel_id = href.split('/')[-1].split('.')[0]
    return novel_id

def get_title(novel):
    """
    return novel's title
    """
    title = novel.find('td', class_='tal').a.string
    return title

def get_author(novel):
    """
    return novel's author
    """
    author = novel.find('a', class_='bl').string
    return author

def get_date(novel):
    """
    return novel's date
    """
    date = novel.find('div', class_='f12').string
    if TODAY in date:
        today = datetime.date.today()
        return str(today)
    if YESTERDAY in date:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        return str(yesterday)
    return date

def get_type(novel):
    """
    return type string
    """
    novel_type = novel.find(class_='tal').contents[0].strip()
    return novel_type

def get_link(novel):
    novel_link = novel.find('td', class_='tal').a
    link = host + novel_link['href']
    return link

def get_content(link, author):
    """
    get novel all content
    return content string
    """
    browser = RoboBrowser(parser="html.parser", history=True, timeout=30, tries=5)
    time.sleep(random.randint(R_START, R_END))
    try:
        browser.open(link)
    except:
        print('link failed', link)
        return ''
    else:
        print('novel link', browser.url)
    contents = list()
    # look all page in a novel
    while True:
        content = get_cell_content(browser, author)
        contents.append(content)
        if is_end_page(browser):
            break
        time.sleep(random.randint(R_START, R_END))
        next_page_link = next_page(browser)
        try:
            browser.follow_link(next_page_link)
        except:
            print('link failed', next_page_link)
            break
        else:
            print('page link', browser.url)
    return "\n".join(contents)


def get_cell_content(browser, author):
    """
    get novel cells
    return [cell, cell, cell]
    """
    content = list()
    try:
        cells = browser.find_all(class_='t t2')
    except:
        return "[block]\n"
    for cell in cells:
        if cell.find(class_='r_two').b.string != author:
            continue
        for cell_content in cell.find(class_=['tpc_content do_not_catch', 'tpc_content']).strings:
            content.append(cell_content.strip())
    return "\n".join(content)


def run(url):
    novels = get_all_novels(url)
    i = 0
    for novel in novels:
        i = i + 1
        print('have finished ', i)
        to_sql(
            title = get_title(novel),
            novel_id = get_id(novel),
            author = get_author(novel),
            novel_type = get_type(novel),
            novel_link = get_link(novel),
            content = '',
            date = get_date(novel)
        )

def write_to_content():
    db = records.Database('sqlite:///novel_read.db')
    rows = list(db.query('select * from novel'))
    i = 1763
    for row in rows[1763:]:
        print(i)
        print(row['title'])
        if len(row['link']) != 0 and len(row['author']) != 0:
            content = get_content(row['link'], row['author'])
            if len(content) > len(row['content']):
                update_content(row['id'], content)
        i = i + 1
    

def write_to_api():
    db = records.Database('sqlite:///novel.db')
    rows = db.query('select * from novel')
    for i, row in enumerate(rows):
        print(i)
        if len(row['content']) > 0:
            time.sleep(5)
            to_api(
                title=row['title'],
                novel_id=row['novel_id'],
                author=row['author'],
                novel_type=row['type'],
                novel_link=row['link'],
                content=row['content'],
                date=row['date']
            )


if __name__ == "__main__":
    # run(start_url)
    write_to_content()
    # write_to_api()
