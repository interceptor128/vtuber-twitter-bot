from __future__ import print_function
from dics import members, tw_id_dic, bitly_yt_dic
from get_data import get_subscriber, get_follower, get_twitter_profile, get_twitter_profile_ss, chrome_driver
from tools import twitter_api, tweet_with_imgs, download_image, concatenate_img
import time
import datetime
import pickle
import os
from glob import glob

import tweepy
from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

api = twitter_api()


sl_time = 3
rn_time = 5  # 何分ごとに登録者数とかの数値を取得するか

num_log_file = './num_log_file_{}.pickle'
data_log_file = './data_log_file_{}.pickle'
icon_img = './{}_icon_{}.png'
banner_img = './{}_banner_{}.png'
prof_img = './{}_prof_{}.png'

member_all = [members]

all_num = len(member_all)


# 数値を取得して、条件を満たせばツイートする
def number_notification(members_, num):
    start_ = time.time()
    num_log_file_ = num_log_file.format(num)
    tweet_head = '【達成通知】\n\n'

    if os.path.exists(num_log_file_):
        with open(num_log_file_, 'rb') as pi:
            old_contents = pickle.load(pi)

    contents = {}
    for member in members_:
        follower = get_follower(member)
        subscriber = get_subscriber(member)
        # tc_data     = get_twitcas_data(member)
        contents_in = {'follower': follower, 'subscriber': subscriber}
        # 'tc_supporter': tc_data['supporter'], 'tc_level': tc_data['level']}
        contents.update({member: contents_in})

    if not os.path.exists(num_log_file_):
        with open(num_log_file_, 'wb') as pi:
            pickle.dump(contents, pi)

    with open(num_log_file_, 'rb') as pi:
        old_contents = pickle.load(pi)

    # th_val人刻みでツイートするための条件設定。th_val = 10000 なら10000人刻み
    def _judge(member, key, th_val=10000):
        if key in contents[member].keys():
            if contents[member][key] // th_val > old_contents[member][key] // th_val:
                return True
            else:
                return False
        else:
            return False

    # botが過去50ツイートと同じツイートしようとしたらキャンセルする（はず）
    recent_tweets = api.user_timeline(count=50)
    recent_tweets = [tweet.text for tweet in recent_tweets]

    def _tw_cancel(tweet):
        flags = [r_tweet.split('(')[0] in tweet for r_tweet in recent_tweets]
        if sum(flags) == 0:
            return True
        else:
            print('CANCELLED : ', tweet)
            return False

    for member in members_:
        member_ = member + 'さん'

        if _judge(member, 'follower'):
            tw_url = api.get_user(tw_id_dic[member]).screen_name
            tweet = tweet_head + '{}のTwitterフォロワー数が\n  {:.1f}万人を達成しました。\n'\
                .format(member_, contents[member]['follower']/10000)
            tweet += '(Twitter : twitter.com/{})\n'.format(tw_url)
            if _tw_cancel(tweet):
                time.sleep(sl_time)
                api.update_status(tweet)
                print('number_notification')
                print('Tweeted.')

        if _judge(member, 'subscriber'):
            tweet = tweet_head + '{}のチャンネル登録者数が\n  {:.1f}万人を達成しました。\n'\
                .format(member_, contents[member]['subscriber']/10000)
            tweet += '(YouTube : {})\n'.format(bitly_yt_dic[member])
            if _tw_cancel(tweet):
                time.sleep(sl_time)
                api.update_status(tweet)
                print('number_notification')
                print('Tweeted.')

    with open(num_log_file_, 'wb') as pi:
        pickle.dump(contents, pi)

    measure_time = time.time() - start_
    if measure_time > 60 * rn_time:
        print('Too hard work on number_notification')


