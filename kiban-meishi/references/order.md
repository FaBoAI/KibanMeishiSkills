# Multicolor Silkscreen・PCBA入稿

## 同一リビジョンのデータを揃える

|ファイル|確認内容|
|---|---|
|カラーGerber ZIP|銅箔、穴、R2外形、カラー専用データが同じ最新版|
|BOM CSV|D1/R1/U1の記号・品番・数量。旧抵抗が残らない|
|CPL CSV|記号、中心座標、表裏、回転。拡張子`.csv`も確認|
|ネイティブ設計|回路図とPCBの関連付け、画像、積層、ライブラリ参照|
|確認記録|DRC残存理由、部品照合、配置プレビュー、未検証項目|

EasyEDAのCSV出力がUTF-16・タブ区切りとなる場合はCSVパーサで読み、UTF-8 BOM付きカンマ区切りへ変換する。文字列の単純なタブ置換では、部品名中のカンマ等を壊す。CPLの座標符号・単位・回転を勝手に反転しない。製造プレビューでパッドと部品を確認する。

```bash
python3 scripts/check_order_files.py --bom BOM.csv --cpl CPL.csv --gerber Color.zip
python3 scripts/check_order_files.py --bom BOM.csv --cpl CPL.csv --gerber Color.zip --normalized-dir normalized
```

このスクリプトは形式と記号一致を検査する。サイズ・極性・在庫・DRCを検証するものではない。

## カラー製造ファイル

[公式のカラーシルク手順](https://jlcpcb.com/help/article/how-to-design-multi-color-silkscreen-using-easyeda)と現在の注文画面を確認する。原画を表面カラーシルクオブジェクトとして保持する。原画の縦横比と基板比率が違う場合は、引き伸ばし、トリミング、余白のどれかを意識的に選び、文字の歪みを確認する。

画面からの成功手順（EasyEDA v3.2.148の事例）:

1. 正しいPCBを開き、Export → PCB Fabrication File (Gerber)。
2. `Generate colorful silkscreen fabrication file (Only for JLCPCB)`を選択。
3. 最新版名でExport Gerber。説明ダイアログの`I Got it, Continue`を選択。
4. 保存先・ファイル名を確定。保存ボタンが無効なら入力確定や未完了のダイアログを確認。
5. ZIP整合性、外形、`Fabrication_ColorfulTopSilkscreen.FCTS`、`Fabrication_ColorfulBoardOutlineLayer.FCBO`等を確認。

通常Gerberにカラー画像を添えただけでは専用データの代用にならない。古いFCTS/FCBOを新しい銅箔ZIPへ混ぜない。APIがundefined/nullでも、正しい画面の直接出力で成功する場合がある。権限不足と断定する前に対象文書と確認ダイアログを調べる。

## JLCPCB設定

- ログイン後に見積が初期化されたことがある。ファイル名・解析寸法・全設定を確認して必要なら再入稿する。
- 通常のSilkscreen色だけでなく、Advanced Options → Silkscreen Technology → **EasyEDA multi-color silkscreen**を選ぶ。カラーGerberを上げただけで自動設定されるとは限らない。
- この事例は白、ENIG、1 oz、0.6 mm、基板20枚・Top Side実装20枚。0.6 mmがHASL設定で無効なら対応する表面処理を選ぶ。仕様の組み合わせと価格は現在の画面を優先する。
- 白を緑に変更する提案は、カラー印刷仕様を優先して断った。自動提案をユーザーの指定より優先しない。
- 0.6 mmでEconomicが無効となりStandard PCBAを使用した。これを全ての将来のサービス条件へ一般化しない。
- JLCPCB追加のEdge Rails/Fiducialsにより見積寸法が変わる。完成名刺91 × 55 mmと製造パネルを区別する。本例の画面は91 × 71 mmだが説明文に両側5 mmとあり整合しなかったため、最終パネル図で確認する。完成基板の寸法をその値へ書き換えない。
- `Depanel boards & edge rail before delivery = Yes`で、捨て板を除去して納品する構成を選んだ。必要な加工費として見積に含める。

## BOM/CPLと見積

Bill of MaterialsでAdd BOM File、Add CPL File、Process BOM & CPL。各行の型番、パッケージ、数量、選択状態を確認する。ユーザーが「PCL」と呼んだ場合も、Pick-and-PlaceのCPLを指す文脈ならそのファイルを扱う。

2026-09-06の例では3部品全て照合され、D1は28個、R1は30個（実装20枚＋予備）、U1はMy Partsの20個が選ばれた。My Partsを一般在庫と報告しない。割当可能数・保管状態・ロス数が確認できなければ未確認と記録する。

Component Placementsで3部品のパッド位置・面・回転・極性を確認し、Quote & Orderへ進む。原画の印刷方向と角丸も確認する。3Dモデルが見えたことだけでピン1やLED極性が合格したとは断定しない。

価格の事例は基板$21.33＋Standard PCBA $48.03＝$69.36。送料・税を含む支払総額ではなく、ICがMy Partsという条件付きの過去見積。見積画面の一時的な$0.00を確定額として使わない。

カート・チェックアウト・支払完了は別の状態。ユーザーがブラウザを引き取ったら停止する。ログインセッションを残す必要があれば対象タブを保持し、ログイン情報の公開や転記をしない。注文一覧へ移動しただけでは、支払済み／製造開始と断定しない。
