# 資料部分的授權

本 repo 的授權分兩層。**程式碼與資料不同授權，散布時請分別遵守。**

## 程式碼：MIT

適用於：

- `build/template.html` 當中的 HTML／CSS／JavaScript
- `build/*.py` 全部建置與檢查腳本

見 `LICENSE`。

## 資料：依來源各自的授權

### `build/anatomy.json` 與 `index.html` → CC BY-SA 2.1 Japan

兩者包含或衍生自 BodyParts3D 的骨骼網格，該資料庫採用
[CC Attribution-Share Alike 2.1 Japan](https://creativecommons.org/licenses/by-sa/2.1/jp/)。

**「相同方式分享」的實際意義：**

- 你可以自由使用、修改、再散布，包含商業用途
- 但散布修改後的版本時，**必須以同一授權釋出**，不能改成 MIT 或閉源
- 必須保留這段標示：

  > BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan

`index.html` 是把網格資料內嵌進單一檔案的成品，因此整份檔案受此條款拘束。
若你只想用 MIT 的部分，請使用 `build/template.html`（不含任何網格資料）。

### `build/motion.json` → CC BY 4.0

包含四個研究資料集的衍生數值（時間正規化、平均、單位轉換），全部原始資料集
皆為 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。
散布時須標示原作者與出處，完整引用見 `DATA-SOURCES.md`。

CC BY 4.0 允許衍生作品採用其他授權條款，因此將其與 BY-SA 的網格資料合併為
`index.html` 並無衝突。

### `build/skeleton.json` → MIT

關節中心為本專案由骨骼幾何推估而得（球面擬合、解剖標記點定位），
非 BodyParts3D 原始內容，視為本專案的程式產出。

## 簡表

| 檔案 | 授權 | 相同方式分享 |
|---|---|---|
| `build/template.html` | MIT | 否 |
| `build/*.py` | MIT | 否 |
| `build/skeleton.json` | MIT | 否 |
| `build/motion.json` | CC BY 4.0 | 否（須標示來源） |
| `build/anatomy.json` | CC BY-SA 2.1 JP | **是** |
| `index.html`（成品） | CC BY-SA 2.1 JP | **是** |
