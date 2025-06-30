import requests
import base64
import re
import wave
import time
import os

# エンドポイント設定
API_URL_A = "http://localhost:3001/api/speak_text"      # 話者A
API_URL_B = "http://localhost:3002/api/speak_text"    # 話者B

# 話者設定
SPEAKER_ID_A = 2
SPEAKER_ID_B = 1
SPEED_SCALE = 1.3

# 会話内容（交互に話す）
conversations = [
    {"speaker": "A", "text": "みなさん、こんにちは！ポッドキャストへようこそ。"},
    {"speaker": "B", "text": "こんにちは、Aさん。今日はどんな話題ですか？"},
    {"speaker": "A", "text": "今日はAIと音声合成について話しましょう。"},
    {"speaker": "B", "text": "面白そうですね！最近のAIは本当にすごいです。"},
    {"speaker": "A", "text": "そうですね。リスナーのみなさんもぜひ体験してみてください。"},
    {"speaker": "B", "text": "それでは、また次回お会いしましょう！ありがとうございました。"},
]

os.makedirs("assets", exist_ok=True)

for i, conv in enumerate(conversations):
    if conv["speaker"] == "A":
        api_url = API_URL_A
        speaker_id = SPEAKER_ID_A
        file_prefix = "A"
    else:
        api_url = API_URL_B
        speaker_id = SPEAKER_ID_B
        file_prefix = "B"

    payload = {
        "text": conv["text"],
        "speakerId": speaker_id,
        "speedScale": SPEED_SCALE
    }
    print(f"[{i+1}] {conv['speaker']} → APIリクエスト: {conv['text']}")
    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    data = response.json()

    # audioフィールドからWAVデータを抽出して保存
    audio_data_uri = data["audio"]
    m = re.match(r"data:audio/wav;base64,(.*)", audio_data_uri)
    if not m:
        raise ValueError("audioフィールドが想定外の形式です")
    audio_base64 = m.group(1)
    audio_bytes = base64.b64decode(audio_base64)
    output_path = f"assets/podcast_{file_prefix}_{i+1}.wav"
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    print(f"[{i+1}] 音声ファイルを{output_path}として保存しました。")

    # 音声の長さ分だけ待機
    with wave.open(output_path, "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    print(f"[{i+1}] 音声の長さ: {duration:.2f}秒")
    if i < len(conversations) - 1:
        print(f"[{i+1}] {duration:.2f}秒待機して次の会話へ...")
        time.sleep(duration)