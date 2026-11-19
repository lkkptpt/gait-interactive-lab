# 資料部分的授權

本 repo 的授權分兩層。**程式碼與資料不同授權，散布時請分別遵守。**

## 程式碼：MIT

適用於：

- `build/template.html` 當中的 HTML／CSS／JavaScript
- `build/*.py` 全部建置與檢查腳本

見 `LICENSE`。

## 資料：依來源各自的授權

### `build/anatomy.json` → CC BY 4.0

包含或衍生自 BodyParts3D 的骨骼網格。資料庫授權方於 2025-02-27 將授權改為
[CC Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/)
（[資料庫授權頁](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html)；v1.12.2 以前本 repo 依舊授權 CC BY-SA 2.1 Japan 標示）。

- 你可以自由使用、修改、再散布，包含商業用途
- 必須保留這段標示，並註明有無修改：

  > BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International

### `build/motion.json` → CC BY 4.0

包含四個研究資料集的衍生數值（時間正規化、平均、單位轉換），全部原始資料集
皆為 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)。
散布時須標示原作者與出處，完整引用見 `DATA-SOURCES.md`。

### `index.html`（成品）

內嵌上面兩份 CC BY 4.0 資料與 MIT 程式碼。散布時保留頁面內「資料來源與授權」段落的標示即可，
不需相同方式分享。

### `three.min.js` → MIT（three.js 原作者）

未修改的 three.js r128，檔頭保留原始 MIT 授權聲明。
著作權屬 three.js authors，非本專案。

### `build/skeleton.json` → MIT

關節中心為本專案由骨骼幾何推估而得（球面擬合、解剖標記點定位），
非 BodyParts3D 原始內容，視為本專案的程式產出。

## 簡表

| 檔案 | 授權 | 相同方式分享 |
|---|---|---|
| `build/template.html` | MIT | 否 |
| `build/*.py` | MIT | 否 |
| `build/skeleton.json` | MIT | 否 |
| `three.min.js` | MIT（three.js authors） | 否 |
| `build/motion.json` | CC BY 4.0 | 否（須標示來源） |
| `build/anatomy.json` | CC BY 4.0 | 否（須標示來源） |
| `index.html`（成品） | 內含 CC BY 4.0 資料＋MIT 程式碼 | 否（須保留標示） |
