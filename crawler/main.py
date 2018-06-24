# this file is nothing

import datetime
import random
import re
import sqlite3
import time
import requests

from robobrowser import RoboBrowser

from pipeline import output

# const
NEXT_PAGE = '下一頁'
TODAY = '今天'
YESTERDAY = '昨天'
PATTERN = '草榴官方客戶端|來訪者必看的內容|发帖前必读|关于论坛的搜索功能|文学区违规举报专贴'
R_START = 5
R_END = 10

host = 'https://cl.cbcb.us/'
start_url = host + 'thread0806.php?fid=20&search=&page=10'

def run(start_url):
    """
    start crawler
    """
    # first open novel url with normal browser
    browser = RoboBrowser(history=True)
    browser.open(start_url)
    # look all page in novels
    while not is_end_page(browser):
        novels = get_all_novel_links(browser)
        # process each novel
        for novel in novels:
            novel_id = get_id(novel)
            title = get_title(novel)
            author = get_author(novel)
            date = get_date(novel)
            novel_type = get_type(novel)
            print('*'*75)
            print(title)
            content = get_content(novel, author)
            output(title, novel_id=novel_id, author=author, novel_type=novel_type, content=content, date=date)
        time.sleep(random.randint(R_START, R_END))
        next_page_link = next_page(browser)
        try:
            browser.follow_link(next_page_link)
        except requests.exceptions.ReadTimeout:
            print(next_page_link, "failed")
            print('try again in 60s later')
            time.sleep(60)
            link = host + next_page_link['href']
            run(link)
        else:
            print("novels page link", next_page_link)

def get_all_novel_links(browser):
    """
    get all novel link
    return links list [link1, link2, link3]
    """
    novels = list()
    for tr in browser.select('tr.tr3.t_one.tac'):
        if re.search(PATTERN, tr.h3.a.string) is None:
            novels.append(tr)            
    return novels


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

def get_content(novel, author):
    """
    get novel all content
    return content string
    """
    browser = RoboBrowser(history=True)
    novel_link = novel.find('td', class_='tal').a
    link = host + novel_link['href']
    time.sleep(random.randint(R_START, R_END))
    # browser.follow_link(novel_link)
    try:
        browser.open(link)
    except requests.exceptions.ConnectionError:
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
        except requests.exceptions.ConnectionError:
            print('link failed', browser.url)
            continue
        else:
            print('page link', browser.url)
    return "\n".join(contents)


def get_cell_content(browser, author):
    """
    get novel cells
    return [cell, cell, cell]
    """
    content = list()
    cells = browser.find_all(class_='t t2')
    for cell in cells:
        if cell.find(class_='r_two').b.string != author:
            continue
        for cell_content in cell.find(class_=['tpc_content do_not_catch', 'tpc_content']).strings:
            content.append(cell_content.strip())
    return "\n".join(content)

if __name__ == "__main__":
    run(start_url)
