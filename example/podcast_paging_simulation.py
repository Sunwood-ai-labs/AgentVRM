import requests
import base64
import re
import wave
import time
import os
import sys

try:
    import pyautogui
except Exception as e:
    pyautogui = None
    print(f"[warn] PyAutoGUI unavailable: {e}", file=sys.stderr)
try:
    from tqdm import tqdm
except Exception:
    tqdm = None

# エンドポイント設定（docker-compose.podcast.yml と合わせる）
API_URL_A = "http://localhost:3001/api/speak_text"      # 話者A
API_URL_B = "http://localhost:3002/api/speak_text"      # 話者B

# 話者設定
SPEAKER_ID_A = 2
SPEAKER_ID_B = 1
SPEED_SCALE = 1.3

# タイムライン（talk と action を別イベントとして並べる）
# 必要な場所だけ action を入れてページ送りします。
script=[
    # Slide1: タイトル
    {"type":"talk","speaker":"A","text":"みなさん、こんにちは！サンウッドエーアイラボのポッドキャストへようこそ。きょうのテーマは『じさくデビンでぜんいんがエンジニアに』です。"},
    {"type":"talk","speaker":"B","text":"こんにちは。タイトルからしておもしろそうですね！ぜんいんがエンジニアになるってどういうことなんですか？"},
    {"type":"talk","speaker":"A","text":"これからスライドにそって、かだい・しくみ・ぎじゅつ・つぎのステップをわかりやすくおはなしします。"},
    {"type":"action","name":"press_right"},

    # Slide2: 目次
    {"type":"talk","speaker":"A","text":"まずはアジェンダです。ながれは、かだいとビジョン、しくみとデモ、ぎじゅつとインパクト、つぎのステップ、まとめ です。"},
    {"type":"talk","speaker":"B","text":"なるほど、しっかりしたロードマップですね。それではかだいから！"},
    {"type":"action","name":"press_right"},

    # Slide3: かだいとビジョン
    {"type":"talk","speaker":"A","text":"いまのかいはつげんばでは、イシューやプルリクがふえすぎて、たいしょしきれないんです。"},
    {"type":"talk","speaker":"B","text":"たしかに、やることがたまってしまって、たいせつなタスクをみのがすこともありますよね。"},
    {"type":"action","name":"press_right"},

    # Slide4: プロダクト名
    {"type":"talk","speaker":"A","text":"そこで『ジェミニアクションズラボ ― じさくデビン』。ひエンジニアでもしぜんげんごでアイデアをかたちにできるように せっけいされています。"},
    {"type":"talk","speaker":"B","text":"コードがかけないひとでもアイデアをすぐかたちにできるってことですね！"},
    {"type":"action","name":"press_right"},

    # Slide5: げんばのなやみ
    {"type":"talk","speaker":"A","text":"さらに、アイデアはあるけどコードにできない、かいはつフローにさんかしにくい、そんなハードルがあります。"},
    {"type":"talk","speaker":"B","text":"わかります。そういうとき、“じさくデビン”がいればスムーズにつなげそうですね。"},
    {"type":"action","name":"press_right"},

    # Slide6: しくみとデモ
    {"type":"talk","speaker":"A","text":"しくみはシンプルです。ディスコードにひとことなげるだけで、AIがイシューかやレビューをじどうでおこないます。"},
    {"type":"talk","speaker":"B","text":"それならアイデアがでたしゅんかんに、すぐアクションにつながりますね。"},
    {"type":"action","name":"press_right"},

    # Slide9: ワークフローしょうさい
    {"type":"talk","speaker":"A","text":"フローはこうです。ディスコード→デビンボット→ギットハブアクションズ→ジェミニエーアイ。しかもオープンソースなのでワークフローやプロンプトはじゆうにカスタムできます。"},
    {"type":"talk","speaker":"B","text":"つまり、じぶんのチームにあわせてかいぞうできるってことですね？"},
    {"type":"talk","speaker":"A","text":"そのとおりです。にーずにあわせたフローをつくれるのがつよみです。"},
    {"type":"action","name":"press_right"},

    # Slide10: ぎじゅつとインパクト
    {"type":"talk","speaker":"A","text":"ここからはぎじゅつてきな うらがわとインパクトについて。"},
    {"type":"talk","speaker":"B","text":"どこまでじどうでできるのか、きになります！"},
    {"type":"action","name":"press_right"},

    # Slide11: デビンボットのどうさ
    {"type":"talk","speaker":"A","text":"たとえば ユーザーが『しんきのうをついかして』とメッセージすると、デビンボットがすぐにギットハブにイシューをつくります。"},
    {"type":"talk","speaker":"B","text":"すごい！にんげんがやってたらじかんのかかるしごとを、一しゅんで。"},
    {"type":"action","name":"press_right"},

    # Slide12: エーオーエヌ／ぎじゅつスタック
    {"type":"talk","speaker":"A","text":"さらに エーオーエヌ というフレームワークで、AIのこうどうをにんげんがよみやすいレポートにまとめます。ボットはパイソンせいで、ギットハブエーピーアイとれんけい。ジェミニ シーエルアイとアクションズのつうごうで、じどうレビューまでできます。"},
    {"type":"talk","speaker":"B","text":"なるほど。しごとがみえるかされて、レビューもやりやすくなるわけですね。"},
    {"type":"action","name":"press_right"},

    # Slide13: つぎのステップ
    {"type":"talk","speaker":"A","text":"つぎのステップは、きょういくとオープンソースへのおうようです。"},
    {"type":"talk","speaker":"B","text":"がくしゅうのツールとしてつかえば、だれでもじっせんてきに かいはつにさんかできますね。"},
    {"type":"action","name":"press_right"},

    # Slide14: さんかモデルのてんかん
    {"type":"talk","speaker":"A","text":"そうなんです。コミュニティにとりいれれば、“みるひと”から“つくるひと”へやくわりがシームレスにうつれます。"},
    {"type":"talk","speaker":"B","text":"これまで きゃくかんしゃ だったひとも、きょうどうしゃになれる、ってことか！"},
    {"type":"action","name":"press_right"},

    # Slide15: まとめ
    {"type":"talk","speaker":"A","text":"まとめると、はっそうからかいはつまでのさいたんきょりをうみだし、ひエンジニアのさんかでげんばをつよくします。"},
    {"type":"talk","speaker":"B","text":"たしかに、アイデアをむだにせず、すぐにかたちにできるのはおおきなちからです。"},
    {"type":"action","name":"press_right"},

    # Slide16: キャッチコピー
    {"type":"talk","speaker":"A","text":"キャッチコピーは『じさくデビンで、ぜんいんがエンジニアになる。』"},
    {"type":"talk","speaker":"B","text":"シンプルでわかりやすいメッセージですね。"},
    {"type":"action","name":"press_right"},

    # Slide17: おといあわせ
    {"type":"talk","speaker":"A","text":"しょうさいやデモしょうたいのごきぼうは、マキ@サンウッドエーアイラボまで。"},
    {"type":"talk","speaker":"B","text":"どうにゅうそうだんやカスタムのそうだんも、きがるにできるんですね。"},
    {"type":"action","name":"press_right"},

    # Slide18: サンクユー
    {"type":"talk","speaker":"A","text":"さいごまでおききいただき、ありがとうございました。『じさくデビン』で、つぎのいっぽをいっしょにふみだしましょう。"},
    {"type":"talk","speaker":"B","text":"それではまたじかい！"}
]


