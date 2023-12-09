# 必要モジュール
import requests
import psycopg2
import sys
import os
import json
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

# .envのデータベース接続設定を取得
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
        data = response.json()

        # 種族情報から日本語の名前を取得
        species_url = data["species"]["url"]
        species_response = requests.get(species_url)
        species_response.raise_for_status()
        species_data = species_response.json()

        japanese_name = None
        for name in species_data["names"]:
            if name["language"]["name"] == "ja":
                japanese_name = name["name"]
                break

        # タイプの日本語名を取得
        types = []
        for type_info in data["types"]:
            type_url = type_info["type"]["url"]
            type_response = requests.get(type_url)
            type_response.raise_for_status()
            type_data = type_response.json()

            japanese_type_name = None
            for name in type_data["names"]:
                if name["language"]["name"] == "ja":
                    japanese_type_name = name["name"]
                    break

            if japanese_type_name:
                types.append(japanese_type_name)

        # 種族値を取得
        stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

        # 画像のURLを取得
        image_url = data["sprites"]["front_default"]

        return {
            "name_jp": japanese_name,
            "height": data["height"],
            "weight": data["weight"],
            "types": types,
            "stats": stats,
            "image_url": image_url,
        }
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
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
                # スキーマ、テーブルが存在しない場合、作成
                cursor.execute("CREATE SCHEMA IF NOT EXISTS public")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS public.pokemon (
                        id SERIAL PRIMARY KEY,
                        name_jp VARCHAR(255),
                        height FLOAT,
                        weight FLOAT,
                        types VARCHAR(255),
                        stats JSONB,
                        image_url TEXT
                    )
                    """
                )

                # JSON形式で種族値を保存
                stats_json = json.dumps(pokemon_data["stats"])

                # データを挿入
                cursor.execute(
                    "INSERT INTO pokemon (name_jp, height, weight, types, stats, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
                    (
                        pokemon_data["name_jp"],
                        pokemon_data["height"],
                        pokemon_data["weight"],
                        ",".join(pokemon_data["types"]),
                        stats_json,
                        pokemon_data["image_url"],
                    ),
                )
                conn.commit()
                print(f"Saved Pokemon {pokemon_data['name_jp']} to database.")
    except psycopg2.DatabaseError as e:
        print(f"Database Error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def main():
    for pokemon_id in range(1, 810):  # 809匹のポケモンを取得（メルメタルまで）
        pokemon_data = fetch_pokemon_data(pokemon_id)
        save_pokemon_to_db(pokemon_data)


if __name__ == "__main__":
    main()
