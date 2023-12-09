# 必要モジュール
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
        response.raise_for_status()
        data = response.json()

        # ポケモンの種族情報を取得するためのURL
        species_url = data["species"]["url"]

        # 種族情報から日本語の名前を取得
        species_response = requests.get(species_url)
        species_response.raise_for_status()
        species_data = species_response.json()

        # 日本語の名前を探す
        for name in species_data["names"]:
            if name["language"]["name"] == "ja":
                japanese_name = name["name"]
                break
        else:
            japanese_name = None  # 日本語の名前が見つからない場合

        return {
            "name_jp": japanese_name,
            "height": data["height"],
            "weight": data["weight"],
        }
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


# データベースにポケモンのデータを保存
def save_pokemon_to_db(pokemon_data):
    if pokemon_data is None or pokemon_data["name_jp"] is None:
        return

    try:
        with psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS pokemon (
                        id SERIAL PRIMARY KEY,
                        name_jp VARCHAR(255),
                        height FLOAT,
                        weight FLOAT
                    )
                    """
                )

                cursor.execute(
                    "INSERT INTO pokemon (name_jp, height, weight) VALUES (%s, %s, %s)",
                    (
                        pokemon_data["name_jp"],
                        pokemon_data["height"],
                        pokemon_data["weight"],
                    ),
                )
                conn.commit()
                print(f"Saved Pokemon {pokemon_data['name_jp']} to database.")
    except psycopg2.DatabaseError as e:
        print(f"Database Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    for pokemon_id in range(1, 11):  # 例として最初の10匹のポケモンを取得
        pokemon_data = fetch_pokemon_data(pokemon_id)
        save_pokemon_to_db(pokemon_data)


if __name__ == "__main__":
    main()
