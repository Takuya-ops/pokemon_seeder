# Dockerコンテナの起動
up:
	docker-compose up -d

# Dockerコンテナの停止
down:
	docker-compose down

# データベースにシードデータを投入
seed:
	python seeder.py

# データベースと連携したテストの実行（仮）
test:
	python -m unittest discover -s tests

# Dockerコンテナの状態確認
ps:
	docker-compose ps

# データベースのログを表示
logs:
	docker-compose logs postgres

# Dockerコンテナの再起動
restart:
	docker-compose restart

# Dockerコンテナとボリュームの完全な停止と削除
clean:
	docker-compose down -v
