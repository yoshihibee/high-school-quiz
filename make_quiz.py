import json
import os
import time
from datetime import datetime
from google import genai

# APIキーの設定
API_KEY = "AQ.Ab8RN6IsMS7_tgW3XLpwVXQDCGNxBP8zjgvpWYDATKU96_zq0g"
client = genai.Client(api_key=API_KEY)

SUBJECTS = [
    {"code": "eng_read", "name": "英語リーディング"},
    {"code": "eng_listen", "name": "英語リスニング"},
    {"code": "math1", "name": "数学I"},
    {"code": "math_a", "name": "数学A"},
    {"code": "math2", "name": "数学Ⅱ"},
    {"code": "math_b", "name": "数学B"},
    {"code": "math_c", "name": "数学C"},
    {"code": "kokugo_gen", "name": "現代文"},
    {"code": "kokugo_ko", "name": "古文"},
    {"code": "kokugo_kan", "name": "漢文"},
    {"code": "chem_base", "name": "化学基礎"},
    {"code": "earth_base", "name": "地学基礎"},
    {"code": "geo_tankyu", "name": "地理総合探究"},
    {"code": "seikei", "name": "公共政治経済"},
    {"code": "info1", "name": "情報I"},
]

QUESTIONS_PER_SUBJECT = 200
BATCH_SIZE = 20

print("=== 自動クイズ生成システム（履歴保存・無料枠制限対応） ===")

timestamp = datetime.now().strftime("%Y%m%d")

for sub in SUBJECTS:
    selected_subject = sub["name"]
    selected_code = sub["code"]
    print(f"\n📚 【{selected_subject}】の生成を開始します...")

    all_questions = []

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
                    all_questions.extend(data)
                else:
                    all_questions.append(data)
                success = True

            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    print("\n🚨 【無料枠の制限（上限）に達しました】")
                    print("安全にプログラムを自動停止します。")
                    exit()
                
                retry_count += 1
                if retry_count > 3:
                    print(f"⚠️ エラーが続くためスキップします: {e}")
                    success = True
                else:
                    print(f"  ⚠️ 一時的なエラー。20秒後に再試行します: {e}")
                    time.sleep(20)

        time.sleep(4)

    # 1. クイズ演習用HTMLファイルの保存
    html_filename = f"{selected_code}_LevelQuiz_{timestamp}.html"
    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>{selected_subject} 20段階難易度クイズ</title>
  <style>
    body {{ font-family: sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; line-height: 1.6; background: #fdfbf7; }}
    .card {{ border: 1px solid #ddd; padding: 20px; border-radius: 8px; background: #fff; box-shadow: 2px 2px 8px rgba(0,0,0,0.05); margin-bottom: 15px; }}
    .btn {{ background: #0066cc; color: #fff; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }}
    .btn:hover {{ background: #004c99; }}
    .opt-btn {{ display: block; width: 100%; text-align: left; padding: 12px; margin: 8px 0; border: 1px solid #ddd; background: #f9f9f9; border-radius: 4px; cursor: pointer; font-size: 16px; }}
    .opt-btn:hover {{ background: #eef; }}
    .badge {{ background: #ff9900; color: white; padding: 3px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
    .explanation {{ background: #f0f8ff; border-left: 4px solid #0066cc; padding: 12px; margin-top: 15px; border-radius: 0 4px 4px 0; }}
    .hidden {{ display: none; }}
  </style>
</head>
<body>
  <h1>{selected_subject} クイズ演習アプリ</h1>
  <div id="start-section" class="card">
    <h3>挑戦する難易度を選んでください</h3>
    <label>難易度フィルター: 
      <select id="diff-filter" style="padding: 5px; font-size: 14px;">
        <option value="all">すべての難易度</option>
        <script>
          for(let d=1; d<=20; d++) {{
            document.write(`<option value="${{d}}">レベル ${{d}}</option>`);
          }}
        </script>
      </select>
    </label><br><br>
    <button class="btn" onclick="startQuiz()">クイズを始める</button>
  </div>
  <div id="quiz-section" class="card hidden">
    <div>
      <span id="progress"></span>
      <span id="diff-badge" class="badge" style="margin-left: 10px;"></span>
      <span id="score-count" style="float:right;"></span>
    </div>
    <h2 id="question-text"></h2>
    <div id="options-container"></div>
    <div id="result-area" class="hidden">
      <h3 id="judge"></h3>
      <div id="explanation" class="explanation"></div>
      <button class="btn" onclick="nextQuestion()">次の問題へ</button>
    </div>
  </div>
  <script>
    const rawQuestions = {json.dumps(all_questions, ensure_ascii=False)};
    let questions = [];
    let currentIndex = 0;
    let score = 0;
    function startQuiz() {{
      const selectedDiff = document.getElementById('diff-filter').value;
      questions = (selectedDiff === 'all') ? [...rawQuestions] : rawQuestions.filter(q => q.difficulty == selectedDiff);
      if (questions.length === 0) {{ alert("指定した難易度の問題が見つかりませんでした"); return; }}
      currentIndex = 0; score = 0;
      document.getElementById('start-section').classList.add('hidden');
      document.getElementById('quiz-section').classList.remove('hidden');
      showQuestion();
    }}
    function showQuestion() {{
      document.getElementById('result-area').classList.add('hidden');
      const q = questions[currentIndex];
      document.getElementById('progress').innerText = `問題 ${{currentIndex + 1}} / ${{questions.length}}`;
      document.getElementById('diff-badge').innerText = `レベル ${{q.difficulty || 1}} / 20`;
      document.getElementById('score-count').innerText = `正解数: ${{score}}`;
      document.getElementById('question-text').innerText = q.q;
      const optsContainer = document.getElementById('options-container');
      optsContainer.innerHTML = '';
      q.opts.forEach((opt, idx) => {{
        const btn = document.createElement('button');
        btn.className = 'opt-btn';
        btn.innerText = `${{idx + 1}}. ${{opt}}`;
        btn.onclick = () => checkAnswer(idx);
        optsContainer.appendChild(btn);
      }});
    }}
    function checkAnswer(selectedIdx) {{
      const q = questions[currentIndex];
      const resultArea = document.getElementById('result-area');
      const judge = document.getElementById('judge');
      const exp = document.getElementById('explanation');
      if (selectedIdx === q.a) {{ judge.innerText = "⭕ 正解！"; judge.style.color = "green"; score++; }}
      else {{ judge.innerText = `❌ 不正解... (正解: ${{q.a + 1}}. ${{q.opts[q.a]}})`; judge.style.color = "red"; }}
      exp.innerText = q.exp || "解説なし";
      resultArea.classList.remove('hidden');
    }}
    function nextQuestion() {{
      currentIndex++;
      if (currentIndex < questions.length) {{ showQuestion(); }}
      else {{ alert(`終了！スコア: ${{score}} / ${{questions.length}}`); location.reload(); }}
    }}
  </script>
</body>
</html>
"""
    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 2. 作問履歴用JSONファイルの更新処理
    history_filename = f"{selected_code}_history.json"
    history_list = []
    if os.path.exists(history_filename):
        try:
            with open(history_filename, "r", encoding="utf-8") as hf:
                history_list = json.load(hf)
        except:
            history_list = []
    
    if timestamp not in history_list:
        history_list.insert(0, timestamp)
        history_list = history_list[:10] # 直近10回分まで保持

    with open(history_filename, "w", encoding="utf-8") as hf:
        json.dump(history_list, hf, ensure_ascii=False, indent=2)

    print(f"  💾 【保存＆履歴更新完了】 {html_filename}")

print("\n🎉 すべての科目の処理が完了しました！")
