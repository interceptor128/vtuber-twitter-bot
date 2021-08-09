'''
reference  YouTube API
    http://www.spemi.org/article/youtubeapi/
'''
from __future__ import print_function
from dics import YT_ID_dic, tw_url_dic, tw_id_dic
import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
from tools import twitter_api
api = twitter_api()

sl_time = 3


# YouTubeチャンネル登録者数を返す。
def get_subscriber(name):
    time.sleep(sl_time)

    API_KEY = os.environ['YT_API_KEY']
    options = {'key': API_KEY,
               'id': YT_ID_dic[name],
               'part': 'statistics'}

    r = requests.get(
        'https://www.googleapis.com/youtube/v3/channels', params=options)
    data = r.json()
    subsc = data['items'][0]['statistics']['subscriberCount']
    subsc = int(subsc)

    return subsc


# Twitterフォロワー数を返す。
def get_follower(name):
    id = tw_id_dic[name]
    tw_user = api.get_user(id)
    time.sleep(1)
    follower = tw_user.followers_count

    return follower


# Twitterプロフィールの内容を返す。
# tw_icon、tw_bannerは画像のURLが入っている。
def get_twitter_profile(name):
    time.sleep(sl_time)

    id = tw_id_dic[name]
    tw_user = api.get_user(id)
    tw_name = tw_user.name
    tw_desc = tw_user.description.replace('\n', ' ')
    tw_place = tw_user.location
    tw_url = tw_user.url
    tw_icon = tw_user.profile_image_url.replace('normal', '400x400')
    tw_banner = tw_user.profile_banner_url

    contents = {'名前': tw_name,
                '概要欄': tw_desc,
                '場所': tw_place,
                'URL': tw_url,
                'アイコン': tw_icon,
                'バナー': tw_banner}

    return contents


# セキュリティ対策
def enable_download_in_headless_chrome(driver, download_dir):
    driver.command_executor._commands["send_command"] = (
        "POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {
        'behavior': 'allow', 'downloadPath': download_dir}}
    driver.execute("send_command", params)


# スクショのための準備
def chrome_driver():
    time.sleep(sl_time)
    options = Options()
    options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    #options.binary_location = './bin/headless-chromium'
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument("--single-process")
    options.add_argument('window-size=1440x1440')
    browser = webdriver.Chrome(executable_path=str(os.environ.get('CHROMEDRIVER_PATH')),
                               options=options)
    browser.implicitly_wait(10)

    return browser


# スクショ実行
# browser = chrome_driver(), nameはVTuberの名前、png_pathはスクショ画像のパス
def get_twitter_profile_ss(browser, name, png_path):
    time.sleep(sl_time)
    browser.get(tw_url_dic[name])
    time.sleep(5)

    xpath = os.environ['TW_FULL_XPATH']
    element = browser.find_element_by_xpath(xpath)
    browser.get_screenshot_as_file(png_path)
    left = int(element.location['x'])
    top = int(element.location['y'])
    right = int(element.location['x'] + element.size['width'])
    bottom = int(element.location['y'] + element.size['height'])
    im = Image.open(png_path)
    im = im.crop((left, top, right, bottom))
    im.save(png_path)

    return browser
