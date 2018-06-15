# this file is nothing

import datetime
import sqlite3
import time
import random

from robobrowser import RoboBrowser

from pipeline import output

start_url = 'https://cl.ghuws.men/thread0806.php?fid=20'

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
            content = get_content(browser, novel, author)
            print('*'*50)
            print(title)
            output(title, novel_id=novel_id, author=author, novel_type=novel_type, content=content, date=date)
            # output(novel_id, title, author, date, novel_type, content)
        time.sleep(random.randint(10, 30))
        browser.follow_link(next_page(browser))
        print('novel link', browser.url)

def get_all_novel_links(browser):
    """
    get all novel link
    return links list [link1, link2, link3]
    """
    novels = list()
    for tr in browser.select('tr.tr3.t_one.tac'):
        if tr.h3.a.string in ['草榴官方客戶端 & 大陸入口 & 永久域名 ** 必須加入收藏夾 9.13更新',
                                  '■■■ 來訪者必看的內容 - 使你更快速上手  ■■■',
                                  '发帖前必读',
                                  '关于论坛的搜索功能',
                                  '文学区违规举报专贴-----置頂版規有新更新（藍色）']:
            continue
        else:
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
    link = 'https://cl.ghuws.men/' + novel_link['href']
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
