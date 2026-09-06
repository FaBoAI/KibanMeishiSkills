# KibanMeishiSkills

EasyEDAでNFC基板名刺を設計し、JLCPCBのMulticolor SilkscreenとPCBA向けにデータを準備するCodex Skillです。ST25TN01K-AFH5を用いた名刺制作の知見を収録しています。

## 使い方

`kiban-meishi` フォルダを `~/.codex/skills/` に配置し、Codexから次のように指定します。

```text
$kiban-meishi ST25TN01K-AFH5、青0603 LED、抵抗の構成で、
厚さ0.6 mm・四隅R2・表面カラー印刷のNFC名刺を20枚設計し、発注データを準備して。
```

入口は [SKILL.md](kiban-meishi/SKILL.md)。ライブ操作にはEasyEDAと接続用API／ブラウザ操作環境、発注にはJLCPCBアカウントが必要です。ドキュメントの参照とCSV／ZIP検査スクリプトは単独でも利用できます。

## 収録内容

- 最小構成の部品候補、入力素材、設計・検証に必要な道具
- RFアンテナとLED負荷、抵抗値の計算と実測の区別
- EasyEDAのネットリスト・属性・DRC・角丸外形の扱い
- カラーGerber、BOM、CPLとJLCPCBの照合・見積・引き継ぎ
- Python標準ライブラリだけで使える入稿データの形式検査

これは量産保証済みの回路・Gerber配布ではありません。2026-09-06の事例では62Ωでの点灯とiPhoneでの動作がユーザーから報告されましたが、今回の100Ω・独自アンテナ版の実機評価結果は未収録です。決済画面や注文一覧への遷移から支払完了を推定していません。
