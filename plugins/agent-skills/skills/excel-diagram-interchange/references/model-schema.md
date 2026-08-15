# Canonical diagram model

`diagram.json` is the canonical representation.

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

IDs must match `^[A-Za-z][A-Za-z0-9_-]{0,119}$` and be unique within their scope.

The supported style fields are:

- `fill`
- `stroke`
- `stroke_width`
- `dashed`
- `font_color`
- `font_size`
- `arrow_start`
- `arrow_end`

Colors are six-digit `#rrggbb` strings. `fill` may also be `none`.
