# 資料來源與授權

本工具不含任何手繪、模擬或推測產生的動作資料。所有關節角度皆來自以下公開資料集的實測值。

---

## L1 骨骼網格

**BodyParts3D**（126 個骨骼部件）

> BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan

- 授權：[CC BY-SA 2.1 Japan](https://creativecommons.org/licenses/by-sa/2.1/jp/)
- 來源：<https://dbarchive.biosciencedbc.jp/en/bodyparts3d/desc.html>
- 本專案的處理：座標轉換與數值量化，**未修改形狀**
- ⚠️ 此授權含「相同方式分享」條款。`build/anatomy.json` 與內嵌它的 `index.html`
  必須以同一授權散布，詳見 `LICENSE-DATA.md`

---

## L3 動作資料

### 1. 健康成人（年輕／中年／年長平均，n=138）與中風（n=50）

Van Criekinge, T., Saeys, W., Truijen, S. et al. (2023).
*A full-body motion capture gait dataset of 138 able-bodied adults across the life span and 50 stroke survivors.*
Scientific Data, 10, 852.

- DOI：<https://doi.org/10.1038/s41597-023-02767-y>
- 資料：figshare collection <https://doi.org/10.6084/m9.figshare.c.6503791>
- 授權：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 本工具使用：健康組三個年齡層的逐點平均；中風組 3 名個案 ＋ 組平均
- 標記組：Plug-in Gait

### 2. 帕金森氏症 ON／OFF 藥效（n=26）

*A dataset of overground walking full-body kinematics and kinetics in individuals with Parkinson's disease.*

- 資料：figshare article 14896881 <https://doi.org/10.6084/m9.figshare.14896881>
- 授權：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 本工具使用：ON／OFF 組平均、凍結／非凍結組平均、2 名個案的 ON／OFF 對照
- ⚠️ 本資料集未提供額狀面以外的完整通道，髖內收為唯一有額狀面資料的世代

### 3. 髖關節退化（術前，n=106）

Bertaux, A., Gueugnon, M., Moissenet, F. et al. (2022).
*Gait analysis dataset of healthy volunteers and patients before and 6 months after total hip arthroplasty.*
Scientific Data, 9, 399.

- DOI：<https://doi.org/10.1038/s41597-022-01483-3>
- 授權：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 本工具使用：醫師依步態錄影判定為 Trendelenburg（4 例）與 Duchenne（3 例）的個案
- 標記組：Plug-in Gait

### 4. 跑步機行走（控制速度）

Fukuchi, C.A., Fukuchi, R.K., Duarte, M. (2018).
*A public dataset of overground and treadmill walking kinematics and kinetics in healthy individuals.*
PeerJ, 6, e4640.

- DOI：<https://doi.org/10.7717/peerj.4640>
- 資料：figshare <https://doi.org/10.6084/m9.figshare.5722711>
- 授權：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 本工具使用：年輕組與年長組的跑步機 T05 平均

---

## 外部程式庫

**three.js r128** — [MIT License](https://github.com/mrdoob/three.js/blob/dev/LICENSE)

> Copyright © 2010-2021 three.js authors — MIT License

- 本 repo 內含未修改的 `three.min.js`（r128，檔頭保留原始 MIT 授權聲明）
- `index.html` 優先載入同目錄的 `three.min.js`；若不存在（例如單獨下載 index.html），
  自動退回 cdnjs 的 r128

---

## 曾經評估但未採用

| 資料集 | 授權 | 未採用原因 |
|---|---|---|
| OpenSim `gait2354` 範例（subject01） | 不明 | OpenSim 的 Apache 2.0 僅涵蓋 GUI 與 API；官方明載「Models, examples and plugins retain their own custom licenses」，範例資料的散布條件無法確認 |
| 腦性麻痺 3D 步態（figshare 4877432） | CC0 | 授權沒問題，但資料與剛體骨架模型自相矛盾——雙支撐期兩足距離變化達 18.5 cm，無法正確呈現，已移除 |

---

## 引用本工具時

請同時標示上述原始資料集。本工具只是呈現層，科學貢獻屬於原作者。
