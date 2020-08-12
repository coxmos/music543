import os
import time
from datetime import datetime
from email import utils
from urllib import parse
import xml.etree.ElementTree as ET


def get_timestamp(date):
    """
    得到 rfc2822 时间戳
    :param date: 日期 格式：20200222
    :return: 时间戳
    """
    date_time = datetime.strptime(date, '%Y%m%d').replace(hour=18)
    date_tuple = date_time.timetuple()
    date_timestamp = time.mktime(date_tuple)
    res = utils.formatdate(date_timestamp)
    return res


def add_p_label(lines=[]):
    text = ''
    for line in lines:
        text += f'<p>{line}</p>'
    return text


def read_description():
    lines = []
    line = input("請輸入介紹：（默認請回車, q 退出):")
    while line != 'q':
        lines.append(line)
        line = input()
    return add_p_label(lines)


def handle_file(base_path, filename):
    if filename.count('.mp3') != 1 and filename.count('.m4a') != 1:
        print(filename)
        return None
    base_audio_url = 'https://one.xiaoyuu.ga/music543'

    filepath = os.path.join(base_path, filename)

    date = filename.split('-', 1)[0]
    year = date[:4]

    name = filename.split('-', 1)[1].rsplit('.', 1)[0]
    size = os.path.getsize(filepath)
    url = f'{base_audio_url}/{year}/{parse.quote(filename)}'
    guid = 'a' + str(size) + str(date)
    timestamp = get_timestamp(date)
    image = ''
    has_image = input('有單集圖片嗎（no-0，yes-1）：')
    if has_image == '1':
        image = f'https://cdn.jsdelivr.net/gh/coxmos/music543/image/cover/{date}.jpg'
    link = input('請輸入單集網址：（如沒有請按回車）').strip()
    # link = link.replace('medium.com', 'medium.xiaoyuu.ga').replace('honeypie.wordpress.com', 'honeypie.xiaoyuu.ga')
    description = '<![CDATA['
    text = read_description().strip()
    if text != '':
        description += text
    description += f'<p></p><p>馬世芳老師的电台节目「音樂五四三」非官方存档。 </p><p>如有問題或建議，请发邮件至 <a href="mailto:music543@xiaoyuu.ga">music543@xiaoyuu.ga</a>。</p>]]>'

    return {
        'title': name,
        'url': url,
        'length': str(size),
        'season': year,
        'pubDate': timestamp,
        'guid': guid,
        'description': description,
        'image': image,
        'link': link,
    }


def get_item(info):
    """
    添加单集信息
    :param info: 单集信息
    :return: Element
    """
    item = ET.Element('item')
    if info['image'].strip() != '':
        image = ET.SubElement(item, 'itunes:image', {'href': info['image']})
    if info['link'].strip() != '':
        link = ET.SubElement(item, 'link')
        link.text = info['link']

    enclosure = ET.SubElement(item, 'enclosure',
                              {'length': str(info['length']), 'type': 'audio/mpeg', 'url': info['url']})
    title = ET.SubElement(item, 'title')
    title.text = info['title']
    description = ET.SubElement(item, 'description')
    description.text = info['description']
    guid = ET.SubElement(item, 'guid')
    guid.text = info['guid']
    pubDate = ET.SubElement(item, 'pubDate')
    pubDate.text = info['pubDate']
    season = ET.SubElement(item, 'season')
    season.text = str(info['season'])

    return item


def rss_generator(infos):
    rss_file = 'episode.xml'
    root = ET.Element('root')

    for info in infos:
        item = get_item(info)
        root.append(item)
    tree = ET.ElementTree(root)
    tree.write(rss_file, 'UTF-8')


def main():
    base_path = '../../Downloads/music543'
    files = os.listdir(base_path)
    infos = []
    for file in files:
        print(f'\n{file}')
        res = handle_file(base_path, file)
        if res is not None:
            infos.append(res)
        else:
            print(f"Error:{file}")
    rss_generator(infos)


if __name__ == '__main__':
    main()
