# 774トゥデイ
774トゥデイは、774 inc.に所属する所属タレントの配信スケジュールをタイムライン形式で表示する非公式ファンサイトです。

## 内容
774トゥデイは、配信スケジュールに関するデータを取得するプログラムと、配信スケジュールを表示するウェブサイトの2つの部分から構成されています。それぞれの部分は独立に動作します。

### 配信スケジュールに関するデータの取得 (/procedure)
この部分は下記のプログラムで構成されています。このプログラムはAWS Lambdaのようなサービスによって定期的に実行されると想定されています。
- GetStreamingTime.py
配信スケジュールに関するデータを取得するプログラムです。このプログラムはpythonで記述されています。得られたデータはウェブサーバーにアップロードされます。プログラム中ではYouTube Data APIとTwitch APIを使用します。

### 配信スケジュールの表示 (/server)
この部分は下記のファイルから構成されています。これらのファイルは、配信スケジュールに関するデータと一緒に、ウェブサーバーに置かれると想定されています。
- index.html
配信スケジュールを表示するウェブサイトです。このウェブサイトはhtml,css,javascriptで記述されています。
- resources.json
774 inc.所属のタレントについての情報です。
- events.json
配信スケジュールに関するデータです。配信スケジュールに関するデータを取得するプログラムによってアップロードされます。
- *.webp
774 inc.所属のタレントの顔画像です。
- fabicon.png
ブラウザがウェブサイトのタイトルと一緒に表示する画像です。
- screenshot.png
ウェブサイトをTwitterカードで表示する際のサムネイル画像です。
- log.json
配信スケジュールに関するデータを取得するプログラムの稼働記録です。

## 開発
- 配信スケジュールに関するデータを取得するプログラムを実行するには、データをアップロードする場所と、YouTube Data API,Twitch APIのAPIキーが必要です。
- 配信スケジュールを表示するウェブサイトを閲覧するには、serverフォルダ内のファイル一式をウェブサーバーにアップロードする必要があります。また、events.jsonの内容を閲覧する日付に合わせて修正する必要があります。

## ライセンス
774トゥデイに含まれる内容には、「774 inc.」所属タレント二次創作ガイドラインのもとで公開されているものと、GNU General Public License Version 3のもとで公開されているものがあります。詳細はLICENSE.txtを確認してください。
