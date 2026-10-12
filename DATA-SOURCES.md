# 資料來源與授權

本工具不含任何手繪、模擬或推測產生的動作資料。所有關節角度皆來自以下公開資料集的實測值。

---

## L1 骨骼網格

**BodyParts3D**（126 個骨骼部件）

> BodyParts3D, Copyright© The Database Center for Life Science licensed by CC Attribution-Share Alike 2.1 Japan

- 授權：[CC BY-SA 2.1 Japan](https://creativecommons.org/licenses/by-sa/2.1/jp/)
- 來源：<https://dbarchive.biosciencedbc.jp/en/bodyparts3d/desc.html>
- 本專案的處理：座標轉換、數值量化，以及 **quadric decimation 減面**
  （總面數 462,592 → 206,816）。減面比例依部位不同：下肢保留 75%、骨盆腰椎 65%、
  頸椎 25%、胸廓與頭顱 18%，因為步態教學會放大檢視的是下肢。
  **這是對原始網格的修改**，依 CC BY-SA 2.1 Japan 於此聲明；減面腳本見 `build/decimate.py`
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

Shida, T.K.F., Costa, T.M., de Oliveira, C.E.N., Treza, R.C., Hondo, S.M., Los Angeles, E.,
Bernardo, C., de Oliveira, L.S., de Jesus Carvalho, M., Coelho, D.B. (2023).
*A public data set of walking full-body kinematics and kinetics in individuals with Parkinson's disease.*
Frontiers in Neuroscience, 17, 992585.

- DOI：<https://doi.org/10.3389/fnins.2023.992585>
- 資料存放：Coelho, D.B. — figshare <https://doi.org/10.6084/m9.figshare.14896881>
- 授權：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- 本工具使用：ON／OFF 組平均、凍結／非凍結組平均、2 名個案的 ON／OFF 對照
- ⚠️ 本資料集未提供額狀面以外的完整通道，髖內收為唯一有額狀面資料的世代

### 3. 髖關節退化（術前，n=106）

Bertaux, A., Gueugnon, M., Moissenet, F. et al. (2022).
*Gait analysis dataset of healthy volunteers and patients before and 6 months after total hip arthroplasty.*
Scientific Data, 9, 399.

- DOI：<https://doi.org/10.1038/s41597-022-01483-3>
- 授權：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)（figshare 記錄載明）
- 資料存放：Laroche, D. — figshare <https://doi.org/10.6084/m9.figshare.14420645>
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

### 5. 足弓（正常足部姿勢，站立期，n=30）

Sanchis-Sales, E., Sancho-Bru, J.L., Roda-Sales, A., Chiva-Miralles, M.J., García-Gomáriz, C. (2024).
*Foot kinematics and kinetics data for different static foot posture collected using a multi-segment foot model.*
Scientific Data, 11, 1307.

- DOI：<https://doi.org/10.1038/s41597-024-04166-3>
- 資料存放：Zenodo <https://doi.org/10.5281/zenodo.10838067>
- 授權：[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)（Zenodo 記錄載明）
- 標記組：Bruening 等 2012 的多節足部模型改編（脛、後足、中足、拇趾四節，20 個標記）
- 本工具使用：依足部姿勢指數（Foot Posture Index, FPI）分成三組，各組先在受試者內
  平均 5 次試驗，再跨受試者逐點平均：
  - 正常足（FPI 0 至 +5）n=30
  - 旋前足／扁平（FPI > +10）n=20
  - 旋後足／高弓（FPI −5 至 −12）n=20
- ⚠️ 三項限制，介面上皆有標示：
  1. **只有站立期**，時間軸 0–100% 指的是站立期而非完整步態週期
  2. **只有右腳**，且只有踝／中跗／第一蹠趾三個關節；其餘關節無資料，維持參考姿勢
  3. **全部為健康成年男性**（27.3 ± 4.0 歲），非臨床族群、無女性資料，不可當常模
- ⚠️ 零位為「各受試者自己的放鬆站姿」，不是解剖中立位
- ⚠️ 資料集的踝水平面分量（R_ANK_AB）在本工具的單軸踝模型中無對應自由度，未顯示

---

## 本工具對 L3 動作資料的改作

依 CC BY 4.0 第 3(a)(1)(B) 條，須標示是否修改。本工具對五個資料集一律做了以下處理：

- 時間正規化為每週期 100 點
- 跨受試者逐點平均（組平均片段）
- 單位與座標系轉換
- 週期首尾線性去趨勢（make_cyclic）
- 每個片段施加一個常數髖角度偏移（幾何閉合條件求得，數值顯示於介面）

足弓片段（arch_normal）不適用上述部分處理：它只有站立期，首尾本來就不相接
（著地與離地是兩個不同瞬間），因此**未做首尾去趨勢**，也沒有髖角度偏移與貼地閉合。

### 合成片段：arch_walk_normal／pronated／supinated（「足弓（走路中・合成）」）

這是全工具唯一一個**合成**片段，不是同一個人身上量到的，介面上以橘字標示。

- **身體**（骨盆、腰椎、雙髖、雙膝、踝矢狀面、左腳全部）：取自資料集 1 的
  `vc_young`（Van Criekinge 2023 健康年輕組，n=39、27.2 歲）。
  20 個通道逐點比對確認**一個數字都沒有改動**。
  **三個合成片段共用這同一個身體**，所以把它們疊在一起時，看到的差異
  一定來自足部姿勢分組，不會混進不同走路資料的差異。
