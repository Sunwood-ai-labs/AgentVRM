<div align="center">

![](https://github.com/user-attachments/assets/9627b73a-3b5b-4a20-bafa-4a2a69a31ab0)

# AgentVRM

</div>

<p align="center">
  <a href="https://nextjs.org/" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js"></a>
  <a href="https://react.dev/" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React"></a>
  <a href="https://www.typescriptlang.org/" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript"></a>
  <a href="https://threejs.org/" target="_blank" rel="noopener noreferrer"><img src="https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=three.js&logoColor=white" alt="Three.js"></a>
</p>


> [!NOTE]
> AgentVRMは、外部Agent（Roo-Code、ClaudeCodeなど）による制御専用のVRM表示システムです。
> 

本プロジェクトは[pixiv/ChatVRM](https://github.com/pixiv/ChatVRM)をベースに、外部プログラムからのVRM制御に特化したシステムとして開発されています。

AgentVRMはブラウザで3DキャラクターをAgent制御で動作させるためのプラットフォームです。VRMファイルをインポートし、外部プログラムから音声制御を行うことができます。

---

## ✨ 機能

AgentVRMの各機能は主に以下の技術を使用しています。

- **🔊 音声合成・再生**: [VOICEVOX Engine](https://voicevox.hiroshiba.jp/)

> [!TIP]
> 🐳 **docker-composeでVOICEVOXエンジンのURLを指定するには？**
>
> `docker-compose.yml` の `environment` セクションで `VOICEVOX_ENGINE_URL` を設定できます。
> 例:
>
> ```yaml
> services:
---

## .env ファイルによる環境変数の一元管理

プロジェクトルートに `.env` ファイルを作成し、下記のように記載してください。

```
VOICEVOX_ENGINE_URL=http://voicevox_engine:50021
```

各種 docker-compose ファイルでは、下記のように `${VOICEVOX_ENGINE_URL}` で参照します。

```yaml
environment:
  - VOICEVOX_ENGINE_URL=${VOICEVOX_ENGINE_URL}
```

`.env` ファイルを使うことで、環境ごとに値を切り替えたり、複数 compose ファイル連結時も一元管理できます。

---

## 複数の docker-compose ファイルを連結して実行する方法

Voicevox Engine（CPU版またはGPU版）と他サービス（Next.js など）を同時に起動する場合は、`docker-compose -f` オプションで複数の compose ファイルを連結して実行してください。

### 例: CPU版 Voicevox Engine + Next.js サービス

```sh
docker-compose -f docker-compose.cpu.yml -f docker-compose.yml up
```

### 例: GPU版 Voicevox Engine + Next.js サービス

```sh
docker-compose -f docker-compose.gpu.yml -f docker-compose.yml up
```

### 例: CPU版 Voicevox Engine + Podcast用サービス

```sh
docker-compose -f docker-compose.cpu.yml -f docker-compose.podcast.yml up
```

### 注意
- `VOICEVOX_ENGINE_URL` などの環境変数は、Next.js サービス側の compose ファイルに記載されています。
- 必要に応じて `-d` オプションでバックグラウンド起動も可能です。

---
>   nextjs:
>     environment:
>       - VOICEVOX_ENGINE_URL=http://voicevox_engine:50021
> ```
>
> デフォルト値は `.env` または `.env.example` で `http://localhost:50021` です。
> Docker環境では `http://voicevox_engine:50021` を指定してください。
- **🤖 3Dキャラクター表示**: [@pixiv/three-vrm](https://github.com/pixiv/three-vrm)
- **📡 外部制御通信**: WebSocket + REST API
- **🐍 Agent制御**: Python制御サンプル

## 🎯 Agent制御機能

### 主要機能

- **📡 WebSocket音声配信**: リアルタイムでVRMキャラクターに音声を送信
- **🎯 テキスト発話API**: 外部からテキストを送信してVRMを喋らせる
- **📁 音声ファイル送信**: WAV/MP3ファイルを直接アップロードして再生
- **🐍 Python制御サンプル**: `example/`フォルダに豊富なサンプルコード
- **🎭 VRMファイル対応**: 任意のVRMファイルをドラッグ&ドロップで変更可能

## 🚀 セットアップ

### 1. リポジトリクローン

```bash
git clone https://github.com/Sunwood-ai-labs/AgentVRM.git
cd AgentVRM
```

### 2. 依存関係インストール

```bash
npm install
```

### 3. VOICEVOX Engineセットアップ

```bash
# DockerでVOICEVOXエンジンを起動
docker run --rm -p 50021:50021 voicevox_engine
```

### 4. 環境変数設定

```bash
cp .env.example .env
```

`.env`ファイルの内容：
```bash
# WebSocketサーバーのURL
NEXT_PUBLIC_WS_URL=ws://localhost:8080

# VOICEVOXエンジンのURL
VOICEVOX_ENGINE_URL=http://localhost:50021

# 初期モーションのファイル名（publicディレクトリからのパス、.vrmaまたは.fbx）
# NEXT_PUBLIC_MOTION_FILENAME=/anim/Breathing Idle.fbx
```

### 5. WebSocketサーバー起動

```bash
node server/ws-server.js
```

### 6. Webアプリケーション起動

```bash
npm run dev
```

ブラウザで [http://localhost:3000](http://localhost:3000) にアクセスして動作確認してください。

---

## 🔧 Agent制御方法

### 1. テキスト発話API（推奨）

最もシンプルな制御方法。テキストを送信するだけでVRMが喋ります。

```python
import requests

# VRMキャラクターにテキストを喋らせる
response = requests.post("http://localhost:3000/api/speak_text", json={
    "text": "外部プログラムから制御されています！",
    "speakerId": 1,      # VOICEVOX話者ID（省略可）
    "speedScale": 1.0    # 話速（省略可）
})

print(response.json())
```

### 2. 音声ファイル送信

WAVやMP3ファイルを直接WebSocket経由で送信してVRMに再生させることができます。

```python
import websocket

def send_audio_file(file_path):
    ws = websocket.create_connection("ws://localhost:8080")
    with open(file_path, "rb") as f:
        audio_data = f.read()
        ws.send(audio_data, opcode=websocket.ABNF.OPCODE_BINARY)
    ws.close()

# 使用例
send_audio_file("path/to/your/audio.wav")
```

### 3. VOICEVOX直接制御

VOICEVOX APIを使用して音声合成とWebSocket送信を分離して制御することも可能です。

```python
import requests
import base64
import websocket

# 音声合成
response = requests.post("http://localhost:3000/api/voicevox_tts", json={
    "text": "VOICEVOX APIで合成しました",
    "speakerId": 1,
    "speedScale": 1.0
})

# WebSocket送信
data = response.json()
audio_base64 = data["audio"].split(",")[1]
audio_bytes = base64.b64decode(audio_base64)

ws = websocket.create_connection("ws://localhost:8080")
ws.send(audio_bytes, opcode=websocket.ABNF.OPCODE_BINARY)
ws.close()
```

## 📝 サンプルコード

`example/`ディレクトリにPython制御サンプルが含まれています：

| ファイル名 | 説明 |
|-----------|------|
| `speak_text_api_sample.py` | テキスト発話APIの基本的な使用例 |
| `speak_text_conversation_sample.py` | 連続発話制御（ログ出力・待機処理含む） |
| `voicevox_api_sample.py` | VOICEVOX API + WebSocket送信の例 |
| `voicevox_tts_sample.py` | VOICEVOX音声合成のみのサンプル |
| `ws_audio_sender.py` | 音声ファイルをWebSocket送信するサンプル |

### サンプル実行

```bash
# Python依存関係のインストール
pip install requests websocket-client loguru

# サンプル実行（WebSocketサーバーとWebアプリが起動済みであること）
cd example
python speak_text_api_sample.py
```

## 🔧 API仕様

### POST /api/speak_text

VRMキャラクターにテキストを喋らせる

**リクエスト**:
```json
{
  "text": "喋らせたいテキスト",
  "speakerId": 1,     // VOICEVOX話者ID（省略可、デフォルト: 1）
  "speedScale": 1.0   // 話速（省略可、デフォルト: 1.0）
}
```

**レスポンス**:
```json
{
  "status": "ok",
  "message": "VRMに発話指示を送信しました",
  "audio": "data:audio/wav;base64,..."
}
```

### POST /api/voicevox_tts

VOICEVOX APIで音声合成のみを行う

**リクエスト**:
```json
{
  "text": "合成するテキスト",
  "speakerId": 1,
  "speedScale": 1.0
}
```

**レスポンス**:
```json
{
  "audio": "data:audio/wav;base64,..."
}
```

### POST /api/speak_external_audio

外部音声ファイルを再生する

**リクエスト**: バイナリ音声データ（WAV/MP3）  
**レスポンス**: 同じ音声データをエコーバック

### WebSocket ws://localhost:8080

音声バイナリデータのリアルタイム送受信

- バイナリデータ（WAV、MP3等）を送信すると、接続中の全クライアントにブロードキャスト
- VRMキャラクターがリアルタイムで音声を再生

## 🐳 Docker環境

Docker Composeを使用した環境構築：

```bash
docker-compose up
```

これにより、WebアプリとWebSocketサーバーが同時に起動します。

## 📋 システム要件

- **Node.js**: 16.14.2以上
- **Python**: 3.7以上（制御スクリプト使用時）
- **VOICEVOX Engine**: Docker環境推奨

## 🚨 トラブルシューティング

### VRMが喋らない場合

1. WebSocketサーバー起動確認: `node server/ws-server.js`
2. VOICEVOXエンジン起動確認: `curl http://localhost:50021/docs`
3. ブラウザでWebアプリにアクセスし、音声権限を許可

### Agent制御が動作しない場合

1. 全サービス起動確認:
   - Webアプリ: http://localhost:3000
   - WebSocketサーバー: ws://localhost:8080
   - VOICEVOXエンジン: http://localhost:50021

2. ファイアウォール確認: ポート3000, 8080, 50021の開放

3. Python依存関係確認:
   ```bash
   pip install requests websocket-client loguru
   ```

## 🎭 VRMファイル変更

- ブラウザのWebアプリで「VRMを開く」ボタンからファイル選択
- または、VRMファイルをブラウザ画面にドラッグ&ドロップ

## 🔧 詳細設定

### VOICEVOX話者ID

VOICEVOX Engineで利用可能な話者IDを確認：
```bash
curl http://localhost:50021/speakers
```

### WebSocketサーバー設定

`server/ws-server.js`で以下の環境変数を設定可能：
- `WS_PORT`: WebSocketポート（デフォルト: 8080）
- `WS_HOST`: WebSocketホスト（デフォルト: 0.0.0.0）

## 🤝 関連プロジェクト

- **ベースプロジェクト**: [pixiv/ChatVRM](https://github.com/pixiv/ChatVRM)
- **VOICEVOX**: [voicevox.hiroshiba.jp](https://voicevox.hiroshiba.jp/)

## 📄 ライセンス

本プロジェクトはベースプロジェクトのライセンスに従います。

## 複数の docker-compose ファイルを連結して実行する方法

Voicevox Engine（CPU版またはGPU版）と他サービス（Next.js など）を同時に起動する場合は、`docker-compose -f` オプションで複数の compose ファイルを連結して実行してください。

### 例: CPU版 Voicevox Engine + Next.js サービス

```sh
docker-compose -f docker-compose.cpu.yml -f docker-compose.yml up
```

### 例: GPU版 Voicevox Engine + Next.js サービス

```sh
docker-compose -f docker-compose.gpu.yml -f docker-compose.yml up
```

### 例: CPU版 Voicevox Engine + Podcast用サービス

```sh
docker-compose -f docker-compose.cpu.yml -f docker-compose.podcast.yml up
```

### 注意
- `VOICEVOX_ENGINE_URL` などの環境変数は、Next.js サービス側の compose ファイルに記載されています。
- 必要に応じて `-d` オプションでバックグラウンド起動も可能です。

## .env ファイルによる環境変数の一元管理

プロジェクトルートに `.env` ファイルを作成し、下記のように記載してください。

```
VOICEVOX_ENGINE_URL=http://voicevox_engine:50021
```

各種 docker-compose ファイルでは、下記のように `${VOICEVOX_ENGINE_URL}` で参照します。

```yaml
environment:
  - VOICEVOX_ENGINE_URL=${VOICEVOX_ENGINE_URL}
```

`.env` ファイルを使うことで、環境ごとに値を切り替えたり、複数 compose ファイル連結時も一元管理できます。
