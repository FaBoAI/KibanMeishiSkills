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

## 注文画面への入力と確認

ユーザーから発注準備・発注操作を依頼されたら、操作可能なブラウザで以下の入力まで実施する。リンクや入力方法を説明するだけで完了としない。ユーザーが自分で入力すると指定した場合は、その時点で操作を引き継ぐ。

|画面の項目|本Skillの標準入力|確認方法|
|---|---|---|
|Gerber|同一リビジョンのカラーGerber ZIP|ファイル名と解析された基板寸法|
|PCB Qty|ユーザー指定。本例20枚|数量表示が20|
|PCB Color|White|選択状態を確認。白→緑の提案を自動承諾しない|
|Surface Finish|ENIG|選択状態を確認|
|PCB Thickness|**0.6mm**|選択状態を確認。入力不可なら対応する表面処理を先に選ぶ|
|Outer Copper Weight|1 oz|選択状態を確認|
|Advanced Options → Silkscreen Technology|**EasyEDA multi-color silkscreen**|選択状態と見積への反映を確認|
|PCB Assembly / PCBA Type|有効化し、対応する方式。本例Standard|0.6 mmでEconomicが選択できなければStandardを使用|
|Assembly Side / PCBA Qty|Top Side / ユーザー指定。本例20枚|基板枚数とは別に実装枚数を確認|
|Edge Rails/Fiducials|Added by JLCPCB|製造パネルと完成基板の寸法を区別|
|Depanel boards & edge rail before delivery|Yes|捨て板を除去した完成名刺での納品を確認|

ユーザーが明示した値を優先する。上記の対応可否・追加料金は現行画面で確認する。0.6 mmを選べないからといって無断で1.6 mm等へ変えない。

実際の操作順序:

1. ログイン状態を確認し、最新カラーGerberをアップロードする。解析完了を待ってから、寸法と層数を確認する。処理中の設定は解析完了時に初期化される場合がある。
2. 数量・White・ENIGを設定し、0.6mmを選択する。0.6 mmがHASL設定で無効なら表面処理の対応条件を確認する。
3. PCB側のAdvanced Optionsを展開し、Silkscreen TechnologyでEasyEDA multi-color silkscreenを選ぶ。通常のSilkscreen欄のBlack/Whiteだけではカラー印刷指定にならない。カラーGerberだけで自動設定されるとも限らない。
4. PCB Assemblyを有効化し、実装方式・面・枚数・捨て板除去を設定する。非同期更新が落ち着いてから、0.6 mm・カラー印刷・数量が維持されていることを確認する。フォーカス表示やクリック成功を選択済みの証拠とせず、選択状態・チェック状態・見積への反映を見る。
5. ログインなどで画面が再読み込みされたら、アップロードと設定が保持されているか確認し、消えていれば再入力する。重複注文を作成しない。
6. BOM/CPLの部品照合、実装プレビュー、Quote & Orderまで進め、基板代・部品代・実装代・必要な加工費を確認する。チェックアウト時は送料・税を含む総額で確認する。

操作が使えない、ログイン待ち、サイトが要求仕様に対応しない等の場合は、完了した項目と未完了の項目を分け、具体的な障害を伝える。規約同意・購入・決済はその環境の実行ルールとユーザー承認に従い、入力完了と発注完了を区別する。

JLCPCB追加のEdge Rails/Fiducialsにより見積寸法が変わる。本例は完成名刺91 × 55 mmに対して画面表示91 × 71 mmとなった一方、説明文に両側5 mmとあり整合しなかったため、最終パネル図で確認する。完成基板の寸法をその値へ書き換えない。

## BOM/CPLと見積

Bill of MaterialsでAdd BOM File、Add CPL File、Process BOM & CPL。各行の型番、パッケージ、数量、選択状態を確認する。ユーザーが「PCL」と呼んだ場合も、Pick-and-PlaceのCPLを指す文脈ならそのファイルを扱う。

2026-09-06の例では3部品全て照合され、D1は28個、R1は30個（実装20枚＋予備）、U1はMy Partsの20個が選ばれた。My Partsを一般在庫と報告しない。割当可能数・保管状態・ロス数が確認できなければ未確認と記録する。

Component Placementsで3部品のパッド位置・面・回転・極性を確認し、Quote & Orderへ進む。原画の印刷方向と角丸も確認する。3Dモデルが見えたことだけでピン1やLED極性が合格したとは断定しない。

価格の事例は基板$21.33＋Standard PCBA $48.03＝$69.36。送料・税を含む支払総額ではなく、ICがMy Partsという条件付きの過去見積。見積画面の一時的な$0.00を確定額として使わない。

カート・チェックアウト・支払完了は別の状態。ユーザーがブラウザを引き取ったら停止する。ログインセッションを残す必要があれば対象タブを保持し、ログイン情報の公開や転記をしない。注文一覧へ移動しただけでは、支払済み／製造開始と断定しない。
