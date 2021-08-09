from __future__ import print_function
import os
import time
import urllib.request
import urllib.error
from PIL import Image, ImageDraw
import tweepy

sl_time = 3


# Twitterでツイートしたりデータを取得したりする準備
def twitter_api():
    CONSUMER_KEY = os.environ['API_KEY']
    CONSUMER_SECRET = os.environ['API_SECRET_KEY']
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
    ACCESS_SECRET = os.environ['ACCESS_TOKEN_SECRET']
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth)

    return api


# 画像と一緒にツイートする
# tweetはツイートする文章、filesは画像のパスのlist
def tweet_with_imgs(tweet, files):
    api = twitter_api()
    time.sleep(sl_time)
    api.update_with_media(status=tweet, filename=files)


# urlにある画像をdst_pathで指定したパスにダウンロードする
def download_image(url, dst_path):
    try:
        data = urllib.request.urlopen(url).read()
        with open(dst_path, mode="wb") as f:
            f.write(data)
    except urllib.error.URLError as e:
        print(e)


# 2つの画像をつなげた画像を作る
# im1_path, im2_pathでパスを指定した2画像を矢印でつなげ、gen_img_nameというパスに保存
def concatenate_img(im1_path, im2_path, gen_img_name):
    im1 = Image.open(im1_path)
    im2 = Image.open(im2_path)

    void_pix = 30
    dst_width = im1.width + im2.width + void_pix
    dst_height = max(im1.height, im2.height)
    dst = Image.new('RGBA', (dst_width, dst_height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width + void_pix, 0))

    draw = ImageDraw.Draw(dst)
    line_xm = int(im1.width - 5)
    line_xp = int(dst_width - im2.width - 5)
    line_y = int(dst_height / 2)
    line_width = 20
    arrow_x = line_xp - 5
    line_coor = (line_xm, line_y, line_xp, line_y)
    arrow_coor = (line_xp+line_width/2, line_y,
                  arrow_x, line_y+line_width,
                  arrow_x, line_y-line_width)
    line_c = (70, 170, 255)
    draw.line(line_coor, fill=line_c, width=line_width)
    draw.polygon(arrow_coor, fill=line_c)
    dst.save(gen_img_name)
