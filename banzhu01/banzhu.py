import logging
import os
import random
import time

import robobrowser

from pipeline import output

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

handler = logging.FileHandler('banzhu.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
IDS_PATH = os.path.join(BASE_DIR, 'ids.txt')

HOST = 'https://www.01banzhu.org'

def run():
    browser = robobrowser.RoboBrowser(timeout=60, tries=5, history=True, parser="html.parser")
    ids = list()
    with open(IDS_PATH, 'r') as f:
        ids = f.readlines()
    for novel_id in ids[240:]:
        novel_link = HOST + novel_id
        logger.info('link ' + novel_link)
        wait()
        try:
            browser.open(novel_link.strip())
        except:
            logger.info('fail novel link' + novel_link)
            continue
        else:
            get_novel(browser, novel_id)


def get_novel(browser, novel_id):
    info = browser.find(id='info')
    title, author, last_update = get_novel_detail(info)
    chapter_list = browser.find(id='list').find_all('a')
    content = get_content(chapter_list)
    output(title, novel_id, author, last_update, content)
    
def get_novel_detail(info):
    title = info.find('h1').string
    author = info.find_all('p')[0].string
    last_update = info.find_all('p')[2].string
    return title, author, last_update

def get_content(chapter_list):
    browser = robobrowser.RoboBrowser(timeout=60, tries=5, history=True, parser="html.parser")
    content = list()
    for chapter in chapter_list:
        chapter_name = 'chapter: ' + chapter.string
        content.append(chapter_name)
        chapter_link = HOST + chapter['href']
        logger.info('link ' + chapter_link)
        wait()
        try:
            browser.open(chapter_link)
        except:
            logger.info('fail chapter link')
            continue
        else:
            chapter_content = get_chapter_content(browser)
        content += chapter_content
    return '\n'.join(content)

def get_chapter_content(browser):
    return [line.strip('\n') for line in browser.find(id='content').strings]

def wait():
    seconds = random.randint(5, 10)
    time.sleep(seconds)

if __name__ == "__main__":
    run()
