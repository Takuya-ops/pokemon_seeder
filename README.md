# 目的
PokeAPIから取得したデータをDB（Postgres）に入れる用のseederです（name, height, weight）。

# 利用方法
## ローカル環境にクローン
git clone このリポジトリのリンク

## 仮想環境の作成
virtualenv 任意の環境名

## 仮想環境の有効化
source ./任意の環境名/bin/activate

## 必要モジュールのインストール
pip install -r requirements.txt

## 環境変数の登録
.envファイルを作成し、以下の内容を追記してください。
```記入例
DB_HOST = "localhost"
DB_PORT= 5436
DB_NAME = "your_dbname"
DB_USER = "your_username"
DB_PASS = "your_password"
```

## postgresのdockerコンテナの起動（docker desktopを入れておいてください）
make up

## 認証情報の登録
ターミナルで以下のコマンドを実行。
```
docker run -d \
  --name postgres-container \
  -e POSTGRES_DB=your_dbname \
  -e POSTGRES_USER=your_username \
  -e POSTGRES_PASSWORD=your_password \
  -p 5436:5432 \
  postgres
```

## データの取得と投入
make seed

## データの確認
データベース確認用のツールで確認してください。

※ おすすめツール
https://www.beekeeperstudio.io/
https://www.pgadmin.org/download/

以下のようにデータが投入されていれば成功です。
<img width="1440" alt="スクリーンショット 2023-12-09 23 03 01" src="https://github.com/Takuya-ops/pokemon_seeder/assets/83127305/38ee2fd0-8c72-458e-92f8-ee44a95011e6">

