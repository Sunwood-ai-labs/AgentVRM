#!/usr/bin/env python3
"""
AgentVRMアニメーション再生API サンプルスクリプト

このスクリプトは /api/play_animation エンドポイントを使って
VRMモデルにアニメーションを再生する例です。

使用方法:
1. AgentVRMサービスが起動している状態で実行します
2. アニメーションファイルは public/ ディレクトリに配置されている必要があります

前提条件:
- AgentVRMサービスが http://localhost:3002 で起動中
- requests, tqdmライブラリがインストール済み
- public/ ディレクトリに vrma または fbx アニメーションファイルがある
"""

import json
import requests
import time
from tqdm import tqdm

# 設定
API_BASE_URL = "http://localhost:3002"  # AgentVRMのURL
API_ENDPOINT = "/api/play_animation"

def play_animation(animation_path: str, play_duration: int = 5):
    """
    アニメーションを再生する

    Args:
        animation_path (str): public/ ディレクトリからの相対パス
                             例: "/idle_loop.vrma", "/walk.fbx"
        play_duration (int): 再生時間を待機する秒数（プログレスバー表示用）
    """
    url = f"{API_BASE_URL}{API_ENDPOINT}"

    # POSTデータ
    payload = {
        "animation": animation_path
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # APIリクエスト送信
        response = requests.post(url, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功: {result.get('message', 'アニメーション再生指示を送信しました')}")
            print(f"  アニメーション: {animation_path}")

            # 再生中のプログレスバー表示
            print(f"\n⏯️  アニメーション再生中... ({play_duration}秒)")
            for _ in tqdm(range(play_duration), desc="再生時間", unit="秒", ncols=70):
                time.sleep(1)
            print("✅ アニメーション完了\n")

        else:
            print(f"❌ エラー: HTTP {response.status_code}")
            print(f"   レスポンス: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ リクエストエラー: {e}")
    except Exception as e:
        print(f"❌ その他のエラー: {e}")

def main():
    print("🎬 AgentVRM アニメーション再生API サンプル")
    print("=" * 50)

    # VRMAアニメーション再生例
    print("\n1. VRMAアニメーション再生")
    play_animation("/idle_loop.vrma")

    print("\n2. FBXアニメーション再生 - Old Man Idle")
    play_animation("/anim/Old Man Idle.fbx")

    print("\n3. FBXアニメーション再生 - Samba Dancing")
    play_animation("/anim/Samba Dancing.fbx")

    print("\n" + "=" * 50)
    print("💡 使い方の注意:")
    print("- アニメーションファイルは public/ ディレクトリに配置してください")
    print("- サポートする形式: .vrma, .fbx")
    print("- FBXファイルはMixamo形式を想定しています")
    print("- ブラウザでAgentVRMを開き、VRMモデルが読み込まれていることを確認してください")

if __name__ == "__main__":
    main()
