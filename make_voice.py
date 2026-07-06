#!/usr/bin/env python3
# ============================================================
# VOICEVOXで音声ガイドのファイルを一括生成するスクリプト
#
# 使い方:
#   1. VOICEVOXアプリを起動しておく（起動しているだけでOK）
#   2. ルーティンアプリの「🎙 音声データ用テキストを書き出す」で
#      voice-texts.json をダウンロードし、このファイルと同じフォルダに置く
#   3. ターミナルでこのフォルダに移動して:
#        python3 make_voice.py
#
#   話者を変えたいとき（番号を付けて実行）:
#        python3 make_voice.py 22
#   話者の番号一覧を見る:
#        python3 make_voice.py list
#
# よく使う番号: 3=ずんだもん(ノーマル) 22=ずんだもん(ささやき・夜向き)
#               2=四国めたん(ノーマル) 8=春日部つむぎ
# ============================================================
import json
import sys
import pathlib
import urllib.parse
import urllib.request

ENGINE = "http://127.0.0.1:50021"
SPEAKER = 3  # 初期値: ずんだもん(ノーマル)


def api_post(path, body=None):
    req = urllib.request.Request(ENGINE + path, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def list_speakers():
    with urllib.request.urlopen(ENGINE + "/speakers", timeout=10) as r:
        for sp in json.load(r):
            for st in sp["styles"]:
                print(f'{st["id"]:>4}  {sp["name"]}（{st["name"]}）')


def main():
    global SPEAKER
    if len(sys.argv) > 1:
        if sys.argv[1] == "list":
            list_speakers()
            return
        SPEAKER = int(sys.argv[1])

    here = pathlib.Path(__file__).parent
    src = here / "voice-texts.json"
    if not src.exists():
        print("voice-texts.json が見つかりません。")
        print("アプリの「🎙 音声データ用テキストを書き出す」でダウンロードして、このフォルダに置いてください。")
        return

    texts = json.loads(src.read_text(encoding="utf-8"))
    outdir = here / "voice"
    outdir.mkdir(exist_ok=True)

    manifest = {}
    for i, text in enumerate(texts, 1):
        query = api_post(f"/audio_query?speaker={SPEAKER}&text=" + urllib.parse.quote(text))
        wav = api_post(f"/synthesis?speaker={SPEAKER}", query)
        name = f"v{i:03d}.wav"
        (outdir / name).write_bytes(wav)
        manifest[text] = "voice/" + name
        label = text if len(text) <= 24 else text[:24] + "…"
        print(f"({i}/{len(texts)}) {label}")

    (outdir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"\n完了！ {len(texts)}件の音声を voice/ フォルダに生成しました。")
    print("アプリを再読み込みすると、ホームのボタンが「🎧 音声ガイド ON（VOICEVOX）」に変わります。")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError:
        print("VOICEVOXに接続できませんでした。VOICEVOXアプリを起動してから、もう一度実行してください。")
