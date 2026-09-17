import json

# 11段階のレベル定義
# 1: 中学校卒業レベル
# 2: 高校1年生前期レベル
# 3: 高校1年生後期レベル
# 4: 高校2年生前期レベル
# 5: 高校2年生後期レベル
# 6: 高校3年生前期レベル
# 7: 高校3年生後期レベル
# 8: 共通テストレベル
# 9: 地方国公立レベル
# 10: 中堅国公立レベル
# 11: 旧帝国公立レベル

def estimate_difficulty(word, meaning):
    """
    単語の長さや一般的な難易度、意味の複雑さに基づいて1〜11のレベルを推定する関数
    （必要に応じて辞書や外部API、AIモデルの判定ロジックに置き換えることができます）
    """
    word = word.lower()
    length = len(word)
    
    # 簡単なサンプル判定ロジック（実際にはAIによる判定や頻出度データベースと照合します）
    if length <= 4 and any(basic in meaning for be in ["いる", "ある", "する", "持つ", "行く"]):
        return 1  # 中学校卒業レベル
    elif length <= 5:
        return 2  # 高校1年生前期レベル
    elif length <= 6:
        return 3  # 高校1年生後期レベル
    elif length <= 7:
        return 4  # 高校2年生前期レベル
    elif length <= 8:
        return 5  # 高校2年生後期レベル
    elif length <= 9:
        return 6  # 高校3年生前期レベル
    elif length <= 10:
        return 7  # 高校3年生後期レベル
    elif "専門" in meaning or length == 11:
        return 8  # 共通テストレベル
    elif length == 12:
        return 9  # 地方国公立レベル
    elif length == 13:
        return 10 # 中堅国公立レベル
    else:
        return 11 # 旧帝国公立レベル（最難関）

def update_vocab_json(filename='db_eng_vocab.json'):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"合計 {len(data)} 語の単語データを読み込みました。11段階への自動振り分けを開始します...")
        
        for item in data:
            word = item.get('word', '')
            meaning = item.get('meaning', '')
            # AI/アルゴリズムによる11段階（1〜11）の判定を適用
            item['difficulty'] = estimate_difficulty(word, meaning)
            
        # 更新したデータを保存
        output_filename = 'db_eng_vocab_11levels.json'
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✨ 完了しました！ 11段階に振り分けたデータを '{output_filename}' として保存しました。")
        print("HTML側の読み込みファイルをこの新しいファイル名に変更してお使いください。")
        
    except FileNotFoundError:
        print(f"エラー: '{filename' が見つかりませんでした。ファイル名を確認してください。")

if __name__ == '__main__':
    update_vocab_json()