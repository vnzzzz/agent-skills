# 正規ダイアグラムモデル

`diagram.json`を正規表現として使用する。

```text
Diagram
  schema_version: "1.0"
  title: string
  metadata: object
  pages[]
    id, name, width, height
    warnings[]
    nodes[]
      id, label, shape
      x, y, width, height, rotation, z
      style
      metadata
    edges[]
      id, source?, target?, label
      points[[x,y], ...]
      z
      style
      metadata
```

IDは`^[A-Za-z][A-Za-z0-9_-]{0,119}$`に一致し、各scope内で一意でなければならない。

対応するstyle fieldは次のとおり。

- `fill`
- `stroke`
- `stroke_width`
- `dashed`
- `font_color`
- `font_size`
- `arrow_start`
- `arrow_end`

色は6桁の`#rrggbb`形式で表す。`fill`には`none`も指定できる。
