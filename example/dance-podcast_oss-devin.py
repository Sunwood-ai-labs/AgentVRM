#!/usr/bin/env python3
"""
AgentVRM v0.4.0 Release Notes ポッドキャスト形式解説スクリプト

このスクリプトはAgentVRMのリリースノートをポッドキャスト風に解説します。
各スライドに対して、音声合成 + アニメーションを組み合わせ、
pyautoguiでスライドのページ送りを自動制御します。

実行フロー:
- 各スライドで話者A/Bが交互に内容を解説
- 話す間にアニメーション(話したて中、他はダンスなど)を同時再生
- 説明完了後に右矢印キーで次のスライドへ移動

使用方法:
1. AgentVRMサービスが起動している状態で実行します
2. リリースノートのHTMLスライドショーをブラウザで開きます
3. アニメーションファイルは public/ ディレクトリに配置されている必要があります

前提条件:
- AgentVRMサービスが http://localhost:3001 と http://localhost:3002 で起動中
- requests, tqdm, pyautogui ライブラリがインストール済み
- public/ ディレクトリに vrma または fbx アニメーションファイルがある
"""

import json
import requests
import base64
import re
import wave
import time
import os
import sys
import random
import threading
from tqdm import tqdm

try:
    import pyautogui
except Exception as e:
    pyautogui = None
    print(f"[warn] PyAutoGUI unavailable: {e}", file=sys.stderr)

# =================== アニメーション再生設定 ===================
ANIMATION_BASE_URL_A = "http://localhost:3001"  # 話者Aのアニメーションポート
ANIMATION_BASE_URL_B = "http://localhost:3002"  # 話者Bのアニメーションポート
ANIMATION_ENDPOINT = "/api/play_animation"

# 利用可能なアニメーション
TALK_ANIMATIONS = [
    "/anim/Talking1.fbx",
    "/anim/Talking2.fbx",
    "/anim/Talking3.fbx"
]

DANCE_ANIMATIONS = [
    "/anim/Samba Dancing.fbx",
    "/anim/Swing Dancing.fbx",
    "/anim/Wave Hip Hop Dance.fbx"
]

IDLE_ANIMATION = [
    "/anim/Breathing Idle.fbx",
    # "/anim/Swing Dancing.fbx",
    # "/anim/Wave Hip Hop Dance.fbx"
]
# =================== ポッドキャスト設定 ===================
API_URL_A = "http://localhost:3001/api/speak_text"      # 話者A
API_URL_B = "http://localhost:3002/api/speak_text"    # 話者B

SPEAKER_ID_A = 2
SPEAKER_ID_B = 1
SPEECH_SPEED_SCALE = 1.3  # 話すアクションの速度倍率

# =================== アニメーション関数のインポート ===================
def play_dual_animation(speaking_speaker: str, wait_duration: int):
    """
    話す人と喋ってない人で別々のアニメーションを同時再生

    Args:
        speaking_speaker (str): 話している話者 "A" または "B"
        wait_duration (int): 再生待機時間(秒)
    """
    # 話す人のアニメーション: talkアニメーションからランダム選択
    speaking_speaker_talk_anim = random.choice(TALK_ANIMATIONS)

    # 喋ってない人のアニメーション: danceアニメーションからランダム選択またはidle
    if speaking_speaker == "A":
        non_speaking_speaker = "B"
        speaking_url = f"{ANIMATION_BASE_URL_A}{ANIMATION_ENDPOINT}"
        non_speaking_url = f"{ANIMATION_BASE_URL_B}{ANIMATION_ENDPOINT}"
    else:
        non_speaking_speaker = "A"
        speaking_url = f"{ANIMATION_BASE_URL_B}{ANIMATION_ENDPOINT}"
        non_speaking_url = f"{ANIMATION_BASE_URL_A}{ANIMATION_ENDPOINT}"

    non_speaking_dance_anim = random.choice(DANCE_ANIMATIONS + [IDLE_ANIMATION])

    def play_single_animation(url, speaker, anim_path):
        """単一キャラクターのアニメーション再生"""
        try:
            payload = {"animation": anim_path}
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)

            if response.status_code == 200:
                print(f"✅ [{speaker}] アニメーション開始: {anim_path}")
            else:
                print(f"❌ [{speaker}] アニメーションエラー: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ [{speaker}] アニメーションエラー: {e}")

    print(f"🎬 同時アニメーション再生開始 - 話者[{speaking_speaker}]:{speaking_speaker_talk_anim} / 話者[{non_speaking_speaker}]:{non_speaking_dance_anim}")

    # 両方のアニメーションを同時に開始
    play_single_animation(speaking_url, speaking_speaker, speaking_speaker_talk_anim)
    play_single_animation(non_speaking_url, non_speaking_speaker, non_speaking_dance_anim)

    # 再生待機
    for _ in tqdm(range(wait_duration), desc="並行アニメーション再生", unit="秒", ncols=60):
        time.sleep(1)

    print(f"✅ 同時アニメーション完了")


