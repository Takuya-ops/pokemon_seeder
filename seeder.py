import requests
import psycopg2
import sys
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# 環境変数からデータベース接続設定を取得
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))  # ポート番号を整数に変換
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")


# PokeAPIからポケモンのデータを取得
def fetch_pokemon_data(pokemon_id):
    api_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # ステータスコードが200系以外の場合、例外を発生させる
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
    return None


# データベースにポケモンのデータを保存
def save_pokemon_to_db(pokemon_data):
    if pokemon_data is None:
        return

    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as cursor:
                # テーブルが存在しない場合、作成
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS pokemon (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        height FLOAT,
                        weight FLOAT
                    )
                    """
                )

                # データを挿入
                cursor.execute(
                    "INSERT INTO pokemon (name, height, weight) VALUES (%s, %s, %s)",
                    (
                        pokemon_data["name"],
                        pokemon_data["height"],
                        pokemon_data["weight"],
                    ),
                )
                conn.commit()
                print(f"Saved Pokemon {pokemon_data['name']} to database.")
    except psycopg2.DatabaseError as e:
        print(f"Database Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


# スクリプトのメイン部分
def main():
    for pokemon_id in range(1, 10):  # 例として最初の809匹のポケモンを取得
        pokemon_data = fetch_pokemon_data(pokemon_id)
        save_pokemon_to_db(pokemon_data)


if __name__ == "__main__":
    main()
