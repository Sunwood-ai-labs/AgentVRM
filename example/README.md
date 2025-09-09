# 🎤 ChatVRM Pythonサンプル集

このディレクトリは、ChatVRMと連携する各種Pythonサンプル・音声ファイル・実行手順をまとめたものです。

---

## 📁 ディレクトリ構成

```
example/
├── anim/
│   ├── Old Man Idle.fbx
│   └── Samba Dancing.fbx
├── assets/
│   ├── out.wav
│   ├── output_voicevox.wav
│   ├── output_speak_text_1.wav
│   ├── output_speak_text_2.wav
│   ├── output_speak_text_3.wav
│   ├── podcast_anim_A_1.wav
│   ├── podcast_anim_B_1.wav
│   └── sample-talk01.wav
├── play_animation_api_sample.py
├── play_animation_podcast_sample.py
├── podcast_simulation.py
├── speak_text_api_sample.py
├── speak_text_conversation_sample.py
├── voicevox_api_sample.py
├── voicevox_tts_sample.py
├── ws_audio_sender.py
├── pyproject.toml
└── README.md
```

- `assets/` … 音声ファイルの格納場所（全サンプル共通で利用）

---

## 📝 サンプルスクリプト一覧と用途

| ファイル名                        | 用途・説明 |
|-----------------------------------|-----------|
| `play_animation_api_sample.py`    | VRMアニメーション再生APIの使用例（VRMA/FBXアニメーションの再生） |
| `play_animation_podcast_sample.py` | **新規**：ポッドキャスト会話中にアニメーションを連動再生（アニメーション＋音声の融合） |
| `podcast_simulation.py`           | ポッドキャスト風会話のシミュレーション（音声生成＋ページ送りアクション） |
| `speak_text_api_sample.py`        | テキストをPOSTするだけでVRMキャラクターがVOICEVOX音声で喋る（最もシンプル） |
| `speak_text_conversation_sample.py` | 3回分のテキストを順に喋らせ、音声ファイルを保存・会話時間分待機・loguruで見やすいログ（レスポンスはキーのみ表示）|
| `voicevox_api_sample.py`          | テキスト→音声ファイル生成→WebSocket送信でVRMが喋る（音声ファイルも保存） |
| `voicevox_tts_sample.py`          | テキスト→音声ファイル生成のみ（WebSocket送信なし） |
| `ws_audio_sender.py`              | 任意のWAVファイルをWebSocket経由で送信しVRMに喋らせる |
| `post_audio_sample.py`            | 任意のWAVファイルをAPI経由で送信し、レスポンスを保存するサンプル |

---

## 🚀 実行手順

### 1. 依存パッケージのインストール

- WebSocketサーバー用（Node.jsプロジェクトルートで実行）:

  ```
  npm install ws
  ```

- Python用（サンプル実行前に）:

  ```
  pip install requests websocket-client loguru
  ```

### 2. WebSocketサーバーの起動

```
node server/ws-server.js
```
- `ws://localhost:8080` で待ち受けます

### 3. ChatVRMのWebアプリを起動

```
npm run dev
```
- ブラウザでアクセス

### 4. サンプルの実行例

- VRMキャラクターにアニメーションを再生:

  ```
  python play_animation_api_sample.py
  ```

- **ポッドキャスト会話中にアニメーションを連動再生（新規）**:

  ```
  python play_animation_podcast_sample.py
  ```

- ポッドキャスト風会話のシミュレーション:

  ```
  python podcast_simulation.py
  ```

- VRMキャラクターにテキストだけで喋らせる（推奨）:

  ```
  python speak_text_api_sample.py
  ```

- 3回分の会話を連続で喋らせ、音声ファイル保存・会話時間分待機・loguruで見やすいログ（レスポンスはキーのみ表示）:

  ```
  python speak_text_conversation_sample.py
  ```

- 音声ファイル生成＋WebSocket送信:

  ```
  python voicevox_api_sample.py
  ```

- 任意のWAVファイルをWebSocket送信:

  ```
  python ws_audio_sender.py
  ```

---

## ✨ `speak_text_conversation_sample.py` の特徴

- 3回分のテキストを順に `/api/speak_text` へ送信し、各レスポンスの音声データを `assets/output_speak_text_1.wav` などに保存
- 保存したwavファイルの長さ（秒）を自動計算し、その時間だけ待機して次の会話へ進行
- サーバーレスポンスはバイナリや長い値を出さず、キーのみをloguruで見やすく表示
- 進行状況・エラーもloguruで整形
- 依存パッケージ: `loguru`, `requests`

---

## 🎭 `play_animation_podcast_sample.py` の特徴

- **アクション別実行方式**: 話すアクションとアニメーション変化を完全に分離し、独立して順次実行
- **同時アニメーション機能**: 話すアクション中は自動で豊富なアニメーションを同時再生
  - 話す人: Talkアニメーション（Talking1.fbx〜Talking3.fbx）をランダム選択
  - 喋ってない人: Danceアニメーション（Samba Dancing, Swing Dancing, Wave Hip Hop Dance）をランダム選択
- **視覚的に豊かな表現**: ため息やジェスチャーも一旦考えるほど奥行きのあるパフォーマンス
- **カスタムアニメーション設定可能**: 各アクションで特定のアニメーションを指定可能（VRMA/FBX形式）
- **プログレスバー表示**: アニメーションおよび音声再生の進行状況を視覚化
- **生成音声自動保存**: `assets/podcast_anim_{A|B}_{番号}.wav`形式で保存
- **依存パッケージ**: `requests`, `tqdm`, `random`, `threading`

---

## ℹ️ 備考

- 音声ファイルはすべて `assets/` ディレクトリに格納してください。
- `server/ws-server.js` は package.json の scripts には含まれていません。直接 `node server/ws-server.js` で起動してください。
- 複数クライアントが接続している場合、全てのクライアントに音声がブロードキャストされます。
- サンプルごとに用途が異なるため、目的に応じて使い分けてください。