# =================== タイムライン（release notes内容）===================
script = [
    # Slides 1-4: タイトル & 導入
    {
        "type": "talk",
        "speaker": "A",
        "text": "こんにちは！本日は『OSS自作マルチモーダルデヴィン、ジェミニアクションズラボ』をご紹介します。"
    },
    {
        "type": "action",
        "name": "press_right"
    },
    {
        "type": "talk",
        "speaker": "B",
        "text": "コーディングは好きでも、リポジトリ設定やドキュメント修正って、ちょっと面倒ですよね。"
    },
    {
        "type": "talk",
        "speaker": "A",
        "text": "そうなんです！今回は、そんな創造的ではない定型タスクをAIに任せてしまおう、というお話です。"
    },
    {
        "type": "action",
        "name": "press_right"
    },

    # Slides 5-6: コンセプト
    {
        "type": "talk",
        "speaker": "B",
        "text": "なるほど！面倒な作業はAIにお願いするだけというわけですね！"
    },
    {
        "type": "talk",
        "speaker": "A",
        "text": "その通り！ディスコードで『これやっておいて』と会話するだけで、AIエージェントが自律的にタスクを実行してくれます。"
    },
    {
        "type": "action",
        "name": "press_right"
    },

    # Slides 7-8: 技術概要とデモの見どころ
    {
        "type": "talk",
        "speaker": "B",
        "text": "裏側ではジェミニ2.5 Proと、画像生成AIのイメージェン4が連携しているんですね！"
    },
    {
        "type": "talk",
        "speaker": "A",
        "text": "はい！この後の動画では、その実力がわかる3つのタスク…① リポジトリ作成、② コード修正、そして③ AI画像付きリリースノート生成を実演します。"
    },
    {
        "type": "action",
        "name": "press_right"
    },

    # Slides 9-10: デモ開始
    {
        "type": "talk",
        "speaker": "B",
        "text": "それは楽しみです！"
    },
    {
        "type": "talk",
        "speaker": "A",
        "text": "それではご覧ください。『ジェミニアクションズラボ』の実際の動作デモンストレーションです。"
    }
]


# =================== メイン処理 ===================
def main():
    print("🚀 AgentVRM v0.4.0 Release Notes ポッドキャスト解説")
    print("=" * 70)
    print("🎭 各スライドを順次解説します")
    print("🎤 話すアクション → ページ送りアクション → ...")
    print("🎬 同時アニメーション有効")
    print("=" * 70)

    os.makedirs("assets", exist_ok=True)

    # ===== 実行開始前のカウントダウン =====
    initial_delay = 5
    for _ in tqdm(range(initial_delay), desc="開始まで", unit="秒"):
        time.sleep(1)

    global talk_index
    talk_index = 0

    for step_i, step in enumerate(script, start=1):
        if step.get("type") == "action":
            name = step.get("name")
            if name == "press_right":
                if pyautogui is None:
                    print(f"[{step_i}] action press_right スキップ（PyAutoGUI未使用）")
                else:
                    try:
                        pyautogui.press('right')
                        print(f"[{step_i}] ページ送り（→）を実行しました。")
                    except Exception as e:
                        print(f"[{step_i}] ページ送りに失敗: {e}", file=sys.stderr)
                    # ページ送り後の待機
                    time.sleep(0.5)
            else:
                print(f"[{step_i}] 未対応のaction: {name}")
            continue

        # talk イベント
        speaker = step.get("speaker")
        text = step.get("text", "")

        if speaker == "A":
            api_url = API_URL_A
            speaker_id = SPEAKER_ID_A
            animation_url = ANIMATION_BASE_URL_A
            file_prefix = "A"
        else:
            api_url = API_URL_B
            speaker_id = SPEAKER_ID_B
            animation_url = ANIMATION_BASE_URL_B
            file_prefix = "B"

        payload = {
            "text": text,
            "speakerId": speaker_id,
            "speedScale": SPEECH_SPEED_SCALE
        }

        talk_index += 1
        print(f"\n{'='*40} ステップ {step_i} {'='*40}")
        print(f"🎤 [{speaker}] 解説開始: {text}")
        print(f"🎬 アニメーション: 自動トークアニメーション")

        # === [2] 音声合成開始 ===
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
        output_path = f"assets/release_notes_{file_prefix}_{talk_index}.wav"
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        print(f"✅ [{step_i}] 音声ファイルを{output_path}として保存しました。")

        # 音声の長さ分だけ待機して進行
        with wave.open(output_path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            duration = frames / float(rate)

        speech_duration = int(duration + 0.5)
        print(f"[{step_i}] 音声の長さ: {duration:.2f}秒")
        print(f"[{step_i}] {speech_duration:.2f}秒待機して次へ...")

        # === [3] 同時アニメーション再生 ===
        print(f"⏸️  [{speaker}] 音声再生中（同時アニメーション実行）... ({speech_duration:.2f}秒)")

        # アニメーション再生時間を音声長さに合わせる
        anim_duration = speech_duration

        # スレッドで同時アニメーション実行
        anim_thread = threading.Thread(
            target=play_dual_animation,
            args=(speaker, anim_duration)
        )
        anim_thread.start()

        # 音声再生待機
        for _ in tqdm(range(speech_duration), desc=f"[{speaker}] 音声+アニメ", unit="秒", ncols=60):
            time.sleep(1)

        # アニメーション終了を待つ
        anim_thread.join()

        print(f"✅ [{step_i}] 解説完了")

    print("\n" + "=" * 60)
    print("💡 使い方の注意:")
    print("- リソースノートのHTMLをブラウザで開いてください")
    print("- アニメーションファイルは public/anim/ ディレクトリに配置してください")
    print("- pyautoguiにより自動でページ送りが実行されます")
    print("- 生成された音声ファイルは assets/ ディレクトリに保存されます")
    print("- 話者A/Bのポート (3001/3002) が起動していることを確認してください")
    print("=" * 60)

if __name__ == "__main__":
    main()
