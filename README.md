# vtuber-twitter-bot

Twitterのプロフィール文章及びプロフ画像の変更、またYoutubeチャンネル登録者数を監視し変化があったらツイートするPythonプログラムです。

参考サイト  
[heroku + Python で Vtuber Twitter bot 作る - Qiita](https://qiita.com/iroiro_bot/items/3406caf025e89b8f7a25)

## ファイル構成解説

root.  
├── .font  
│   └── `SourceHanMono-Regular.otf`  
├── `LICENSE`  
├── `Procfile` ← heroku用実行時設定ファイル  
├── `README.md`  
├── `dics.py` ← vtuberのリスト  
├── `get_data.py` ← SS等の機能別処理  
├── `index.py` ← heroku実行用ダミーファイル  
├── `main.py` ← メイン処理  
├── `requirements.txt` ← Pythonモジュール＆パッケージリスト  
├── `runtime.txt` ← heroku用Pythonバージョン指定ファイル  
└── `tools.py` ← twitter関連処理

## Herokuにデプロイする時の注意点

### スクリーンショット文字化け対策

デフォルトだと日本語フォントが入っていないため、スクリーンショットに文字化けが発生する  
対策方法を以下に記す。  

1. 100MB未満の日本語フォント（フリー）をダウンロード
1. .fonts フォルダを作成
1. ダウンロードしたフォントを .fonts に格納
1. 最後にコミット（マージ）し、デプロイする

### Twitter仕様変更対策  

スクリーンショット要素を環境変数として設定する

#### コード例

```python
import os

xpath   = os.environ['TW_FULL_XPATH']
element = browser.find_element_by_xpath(xpath)
```

環境変数はアプリのSettings→Config Varsで設定できる  
KEYに環境変数、Valueに環境変数に割り当てる値を設定する
