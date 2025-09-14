#!/usr/bin/env python3
"""
HARINA v3 ポッドキャスト形式スライド解説スクリプト（カタカナ英語）

example/dance-podcast_harina-jp.py をベースに、
TTSが読み上げる talk の text をカタカナ英語に置き換えています。
ネイティブにも聞き取りやすいよう、語切り（・）やカンマでポーズを追加し、
長音・小文字を使って英語寄りの発音になるよう調整しています。

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
API_URL_B = "http://localhost:3002/api/speak_text"      # 話者B

SPEAKER_ID_A = 2
SPEAKER_ID_B = 1

# 英語寄りの聞き取りやすさ重視で少しゆっくりめ
SPEECH_SPEED_SCALE = 1.0


# =================== アニメーション関数 ===================
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
        try:
            payload = {"animation": anim_path}
            response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)

            if response.status_code == 200:
                print(f"✅ [{speaker}] アニメーション開始: {anim_path}")
            else:
                print(f"❌ [{speaker}] アニメーションエラー: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ [{speaker}] アニメーションエラー: {e}")

    print(
        f"🎬 同時アニメーション再生開始 - 話者[{speaking_speaker}]:{speaking_speaker_talk_anim} / "
        f"話者[{non_speaking_speaker}]:{non_speaking_dance_anim}"
    )

    # 両方のアニメーションを同時に開始
    play_single_animation(speaking_url, speaking_speaker, speaking_speaker_talk_anim)
    play_single_animation(non_speaking_url, non_speaking_speaker, non_speaking_dance_anim)

    # 再生待機
    for _ in tqdm(range(wait_duration), desc="並行アニメーション再生", unit="秒", ncols=60):
        time.sleep(1)

    print("✅ 同時アニメーション完了")


# =================== タイムライン（HARINA v3 スライド内容）===================
# 出典: example/assets/HARINA-v3.md を英語要旨に変換し、カタカナ英語で掲載
script = [
    # Slide 1: タイトル
    {"type": "talk", "speaker": "A", "text": "ハロー！ トゥデイ、ウィア・プリゼンティング『ハリナ・ブイ・スリー：ワン・スナップ、ユア・レジャー・イズ・ダン』。"},
    {"type": "talk", "speaker": "B", "text": "プレゼンター・イズ・マキ。デイト・イズ・トゥー・サウザンド・トゥエンティ・ファイヴ、セプテンバー・フォーティーン。レイテスト・バージョン・オーバービュー。"},
    {"type": "action", "name": "press_right"},

    # Slide 2: アジェンダ
    {"type": "talk", "speaker": "A", "text": "トゥデイズ・アジェンダ：プロブレムズ・アンド・ソリューションズ、ビルド・プロセス、テック・スタック、デモ、キー・フィーチャーズ、インパクト、ネクスト・ステップス。"},
    {"type": "action", "name": "press_right"},

    # Slide 3: オープニング
    {"type": "talk", "speaker": "B", "text": "ファースト、オープニング。ハリナ・ブイ・スリー・ビジョン・アンド・ゴールズ、ブリーフ・オーバービュー。"},
    {"type": "action", "name": "press_right"},

    # Slide 4: コンセプト
    {"type": "talk", "speaker": "A", "text": "ワン・スナップ、ユア・レジャー・イズ・ダン。ジャスト・ワン・レシート・フォト・フォー・フル・ブックキーピング。"},
    {"type": "talk", "speaker": "B", "text": "ジェミニ、ジー・ピー・ティー・フォー・オー、クロード、スイッチャブル。オープン・ソース・エネーブルズ・ゼロ・コスト・ラン。"},
    {"type": "action", "name": "press_right"},

    # Slide 5: 見出し（Problem & Solution）
    {"type": "talk", "speaker": "A", "text": "ネクスト、プロブレムズ・アンド・ソリューションズ。"},
    {"type": "action", "name": "press_right"},

    # Slide 6: 課題と解決
    {"type": "talk", "speaker": "B", "text": "スリー・メイン・プロブレムズ：マニュアル・エントリー・ワーク、カップル・オア・パートナー・シェア・ディフィカルティ、アンド・データ・エントリー・エラーズ・リード・トゥ・バジェット・ブレイク。"},
    {"type": "talk", "speaker": "A", "text": "ソリューション・イズ・エーアイ・オートメーション。ワン・フォト・トゥ・エクストラクト・ニーデッド・インフォ。マルチ・エーアイ・フォー・フレキシビリティ。ジェミニ・ミーンズ・プラクティカリー・ゼロ・コスト。"},
    {"type": "action", "name": "press_right"},

    # Slide 7: 見出し（Build Process）
    {"type": "talk", "speaker": "B", "text": "ムービング・オン、ビルド・プロセス。コンバセーション・ドリブン・エボリューション。"},
    {"type": "action", "name": "press_right"},

    # Slide 8: Kiro主導の開発プロセス
    {"type": "talk", "speaker": "A", "text": "スターテッド・ウィズ・サンプル・スクリプト。ゼン、ファスト・エーピーアイ・アンド・シー・エル・アイ・メイク・イット・イージアー。ファイナリー、データベース・バックド・ウェブ・アプリ。"},
    {"type": "talk", "speaker": "B", "text": "ハイライト：マルチファイル・パラレル・プロセッシング。アップロード、プログレス、エラー・ハンドリング、オール・オート・ジェネレーテッド、フロント／バック・セパレーテッド。"},
    {"type": "action", "name": "press_right"},

    # Slide 9: 見出し（Tech Stack）
    {"type": "talk", "speaker": "A", "text": "レッツ・チェック・ザ・テック・スタック。"},
    {"type": "action", "name": "press_right"},

    # Slide 10: モダンなフルスタック
    {"type": "talk", "speaker": "B", "text": "フロントエンド：ネクスト・ジェイエス、タイプスクリプト、テイルウィンド。コンバセーション・トゥ・ユーアイ、オート・ジェネレーテッド。"},
    {"type": "talk", "speaker": "A", "text": "バックエンド：ファスト・エーピーアイ、パイソン、ライト・エルエルエム。データ：ポストグレ・エスキューエル。ドッカー・コンポーズ・フォー・クイック・スタート。"},
    {"type": "action", "name": "press_right"},

    # Slide 11: 見出し（Live Demo）
    {"type": "talk", "speaker": "B", "text": "ネクスト、ライブ・デモ・ハイライト。"},
    {"type": "action", "name": "press_right"},

    # Slide 12: 直感的UIと即時インサイト
    {"type": "talk", "speaker": "A", "text": "ドラッグ・アンド・ドロップ・マルチ・レシート、パラレル・プロセッシング。プログレス、リアルタイム・ディスプレイ。"},
    {"type": "talk", "speaker": "B", "text": "ダッシュボード、ショウズ・バイ・カテゴリ、アンド・カップル・スタッツ。ジャパニーズ・スタイル、イージー・トゥ・リード。プロセスト・レシート、リビュー・レーター、オーケー！"},
    {"type": "action", "name": "press_right"},

    # Slide 13: 見出し（Key Features）
    {"type": "talk", "speaker": "A", "text": "サマライズ・キー・フィーチャーズ。"},
    {"type": "action", "name": "press_right"},

    # Slide 14: 柔軟性・自由・ゼロコスト
    {"type": "talk", "speaker": "B", "text": "ワン・クリック・エーアイ・スイッチ。ジェミニ・レッツ・ユー・ラン・ハンドレッズ・パー・マンス・フォー・フリー。"},
    {"type": "talk", "speaker": "A", "text": "エム・アイ・ティー・オープン・ソース、オン・ギットハブ。セルフ・ホスト、モディファイ、リディストリビュート、フリー。"},
    {"type": "action", "name": "press_right"},

    # Slide 15: 見出し（Impact）
    {"type": "talk", "speaker": "B", "text": "インパクト、イン・ワン・フレーズ。"},
    {"type": "action", "name": "press_right"},

    # Slide 16: 単なるアプリに留まらない
    {"type": "talk", "speaker": "A", "text": "プルーフ・オブ・コンセプト・フォー・コンバセーション・ドリブン・デベロップメント、アンド・プラクティカル・ツール・フォー・デイリー・バジェット。"},
    {"type": "talk", "speaker": "B", "text": "オルソー、ラーニング・リソース・フォー・モダン・フルスタック・プラス・エルエルエム・インテグレーション。"},
    {"type": "action", "name": "press_right"},

    # Slide 17: 見出し（Next Steps）
    {"type": "talk", "speaker": "A", "text": "ヒアズ・ザ・ロードマップ。"},
    {"type": "action", "name": "press_right"},

    # Slide 18: 次の一歩
    {"type": "talk", "speaker": "B", "text": "モバイル・サポート、モア・アドバンスト・エーアイ、マルチリンガル、アンド・コミュニティ・グロース。"},
    {"type": "talk", "speaker": "A", "text": "オン・ギットハブ『ハリナ・ブイ・スリー・ウェブ・ユー・アイ』、プリーズ・ジョイン・アンド・フォーク！"},
    {"type": "action", "name": "press_right"},

    # Slide 19: クロージング
    {"type": "talk", "speaker": "B", "text": "サンキュー・フォー・リスニング！フロム・マキ。"}
]


# =================== メイン処理 ===================
def main():
    print("🚀 HARINA v3 スライド ポッドキャスト解説（カタカナ英語）")
    print("=" * 70)
    print("🎭 各スライドを順次解説します")
    print("🎤 カタカナ英語で話す → ページ送り → ...")
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
            file_prefix = "A"
        else:
            api_url = API_URL_B
            speaker_id = SPEAKER_ID_B
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

        # === 音声合成 ===
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
        output_path = f"assets/harina_kata_{file_prefix}_{talk_index}.wav"
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

        # === 同時アニメーション再生 ===
        print(f"⏸️  [{speaker}] 音声再生中（同時アニメーション実行）... ({speech_duration:.2f}秒)")

        anim_duration = speech_duration

        anim_thread = threading.Thread(
            target=play_dual_animation,
            args=(speaker, anim_duration)
        )
        anim_thread.start()

        for _ in tqdm(range(speech_duration), desc=f"[{speaker}] 音声+アニメ", unit="秒", ncols=60):
            time.sleep(1)

        anim_thread.join()

        print(f"✅ [{step_i}] 解説完了")

    print("\n" + "=" * 60)
    print("💡 使い方の注意:")
    print("- スライドをブラウザで開いてください")
    print("- アニメーションファイルは public/anim/ に配置してください")
    print("- pyautogui により自動でページ送りします")
    print("- 生成音声は assets/ に保存されます（ファイル名: harina_kata_*.wav）")
    print("- 話者A/Bのポート (3001/3002) が起動していることを確認してください")
    print("=" * 60)


if __name__ == "__main__":
    main()