assets_dir = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(assets_dir, exist_ok=True)

# 実行開始前のカウントダウン（デフォルト5秒）をtqdmで表示
initial_delay = int(os.environ.get("PODCAST_INITIAL_DELAY", "5"))
if initial_delay > 0:
    if tqdm is None:
        print(f"開始まで {initial_delay} 秒待機...")
        time.sleep(initial_delay)
    else:
        for _ in tqdm(range(initial_delay), desc="開始まで", unit="s"):
            time.sleep(1)

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
        else:
            print(f"[{step_i}] 未対応のaction: {name}")
        # action では待機しないで次へ
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
        "speedScale": SPEED_SCALE
    }

    talk_index += 1
    print(f"[{step_i}] {speaker} → APIリクエスト: {text}")
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
    output_path = os.path.join(assets_dir, f"podcast_{file_prefix}_{talk_index}.wav")
    with open(output_path, "wb") as f:
        f.write(audio_bytes)
    print(f"[{step_i}] 音声ファイルを{output_path}として保存しました。")

    # 音声の長さ分だけ待機して進行
    with wave.open(output_path, "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    print(f"[{step_i}] 音声の長さ: {duration:.2f}秒")
    print(f"[{step_i}] {duration:.2f}秒待機して次へ...")
    time.sleep(duration)