- **足部**（右側中跗三平面、右側第一蹠趾三平面、右踝額狀面）：取自資料集 5 的
  三組（Sanchis-Sales 2024，全為男性）——
  正常足 n=30、旋前足（扁平）n=20、旋後足（高弓）n=20。
  這七個通道在 `vc_young` 裡原本完全不存在，屬於「填空」而非覆蓋。
- **時間對應**：足弓資料只有站立期，線性對應到步態週期的 0–61.4%
  （該片段由測力板判定的右足離地時間）。
- ⚠️ **擺盪期（61.4–100%）足部無資料**，由離地值以升餘弦平滑回到著地值。
  這是模型補值，不是量測。
- ⚠️ **零位處理**：足弓資料集的零位是「各受試者自己的放鬆站姿」，與 BodyParts3D
  標本的參考姿勢不是同一個東西。處理方式與既有的骨盆零位對齊一致——扣掉站立期
  20–50%（足部貼平）的平均，中跗矢狀面再加一個常數閉合修正
  （正常 1.5°、旋前 1.5°、旋後 1.0°）。
  該修正取值為「使足部貼平期間（原片段跟與前足皆在門檻內的 15–40%）前足不高於
  原片段」成立的最小偏移，由 `solve_arch_walk.js` 以無頭瀏覽器逐 0.5° 掃描求得
  （前足對中跗角度的槓桿實測為 1.44 mm/度）。
  **因此擺幅是實測的，絕對角度不是。**
- 驗證：
  - 身體 20 個通道逐點比對，三個合成片段全部與 `vc_young` 完全相同
  - 合成片段與獨立的站立期片段，同一站立期時間點的關節角度差為常數
    （中跗 −2.30°、第一蹠趾 −4.73°，全程變異各 0.42° 與 0.85°，殘差來自重新取樣）
  - 30 個片段的事件表全部相符，0 JS 錯誤
  - 足地接觸判定與 `vc_young` 逐幀比對：差異集中在雙支撐期（8–14%），
    且多數是改善（原片段在 8% 判為「右足未接觸」，合成片段為「僅腳趾著地」；
    足部貼平的時間點由 15% 提前到 12%）。標紅幀數：原片段 21/101，
    正常 22、旋前 21、旋後 20。多出的那一幀在 10% 的左腳標示，
    屬於雙支撐期高度基準切換，是本工具既有的限制，不是足部資料造成的。

三組之間的差異（中跗矢狀面，站立期；負值＝足弓拉高）：

| 組別 | 著地 | 最大背屈（足弓最低） | 離地 |
|---|---|---|---|
| 正常足 n=30 | −4.6° | +4.2° | **−8.4°** |
| 旋前足（扁平）n=20 | −4.4° | +5.5° | **−1.4°** |
| 旋後足（高弓）n=20 | −3.1° | +4.7° | **−6.1°** |

旋前組在離地時幾乎沒有把足弓拉回來，這是三組之間最大的差別。

### 推進期放大片段：arch_push_normal／pronated／supinated

三組足型的差異幾乎全部集中在推進期，放在完整片段裡看不出來。原始數值
（完全未經本工具處理）的組間差：

| 站立期 | 中跗（足弓） | 第一蹠趾 |
|---|---|---|
| 0–85% | 差 < 1° | 差 < 1° |
| 85–100% | 扁平 − 正常 **+7.9°**（d = 1.93，站立期 95%） | 扁平 − 正常 **−12.8°**（d = 1.91，站立期 89%） |

這三段把足弓片段的站立期 70–100% 取出，橫軸線性拉伸成 0–100%。
**這是重新取樣，數值一個都沒有改動**——介面上標示的是原片段的站立期位置，
時間軸標籤為「推進期」而非「站立期」。

放大後的三組對照（中跗矢狀面，負值＝足弓拉高）：

| 組別 | 起點（站立期 70%） | 離地 | 全段變化 |
|---|---|---|---|
| 正常足 n=30 | +6.0° | −5.6° | −11.6° |
| 旋前足（扁平）n=20 | +6.0° | **+1.6°** | −4.4° |
| 旋後足（高弓）n=20 | +5.3° | −4.0° | −9.2° |

第一蹠趾的差別是**時機**而非幅度：三組最終都到 24–30°，但旋前組明顯較慢——
放大後 60% 時正常組已達 25.5°，旋前組才 12.8°（差 12.7°），到離地才追上來
（差只剩 2.7°）。

⚠️ 需要一併說明的限制：這份資料的零位是「各受試者自己的放鬆站姿」，
所以靜態足弓高度的組間差**在收資料的當下就被扣掉了**，本工具無法呈現。
此外資料集自己量的人體測計值顯示，在這 70 人裡正常組與旋前組的
內踝高度／足長只差 1.4 mm（Cohen d = 0.29），真正與另外兩組分得開的是
旋後（高弓）組（d ≈ 1.1–1.2）。

原作者與各資料集不對本工具的呈現與推論負責；資料依其授權「按現狀」提供，
不附任何明示或默示的擔保。

---

## 引用本工具時

請同時標示上述原始資料集。本工具只是呈現層，科學貢獻屬於原作者。
