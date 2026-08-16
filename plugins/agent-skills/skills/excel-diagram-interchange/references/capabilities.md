# 対応機能

Excel worksheetをキャンバスのように使って描いた図形中心のダイアグラムを、ローカルだけで相互変換するためのtool。配布される同一のSkill directoryをClaude CodeとCodexの両方で利用できる。

次のformat間を変換する。

- Excel `.xlsx`
- 正規`diagram.json`
- 正規`diagram.xml`
- Mermaid `.mmd`
- draw.io `.drawio`

runtimeではExStruct、Excel、LibreOffice、COM、browser、remote API、network accessを使用しない。

## アーキテクチャ

```text
.xlsx ───────┐
.drawio ─────┤
.mmd ────────┼──> canonical diagram.json ──> any supported output
.xml ────────┤
.json ───────┘
```

`diagram.json`を正規の内部表現とし、その他のformatはadapterとして扱う。

## モデルが非対称である理由

Excel、正規JSON/XML、draw.ioは明示的な座標とsizeを保持できる。一方、標準的なMermaid flowchartはrendererがlayoutを決定するため、一般的な絶対座標モデルを持たない。

そのため、生成するMermaidには次のような無視可能なcommentを含める。

```text
%% diagram-interchange: {"type":"node","id":"web","x":80,"y":100,"width":180,"height":80,...}
```

通常のMermaid rendererはこれらのcommentを無視する。このconverterは、自身が生成した`.mmd`を再変換するときにgeometryを復元するために利用する。これらのcommentを持たないthird-party Mermaidには、deterministicな自動layoutを適用する。

## 対応機能マトリクス

| 機能 | JSON/XML | draw.io | Excel | Mermaid |
|---|---:|---:|---:|---:|
| Node/edge topology | 完全 | 対応プロファイル内で完全 | 対応プロファイル内で完全 | 対応syntax内で完全 |
| 絶対geometry | 完全 | 完全 | 完全 / cell anchorは近似 | metadata commentのみ |
| Rotation | 完全 | 完全 | 完全 | metadata commentのみ |
| z-order | 完全 | node/edgeをまたいで保持 | node内・connector内で保持 / cross-typeはnode→connectorへ正規化 | metadata commentのみ |
| Shape text | 完全 | 完全 | 完全 | 完全 |
| 基本fill/stroke/font | 完全 | おおむね対応 | おおむね対応 | 基本的なnode style |
| Connector label/arrow | 完全 | おおむね対応 | おおむね対応 | 基本対応 |
| 複数page/sheet | 完全 | 完全 | 完全 | 最初のpageのみ |
| Cell value/formula | モデル化しない | N/A | 意図的に無視 | N/A |
| Image/SmartArt/chart | 非対応 | 非対応 | 警告して無視 | 非対応 |
| Grouped shape | モデル化しない | inputがすでにflatな場合のみ | v1では警告して無視 | 非対応 |
| Custom/freeform geometry | 正規化 | 正規化 | 正規化 / 無視 | 正規化 |

## 対応プロファイル

### Node

- rectangle / rounded rectangle
- ellipse
- diamond
- cylinder (`can`)
- cloud、hexagon、triangle、parallelogram、trapezoid、pentagon、octagonなどの基本preset shape
- shape text
- x/y、width/height、rotation、z-order
- fill、stroke、line width/dash、font color/size

### Edge

- source / target node ID
- connector label
- 任意のpoint
- line width/dash
- start/end arrowhead
- native `xdr:cxnSp` connector
- 一般的なworkbook writerが通常の`xdr:sp` shapeとしてserializeしたconnector preset。この場合、endpointはgeometryから推定する。

### 意図的に対象外とするもの

- すべてのcell value、formula、comment、table、formatting
- `.xls`、`.xlsm`、`.xlsb`
- VBA、OLE、ActiveX、external link、embedded file
- picture、external icon download
- chart、SmartArt、WordArt
- 任意のMermaid directive、callback、hyperlink、JavaScript
- DrawingMLの完全なstyle/effect

## Round-tripの期待値

- JSON ↔ 正規XML: 構造的に等価であることを意図する。
- JSON ↔ draw.io: 対応プロファイル内でgeometry、topology、node/edgeをまたぐstacking順序を保持する。
- JSON ↔ Excel: 対応するDrawingML profile内でgeometryとtopologyを保持する。cell-based anchorはoutput時にabsolute anchorへ正規化される場合があり、nodeとconnectorをまたぐstacking順序はnode→connectorへ正規化する。
- JSON ↔ 生成Mermaid: topologyとprofile geometry commentを保持する。
- 任意のMermaid ↔ その他format: topologyを保持し、layoutは生成する。

## スコープ境界

SpreadsheetDrawingML全体を実装することは不要な再実装になる。このSkillは、通常のshape、text、connector、geometry、basic styleに対象を絞ったinteroperability profileを実装する。

独自の正規モデルが必要なのは、Excel DrawingML、draw.io `mxGraphModel`、Mermaidの間に共通の標準interchange modelが存在しないためである。将来、grouped shape、picture、custom geometry、高度なOffice effectまで対象を広げる場合は、このparserを無制限に拡張するのではなく、Microsoft Open XML SDKを基盤にした専用componentへOOXML adapterを置き換える。
