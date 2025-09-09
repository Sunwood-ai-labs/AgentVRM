#!/usr/bin/env python3
"""
AgentVRM アニメーション + 音声合成 アクション別実行サンプルスクリプト

このスクリプトは話すアクションとアニメーション変化を完全に分離し、
各アクションを独立して順次実行します。

実行フロー:
1. [話者A] 話すアクション
2. [話者A] 話すアクション
3. [話者A] アニメーション変化アクション
4. [話者B] 話すアクション
等

使用方法:
1. AgentVRMサービスが起動している状態で実行します
2. アニメーションファイルは public/ ディレクトリに配置されている必要があります

前提条件:
- AgentVRMサービスが http://localhost:3001 と http://localhost:3002 で起動中
- requests, tqdm ライブラリがインストール済み
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

IDLE_ANIMATION = "/anim/Old Man Idle.fbx"

# =================== ポッドキャスト設定 ===================
API_URL_A = "http://localhost:3001/api/speak_text"      # 話者A
API_URL_B = "http://localhost:3002/api/speak_text"    # 話者B

SPEAKER_ID_A = 2
SPEAKER_ID_B = 1

# =================== アニメーション関数 ===================
# =================== 同時アニメーション関数 ===================
def play_dual_animation(speaking_speaker: str, wait_duration: int):
    """
    話す人と喋ってない人で別々のアニメーションを同時再生

    Args:
        speaking_speaker (str): 話している話者 "A" または "B"
        wait_duration (int): 再生待機時間（秒）
    """
    # 話す人のアニメーション: talkアニメーションからランダム選択
    speaking_speaker_talk_anim = random.choice(TALK_ANIMATIONS)

    # 喋ってない人のアニメーション: danceアニメーションからランダム選択
    if speaking_speaker == "A":
        non_speaking_speaker = "B"
        speaking_url = f"{ANIMATION_BASE_URL_A}{ANIMATION_ENDPOINT}"
        non_speaking_url = f"{ANIMATION_BASE_URL_B}{ANIMATION_ENDPOINT}"
    else:
        non_speaking_speaker = "A"
        speaking_url = f"{ANIMATION_BASE_URL_B}{ANIMATION_ENDPOINT}"
        non_speaking_url = f"{ANIMATION_BASE_URL_A}{ANIMATION_ENDPOINT}"

    non_speaking_dance_anim = random.choice(DANCE_ANIMATIONS)

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

def play_single_animation(url: str, animation_path: str, description: str = ""):
    """
    単一キャラクターのアニメーション再生

    Args:
        url (str): アニメーションAPIエンドポイントURL
        animation_path (str): アニメーション相対パス
        description (str): 説明文
        wait_duration (int): 再生待機時間（秒）
    """
    payload = {"animation": animation_path}
    headers = {"Content-Type": "application/json"}

    try:
        print(f"🎬 [{description}] アニメーション再生開始: {animation_path}")
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ [{description}] アニメーション開始: {result.get('message', '再生中')}")
        else:
            print(f"❌ [{description}] アニメーションエラー: HTTP {response.status_code}")

        # # 再生待機
        # for _ in tqdm(range(wait_duration), desc=f"[{description}] アニメーション", unit="秒", ncols=60):
        #     time.sleep(1)

    except requests.exceptions.RequestException as e:
        print(f"❌ [{description}] アニメーションリクエストエラー: {e}")
    except Exception as e:
        print(f"❌ [{description}] アニメーションエラー: {e}")

# =================== アクションシーケンス（話す・アニメーションを独立したアクションに）===================
# 注意：話すアクション中は同時アニメーションが自動再生されます
actions = [
    # ===== 話者Aの挨拶 =====
    {
        "type": "speak",
        "speaker": "A",
        "text": "みなさん、こんにちは！",
        "output_filename": "A_001"
    },
    {
        "type": "speak",
        "speaker": "A",
        "text": "ポッドキャストへようこそ。",
        "output_filename": "A_002"
    },
    {
        "type": "animation",
        "animation_path": "/idle_loop.vrma",
        "description": "挨拶時のアニメーション"
    },

    # ===== 話者Bの応答 =====
    {
        "type": "speak",
        "speaker": "B",
        "text": "こんにちは、Aさん。",
        "output_filename": "B_001"
    },
    {
        "type": "speak",
        "speaker": "B",
        "text": "今日はどんな話題ですか？",
        "output_filename": "B_002"
    },
    {
        "type": "animation",
        "animation_path": "/anim/Samba Dancing.fbx",
        "description": "質問時のアニメーション"
    },

    # ===== 話者Aの話題紹介 =====
    {
        "type": "speak",
        "speaker": "A",
        "text": "今日はAIと音声合成について話しましょう。",
        "output_filename": "A_003"
    },
    {
        "type": "animation",
        "animation_path": "/anim/Old Man Idle.fbx",
        "description": "話題紹介時のアニメーション"
    },

    # ===== 話者Bの感想 =====
    {
        "type": "speak",
        "speaker": "B",
        "text": "面白そうですね！",
        "output_filename": "B_003"
    },
    {
        "type": "speak",
        "speaker": "B",
        "text": "最近のAIは本当にすごいです。",
        "output_filename": "B_004"
    },
    {
        "type": "animation",
        "animation_path": "/anim/Wave Hip Hop Dance.fbx",
        "description": "感想表明時のダンスアニメーション"
    },

    # ===== 話者Aの締めくくり =====
    {
        "type": "speak",
        "speaker": "A",
        "text": "そうですね。",
        "output_filename": "A_004"
    },
    {
        "type": "speak",
        "speaker": "A",
        "text": "リスナーのみなさんもぜひ体験してみてください。",
        "output_filename": "A_005"
    },

    # ===== 話者Bの挨拶 =====
    {
        "type": "speak",
        "speaker": "B",
        "text": "それでは、また次回お会いしましょう！",
        "output_filename": "B_005"
    },
    {
        "type": "speak",
        "speaker": "B",
        "text": "ありがとうございました。",
        "output_filename": "B_006"
    },
    {
        "type": "animation",
        "animation_path": "/idle_loop.vrma",
        "description": "締めくくりのアニメーション"
    },
]

# =================== 実行設定 ===================
SPEECH_SPEED_SCALE = 1.3  # 話すアクションの速度倍率

# =================== メイン処理 ===================
def main():
    print("🎭 AgentVRM アニメーション + 音声合成 アクション別実行サンプル")
    print("=" * 70)
    print("📋 各アクションを独立して順次実行します")
    print("🎤 話すアクション → アニメーション変化アクション → 話すアクション...")
    print("=" * 70)

    os.makedirs("assets", exist_ok=True)

    # ===== アクション単独実行 =====
    global_file_counter = 1

    for i, action in enumerate(actions):
        print(f"\n{'='*40} アクション {i+1} {'='*40}")

        if action["type"] == "speak":
            # ============ 話すアクション ============
            speaker = action["speaker"]
            text = action["text"]
            output_filename = action.get("output_filename", f"auto_{global_file_counter}")

            if speaker == "A":
                api_url = API_URL_A
                speaker_id = SPEAKER_ID_A
            else:
                api_url = API_URL_B
                speaker_id = SPEAKER_ID_B

            output_path = f"assets/podcast_anim_{output_filename}.wav"

            print(f"🎤 [アクション{i+1}] 話す（同時アニメーション有効）: [{speaker}] {text}")

            try:
                # === [1] 音声合成開始 ===
                payload = {
                    "text": text,
                    "speakerId": speaker_id,
                    "speedScale": SPEECH_SPEED_SCALE
                }

                response = requests.post(api_url, json=payload)
                response.raise_for_status()
                data = response.json()

                # 音声データ保存
                audio_data_uri = data["audio"]
                m = re.match(r"data:audio/wav;base64,(.*)", audio_data_uri)
                if not m:
                    raise ValueError("audioフィールドが想定外の形式です")

                audio_base64 = m.group(1)
                audio_bytes = base64.b64decode(audio_base64)

                with open(output_path, "wb") as f:
                    f.write(audio_bytes)

                print(f"✅ [アクション{i+1}] 音声ファイルを{output_path}として保存しました。")

                # 音声情報取得
                with wave.open(output_path, "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)

                # === [2] 同時アニメーション再生 ===
                print(f"⏸️  [{speaker}] 音声再生中（同時アニメーション実行）... ({duration:.2f}秒)")
                speech_duration = int(duration + 1)

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

            except Exception as e:
                print(f"❌ [アクション{i+1}] 話すアクションエラー: {e}")

            global_file_counter += 1

        elif action["type"] == "animation":
            # ============ アニメーションアクション ============
            animation_path = action["animation_path"]
            description = action.get("description", "アニメーション")

            print(f"🎬 [アクション{i+1}] アニメーション変化: {description}")
            print(f"  アニメーション: {animation_path}")

            # 全キャラクターの共通アニメーションとして再生（より強制的な制御が可能）
            if animation_path.endswith('.fbx'):
                # 全キャラクター共通アニメーションとして再生
                play_single_animation(ANIMATION_BASE_URL_A, animation_path, f"A_{description}")
            else:
                # VRMAの場合も同様
                play_single_animation(ANIMATION_BASE_URL_A, animation_path, f"A_{description}")

            print(f"✅ [アクション{i+1}] アニメーション完了: {description}")

        else:
            print(f"⚠️  [アクション{i+1}] 不明なアクションタイプ: {action['type']}")

    print("\n" + "=" * 60)
    print("💡 使い方の注意:")
    print("- アニメーションファイルは public/ ディレクトリに配置してください")
    print("- サポートする形式: .vrma, .fbx")
    print("- FBXファイルはMixamo形式を想定しています")
    print("- ブラウザでAgentVRMを開き、VRMモデルが読み込まれていることを確認してください")
    print("- 生成された音声ファイルは assets/ ディレクトリに保存されます")

if __name__ == "__main__":
    main()
