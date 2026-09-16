import json
from datetime import datetime
from google import genai

# APIキーの設定
API_KEY = "AQ.Ab8RN6IsMS7_tgW3XLpwVXQDCGNxBP8zjgvpWYDATKU96_zq0g"
client = genai.Client(api_key=API_KEY)

# テスト用に「情報I」の1科目、10問だけに絞る
SUBJECTS = [
    {"code": "info1", "name": "情報I"},
]

QUESTIONS_PER_SUBJECT = 10
BATCH_SIZE = 10

print("=== テスト用クイズ生成システム ===")

for sub in SUBJECTS:
    selected_subject = sub["name"]
    selected_code = sub["code"]
    print(f"\n📚 【{selected_subject}】のテスト生成を開始します...")

    prompt = (
        f"高校の【{selected_subject}】の四肢択一問題を10問作成してください。\n"
        "難易度は1〜20の範囲で設定してください。\n"
        "出力フォーマットは必ず以下のJSON配列（[...]）のみで返してください：\n"
        '[{"id": 数値, "q": "問題文", "opts": ["選択肢1", "選択肢2", "選択肢3", "選択肢4"], "a": 正解インデックス(0-3), "exp": "解説", "difficulty": 1〜20の整数}]'
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    clean_text = response.text.replace("```json", "").replace("```", "").strip()
    all_questions = json.loads(clean_text)

    # 当日の日付（2026年9月17日）に合わせたファイル名にする
    date_str = "20260917"
    html_filename = f"{selected_code}_LevelQuiz_{date_str}.html"

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>{selected_subject} クイズ演習</title>
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
  <h1>{selected_subject} テストクイズ演習</h1>
  <div id="start-section" class="card">
    <button class="btn" onclick="startQuiz()">クイズを始める（全10問）</button>
  </div>
  <div id="quiz-section" class="card hidden">
    <div>
      <span id="progress"></span>
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
    let currentIndex = 0;
    let score = 0;
    function startQuiz() {{
      currentIndex = 0; score = 0;
      document.getElementById('start-section').classList.add('hidden');
      document.getElementById('quiz-section').classList.remove('hidden');
      showQuestion();
    }}
    function showQuestion() {{
      document.getElementById('result-area').classList.add('hidden');
      const q = rawQuestions[currentIndex];
      document.getElementById('progress').innerText = `問題 ${{currentIndex + 1}} / ${{rawQuestions.length}}`;
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
      const q = rawQuestions[currentIndex];
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
      if (currentIndex < rawQuestions.length) {{ showQuestion(); }}
      else {{ alert(`終了！スコア: ${{score}} / ${{rawQuestions.length}}`); location.reload(); }}
    }}
  </script>
</body>
</html>
"""

    with open(html_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"  💾 【保存完了】 {html_filename}")

print("\n🎉 テスト生成が完了しました！")
