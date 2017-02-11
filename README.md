# KickStarter Scraper:

まずディレクトリの一番上に行き、
```
    $cd [path to kickapp]
```
以下のようにコマンドを実行：
```
    $scrapy crawl RateSpider
    $scrapy crawl LiveSpider
```

RateSpiderは為替をとってくるスパイダーで、
LiveSpiderはKickStarterから今現在ファンデイングできるプロジェクトをとってくるスパイダーです。

env parameterではなく、OSコマンドのPWDを利用しているため、LiveSpiderとRateSpiderのコマンドは最初の/kickappダレクトリーで実行してください。
```
/kickapp    <<ここでコマンド実行します
     /rates
     /project
     /kickapp     <<ここで実行すると失敗してしまいます
     scrapy.cfg
```

