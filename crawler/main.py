# this file is nothing

import datetime
import random
import re
import sqlite3
import time

from robobrowser import RoboBrowser

from pipeline import output

host = 'https://cl.ghuws.men/'
start_url = host + 'thread0806.php?fid=20'

def run():
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
            print('*'*80)
            print(title)
            content = get_content(browser, novel, author)
            output(title, novel_id=novel_id, author=author, novel_type=novel_type, content=content, date=date)
        time.sleep(random.randint(10, 30))
        browser.follow_link(next_page(browser))
        print('novel link', browser.url)

def get_all_novel_links(browser):
    """
    get all novel link
    return links list [link1, link2, link3]
    """
    novels = list()
    pattern = '草榴官方客戶端|來訪者必看的內容|发帖前必读|关于论坛的搜索功能|文学区违规举报专贴'
    for tr in browser.select('tr.tr3.t_one.tac'):
        if re.search(pattern, tr.h3.a.string) is None:
            novels.append(tr)            
    return novels


def next_page(browser):
    """
    get next page url
    return url string
    """
    pages = browser.find(class_='pages')
    for page in pages:
        if page.string == '下一頁':
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
        if label_a.string == '下一頁':
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
    if '今天' in date:
        today = datetime.date.today()
        return str(today)
    if '昨天' in date:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        return str(yesterday)
    return date

def get_type(novel):
    """
    return type string
    """
    novel_type = novel.find(class_='tal').contents[0].strip()
    return novel_type

def get_content(browser, novel, author):
    """
    get novel all content
    return content string
    """
    novel_link = novel.find('td', class_='tal').a
    link = host + novel_link['href']
    time.sleep(random.randint(10, 30))
    # browser.follow_link(novel_link)
    browser.open(link)
    contents = list()
    # look all page in a novel
    while True:
        contents.append(get_cell_content(browser, author))
        if is_end_page(browser):
            break
        time.sleep(random.randint(10, 30))
        browser.follow_link(next_page(browser))
        print('novel more page link', browser.url)
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
    run()