# Twitterプロフの変更を検知してツイートする
def tw_log_notification(members_, num):
    start_ = time.time()
    contents = {}
    for member in members_:
        contents.update({member: get_twitter_profile(member)})

    data_log_file_ = data_log_file.format(num)
    if not os.path.exists(data_log_file_):
        with open(data_log_file_, 'wb') as pi:
            pickle.dump(contents, pi)

    with open(data_log_file_, 'rb') as pi:
        old_contents = pickle.load(pi)

    browser = chrome_driver()
    for name in contents.keys():
        if not os.path.exists(icon_img.format('old', name)):
            download_image(contents[name]['アイコン'],
                           icon_img.format('old', name))
        if not os.path.exists(banner_img.format('old', name)):
            download_image(contents[name]['バナー'],
                           banner_img.format('old', name))
        if not os.path.exists(prof_img.format('old', name)):
            browser = get_twitter_profile_ss(
                browser, name, prof_img.format('old', name))

    def _make_tweet(browser, name, key):
        name_ = name + 'さん'

        tweet = '【twitter プロフィール変更通知】\n\n'
        tweet += '{}が{}を変更しました。\n'.format(name_, key)
        if contents[name][key] != old_contents[name][key]:
            if key == 'アイコン':
                print('tw_log_notification')
                download_image(contents[name][key],
                               icon_img.format('new', name))
                concatenate_img(icon_img.format('old', name), icon_img.format(
                    'new', name), icon_img.format('tw', name))
                tweet_with_imgs(tweet, icon_img.format('tw', name))
                os.rename(icon_img.format('new', name),
                          icon_img.format('old', name))

            elif key == 'バナー':
                print('tw_log_notification')
                tweet += '1枚目　→　2枚目'
                download_image(contents[name][key],
                               banner_img.format('new', name))
                tweet_with_imgs(tweet, [banner_img.format(
                    'old', name), banner_img.format('new', name)])
                os.rename(banner_img.format('new', name),
                          banner_img.format('old', name))

            elif key in ['お気に入り数', 'URL']:
                pass

            else:
                print('tw_log_notification')
                if key in ['名前', '場所']:
                    tweet += '(左) {}\n　　↓\n(右) {}'.format(
                        old_contents[name][key], contents[name][key])
                print(old_contents[name][key])
                print(contents[name][key])
                browser = get_twitter_profile_ss(
                    browser, name, prof_img.format('new', name))
                concatenate_img(prof_img.format('old', name), prof_img.format(
                    'new', name), prof_img.format('tw', name))
                tweet_with_imgs(tweet, prof_img.format('tw', name))

        return browser

    for name in contents.keys():
        for key in contents[name].keys():
            browser = _make_tweet(browser, name, key)
        if os.path.exists(prof_img.format('new', name)):
            os.rename(prof_img.format('new', name),
                      prof_img.format('old', name))
        if os.path.exists(prof_img.format('new', name+'sub')):
            os.rename(prof_img.format('new', name+'sub'),
                      prof_img.format('old', name+'sub'))
    browser.quit()

    with open(data_log_file_, 'wb') as pi:
        pickle.dump(contents, pi)

    measure_time = time.time() - start_
    if measure_time > 60 * rn_time:
        print('Too hard work on tw_log_notification')


if __name__ == '__main__':
    start_ = time.time()
    print('Start work : {}'.format(datetime.datetime.utcnow()))

    for ii, mem_ in enumerate(member_all):
        print('test number_not : {} : {}'.format(ii, mem_))
        number_notification(mem_, ii+1)
        sched.add_job(number_notification, 'interval',
                      minutes=rn_time, args=[mem_, ii+1])
    for ii, mem_ in enumerate(member_all):
        print('test tw_log_not : {} : {}'.format(ii, mem_))
        tw_log_notification(mem_, ii+1)
        sched.add_job(tw_log_notification, 'interval',
                      minutes=rn_time, args=[mem_, ii+1])

    print(time.time() - start_)

    print('old_prof  ', len(glob('old_prof*')))
    print('old_banner', len(glob('old_banner*')))
    print('old_icon  ', len(glob('old_icon*')))

    print('sched work start')
    sched.start()
