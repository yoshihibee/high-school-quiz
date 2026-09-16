import json
import os
import time
from datetime import datetime
from google import genai

# APIキーの設定
API_KEY = "AQ.Ab8RN6IsMS7_tgW3XLpwVXQDCGNxBP8zjgvpWYDATKU96_zq0g"
client = genai.Client(api_key=API_KEY)

SUBJECTS = [
    {"code": "eng_read", "name": "英語リーディング", "color": "#3b82f6"},
    {"code": "eng_listen", "name": "英語リスニング", "color": "#60a5fa"},
    {"code": "math1", "name": "数学I", "color": "#10b981"},
    {"code": "math_a", "name": "数学A", "color": "#34d399"},
    {"code": "math2", "name": "数学Ⅱ", "color": "#059669"},
    {"code": "math_b", "name": "数学B", "color": "#047857"},
    {"code": "math_c", "name": "数学C", "color": "#6ee7b7"},
    {"code": "kokugo_gen", "name": "現代文", "color": "#f59e0b"},
    {"code": "kokugo_ko", "name": "古文", "color": "#fbbf24"},
    {"code": "kokugo_kan", "name": "漢文", "color": "#d97706"},
    {"code": "chem_base", "name": "化学基礎", "color": "#8b5cf6"},
    {"code": "earth_base", "name": "地学基礎", "color": "#a78bfa"},
    {"code": "geo_tankyu", "name": "地理総合探究", "color": "#ec4899"},
    {"code": "seikei", "name": "公共政治経済", "color": "#f43f5e"},
    {"code": "info1", "name": "情報I", "color": "#06b6d4"},
]

QUESTIONS_PER_SUBJECT = 200
BATCH_SIZE = 20

print("=== 自動クイズ生成・データベース蓄積システム ===")

for sub in SUBJECTS:
    selected_subject = sub["name"]
    selected_code = sub["code"]
    print(f"\n📚 【{selected_subject}】の生成を開始します...")

    new_questions = []

    for i in range(0, QUESTIONS_PER_SUBJECT, BATCH_SIZE):
        start_num = i + 1
        end_num = min(i + BATCH_SIZE, QUESTIONS_PER_SUBJECT)

        prompt = (
            f"高校の【{selected_subject}】の四肢択一問題を{start_num}問目から{end_num}問目まで作成してください。\n"
            "難易度は基礎（1）から超難問（20）までの20段階に細かく分けて、それぞれの問題に設定してください。\n"
            "出力フォーマットは必ず以下のJSON配列（[...]）のみで返してください：\n"
            '[{"id": 数値, "q": "問題文", "opts": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"], "a": 正解インデックス(0-3), "exp": "解説", "difficulty": 1〜20の整数}]'
        )

        success = False
        retry_count = 0

        while not success:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )
                clean_text = (
                    response.text.replace("```json", "")
                    .replace("```", "")
                    .strip()
                )
                data = json.loads(clean_text)
                if isinstance(data, list):
                    new_questions.extend(data)
                else:
                    new_questions.append(data)
                success = True

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    print("\n🚨 【無料枠の制限に達しました】安全に停止します。")
                    exit()
                
                retry_count += 1
                if retry_count > 3:
                    print(f"⚠️ エラーが続くためスキップします: {e}")
                    success = True
                else:
                    print(f"  ⚠️ 一時的なエラー。20秒後に再試行します: {e}")
                    time.sleep(20)

        time.sleep(4)

    db_filename = f"db_{selected_code}.json"
    existing_questions = []
    if os.path.exists(db_filename):
        try:
            with open(db_filename, "r", encoding="utf-8") as df:
                existing_questions = json.load(df)
        except:
            existing_questions = []

    combined_questions = new_questions + existing_questions
    combined_questions = combined_questions[:1000]

    with open(db_filename, "w", encoding="utf-8") as df:
        json.dump(combined_questions, df, ensure_ascii=False, indent=2)

    print(f"  💾 【データベース更新完了】 {db_filename} (総問題数: {len(combined_questions)}問)")

print("\n🎉 全科目の処理が完了しました！")
