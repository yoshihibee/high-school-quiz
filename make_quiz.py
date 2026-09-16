import os

# --- 既存のクイズ生成処理のあと ---

# 履歴用JSONファイルのパス
history_filename = f"{selected_code}_history.json"
history_list = []

# すでに履歴ファイルがあれば読み込む
if os.path.exists(history_filename):
    try:
        with open(history_filename, "r", encoding="utf-8") as hf:
            history_list = json.load(hf)
    except:
        history_list = []

# 本日の日付がまだ履歴に無ければ追加（重複防止）
if timestamp not in history_list:
    history_list.insert(0, timestamp) # 新しいものを先頭に
    # 最大保持件数（例: 直近10回分まで残す場合）
    history_list = history_list[:10]

# 履歴ファイルに保存
with open(history_filename, "w", encoding="utf-8") as hf:
    json.dump(history_list, hf, ensure_ascii=False, indent=2)

print(f"  💾 【履歴更新完了】 {history_filename}")
