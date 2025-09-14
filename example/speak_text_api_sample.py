"""
ChatVRM API /api/speak_text サンプル

- 任意のテキストをPOSTするだけでVRMキャラクターがVOICEVOX音声で喋ります
"""

import requests

# ChatVRMのAPIエンドポイント
API_URL = "http://localhost:3002/api/speak_text"

# 喋らせたいテキスト・話者ID・話速
payload = {
    "text": "こんにちは、VOICEVOXでテキストから直接喋らせるサンプルです。",
    "speakerId": 1,      # VOICEVOXの話者ID（省略可）
    "speedScale": 1.0    # 話速（省略可）
}

response = requests.post(API_URL, json=payload)
try:
    response.raise_for_status()
    print("VRMキャラクターに発話指示を送信しました。")
    data = response.json()
    print("サーバーレスポンス:", data)

    # audioフィールドがあればwavとして保存
    if "audio" in data:
        import base64
        import re
        audio_data_uri = data["audio"]
        m = re.match(r"data:audio/wav;base64,(.*)", audio_data_uri)
        if not m:
            raise ValueError("audioフィールドが想定外の形式です")
        audio_base64 = m.group(1)
        audio_bytes = base64.b64decode(audio_base64)
        output_path = "assets/output_speak_text.wav"
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        print(f"音声ファイルを{output_path}として保存しました。")
except requests.HTTPError as e:
    print("APIリクエストでエラーが発生しました:", e)
    try:
        print("サーバーレスポンス:", response.json())
    except Exception:
        print("サーバーレスポンス(非JSON):", response.text)
    raise
