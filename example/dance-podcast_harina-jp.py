#!/usr/bin/env python3
"""
HARINA v3 ポッドキャスト形式スライド解説スクリプト（日本語）

このスクリプトは example/assets/HARINA-v3.md の内容に合わせて、
HARINA v3 のスライドを二人の話者（A/B）が交互に解説します。
音声合成と同時にアニメーションを再生し、pyautoguiでページ送りします。

実行フロー:
- 各スライドで話者A/Bが交互に要点を解説
- 解説中はトーク＋ダンス/アイドルの同時アニメーション
- 解説後に右矢印キーで次スライドへ

使用方法:
1. AgentVRMサービス（ポート3001/3002）が起動している状態で実行
2. HARINA v3 のスライドをブラウザで開いておく
3. アニメーションファイルは public/anim/ に配置

前提条件:
- http://localhost:3001, http://localhost:3002 が利用可能
- requests, tqdm, pyautogui がインストール済み
- public/anim/ に fbx などのアニメーションがある
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
    "/anim/Talking3.fbx",
    "/anim/Talking4.fbx",
]

DANCE_ANIMATIONS = [
    "/anim/Samba Dancing.fbx",
    "/anim/Swing Dancing.fbx",
    "/anim/Wave Hip Hop Dance.fbx",
    "/anim/Chicken Dance.fbx",
    "/anim/Locking Hip Hop Dance.fbx",
    "/anim/Snake Hip Hop Dance.fbx",
    "/anim/Step Hip Hop Dance.fbx",
    "/anim/Tut Hip Hop Dance.fbx",
]

# アイドルは複数化（ランダム選択しやすく）
IDLE_ANIMATIONS = [
    "/anim/Breathing Idle.fbx"
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

    non_speaking_dance_anim = random.choice(DANCE_ANIMATIONS + IDLE_ANIMATIONS)

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


# =================== タイムライン（HARINA v3 スライド内容）===================
# 出典: example/assets/HARINA-v3.md
script = [
    # Slide 1: タイトル
    {"type": "talk", "speaker": "A", "text": "こんにちは！本日は『ハリナブイスリー：ワンスナップで家計簿完成』をご紹介します。"},
    {"type": "talk", "speaker": "B", "text": "発表はまき、日付は2025年9月14日。最新バージョンの全体像をお届けします。"},
    {"type": "action", "name": "press_right"},

    # Slide 2: アジェンダ
    {"type": "talk", "speaker": "A", "text": "本日の流れは、課題と解決策、ビルドプロセス、技術スタック、デモ、主要機能、インパクト、そして次の一歩です。"},
    {"type": "action", "name": "press_right"},

    # Slide 3: オープニング
    {"type": "talk", "speaker": "B", "text": "まずはオープニング。ハリナブイスリーの着想とゴールを簡単に整理します。"},
    {"type": "action", "name": "press_right"},

    # Slide 4: コンセプト
    {"type": "talk", "speaker": "A", "text": "ワンスナップ、ユアレジャーイズダン。レシートを一枚撮るだけで帳簿化まで。"},
    {"type": "talk", "speaker": "B", "text": "ジェミニ・ジーピーティーフォーオー・クロードを切り替え可能、オープンソースで無料運用も可能です。"},
    {"type": "action", "name": "press_right"},

    # Slide 5: 見出し（Problem & Solution）
    {"type": "talk", "speaker": "A", "text": "次に課題と解決策を見ていきましょう。"},
    {"type": "action", "name": "press_right"},

    # Slide 6: 課題と解決
    {"type": "talk", "speaker": "B", "text": "課題は3つ。手入力の手間、夫婦やパートナー間の共有の難しさ、入力ミスによる家計崩れ。"},
    {"type": "talk", "speaker": "A", "text": "解決はエーアイ自動化。写真一枚から必要情報を抽出し、複数エーアイで柔軟に、ジェミニなら実質ゼロコスト運用。"},
    {"type": "action", "name": "press_right"},

    # Slide 7: 見出し（Build Process）
    {"type": "talk", "speaker": "B", "text": "続いて、ビルドプロセス。会話駆動で進化していきました。"},
    {"type": "action", "name": "press_right"},

    # Slide 8: Kiro主導の開発プロセス
    {"type": "talk", "speaker": "A", "text": "最初はサンプルスクリプト。次にファストエイピーアイとシーエルアイで扱いやすくし、最終的にディービー付きのウェブアプリへ。"},
    {"type": "talk", "speaker": "B", "text": "ハイライトは複数ファイル同時処理。アップロード、進捗、エラー処理まで前後分離で一括生成されました。"},
    {"type": "action", "name": "press_right"},

    # Slide 9: 見出し（Tech Stack）
    {"type": "talk", "speaker": "A", "text": "テックスタックを見ていきます。"},
    {"type": "action", "name": "press_right"},

    # Slide 10: モダンなフルスタック
    {"type": "talk", "speaker": "B", "text": "フロントはネクストジェイエスプラスタイプスクリプトプラステイルウィンド。会話からユーアイまで自動生成。"},
    {"type": "talk", "speaker": "A", "text": "バックエンドはファストエイピーアイプラスパイソンプラスライトエルエルエム。データはポストグレエスキューエル、ドッカーコンポーズで手軽に起動。"},
    {"type": "action", "name": "press_right"},

    # Slide 11: 見出し（Live Demo）
    {"type": "talk", "speaker": "B", "text": "ここからライブデモの見どころ。"},
    {"type": "action", "name": "press_right"},

    # Slide 12: 直感的UIと即時インサイト
    {"type": "talk", "speaker": "A", "text": "ドラッグアンドドロップで複数レシートを同時処理。進捗をリアルタイム表示してくれます。"},
    {"type": "talk", "speaker": "B", "text": "ダッシュボードでカテゴリ別やペア向け統計を表示。和のテイストで見やすく。また、処理したレシートは後から見返すこともできます！"},
    {"type": "action", "name": "press_right"},

    # Slide 13: 見出し（Key Features）
    {"type": "talk", "speaker": "A", "text": "主要機能をまとめます。"},
    {"type": "action", "name": "press_right"},

    # Slide 14: 柔軟性・自由・ゼロコスト
    {"type": "talk", "speaker": "B", "text": "ワンクリックでエーアイを切替。ジェミニで月数百枚のレシートも無料運用可能。"},
    {"type": "talk", "speaker": "A", "text": "エムアイティーのオーエスエスとしてギットハブで公開。セルフホスト・改変・再配布も自由です。"},
    {"type": "action", "name": "press_right"},

    # Slide 15: 見出し（Impact）
    {"type": "talk", "speaker": "B", "text": "インパクトを一言で。"},
    {"type": "action", "name": "press_right"},

    # Slide 16: 単なるアプリに留まらない
    {"type": "talk", "speaker": "A", "text": "会話駆動開発の実証であり、日々の家計管理の実用品。"},
    {"type": "talk", "speaker": "B", "text": "同時に最新フルスタックプラスエルエルエム連携の学習リソースとしても役立ちます。"},
    {"type": "action", "name": "press_right"},

    # Slide 17: 見出し（Next Steps）
    {"type": "talk", "speaker": "A", "text": "今後のロードマップです。"},
    {"type": "action", "name": "press_right"},

    # Slide 18: 次の一歩
    {"type": "talk", "speaker": "B", "text": "モバイル対応、より高度なエーアイ、多言語化、そしてコミュニティ拡大。"},
    {"type": "talk", "speaker": "A", "text": "ギットハブの『ハリナブイスリーウェブユーアイ』で、ぜひ参加・フォークしてください。"},
    {"type": "action", "name": "press_right"},

    # Slide 19: クロージング
    {"type": "talk", "speaker": "B", "text": "ご清聴ありがとうございました！まきより。"}
]


# =================== メイン処理 ===================
def main():
    print("🚀 HARINA v3 スライド ポッドキャスト解説（日本語）")
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
        output_path = f"assets/harina_{file_prefix}_{talk_index}.wav"
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
    print("- HARINA v3 のスライドをブラウザで開いてください")
    print("- アニメーションファイルは public/anim/ ディレクトリに配置してください")
    print("- pyautoguiにより自動でページ送りが実行されます")
    print("- 生成された音声ファイルは assets/ ディレクトリに保存されます")
    print("- 話者A/Bのポート (3001/3002) が起動していることを確認してください")
    print("=" * 60)

if __name__ == "__main__":
    main()
