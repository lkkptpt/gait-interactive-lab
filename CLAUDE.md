# CLAUDE.md — 步態互動實驗室

給 Claude Code 的專案說明。每次開新 session 先讀這份，再動手。

## 這個專案是什麼

課堂用的 3D 步態教學工具：把五個公開研究資料集的實測關節角度套在 BodyParts3D 骨骼網格上播放，可轉視角、拉時間軸、疊加不同族群比對。單一 `index.html`，瀏覽器直接開，GitHub Pages 線上版：https://lkkptpt.github.io/gait-interactive-lab/

**是**：34 個片段的步態資料播放器（給教練、學生、物理治療師看「真實的步態長什麼樣子」）
**不是**：步態模擬器、評估工具、常模

作者：鄭宇劭（物理治療師／練健康總教練）。用途：練健康課堂投影、學員平板操作、IG／講義截圖。

## 不能破的原則

1. **實測／推得／模型三者一律在介面上標示，不混在一起。** 新增任何通道或指示，先回答「這是資料集量到的，還是算出來的？」算出來的要標「模型推算」「借用」「合成」。
2. **擺幅是實測的，絕對角度不是。** 骨盆、腰椎、手臂只取週期內變化量；靜態姿勢是文獻常數。不要讓工具看起來能判讀某人骨盆前傾幾度。
3. **不手繪、不模擬動作。** 沒有資料集追蹤的自由度（距下、蹠趾、膝螺旋回鎖）只能做成明確標示的可調模型，預設關閉或標示。
4. **授權要跟著走。** 骨骼網格 CC BY 4.0（BodyParts3D 2025-02-27 起的現行授權，原為 CC BY-SA 2.1 JP）；動作資料五個資料集皆 CC BY 4.0。動到資料就同步更新 `DATA-SOURCES.md` 與介面內的「資料來源與授權」段落。
5. **說法要經得起量測。** v1.10.2 曾把「足弓在塌」改成「前足抬起」——因為把位置換到跟骨座標系後實測舟狀骨其實往上。寫介面文字前先算，不要寫直覺。

## 檔案結構

```
index.html            產出物（3.8 MB，內嵌三份 JSON）——不要直接改
three.min.js          three.js，離線使用時與 index.html 放同一資料夾
build/
  template.html       ← 介面與程式碼都在這裡改
  anatomy.json        骨骼網格（減面後）
  skeleton.json       關節階層、關節中心、旋轉軸
  motion.json         34 個片段的角度曲線（100 點正規化）
  build.py            把三份 JSON 塞進模板 → ../index.html
  check_build.py      檢查 41 個函式定義齊全（曾因字串取代刪掉三個函式而寫）
  check_cycles.py     檢查呼叫環都有阻斷旗標（曾因無窮遞迴而寫）
  check_syntax.py     抽出內嵌 script 跑 node --check（取代原本永遠報錯的 sed 指令）
  build_*.py / patch_*.py / solve_*.js   各版本的資料處理腳本，留作來源追溯
DATA-SOURCES.md       五個資料集的引用、處理方式、每個推得值的算法
LICENSE / LICENSE-DATA.md
README.md             對外說明（使用者看的）
```

## 工作流程

```bash
# 1. 改 build/template.html（或資料 JSON）
# 2. 重新產生
python3 build/build.py
# 3. 三道檢查，缺一不可
python3 build/check_build.py index.html
python3 build/check_cycles.py index.html
python3 build/check_syntax.py index.html
# 4. 本機開 index.html 實際看一下（Playwright 截圖也行）
# 5. commit + push（push 到 main 即發佈到 GitHub Pages）
```

- 版本號在 `build/template.html` 兩處：`<title>` 與 `.sub` 說明段，改版要一起改
- 版號規則：修文字／修 bug → patch；新功能或新片段 → minor
- Commit 訊息格式：`vX.Y.Z：中文一句話說改了什麼`（冒號用全形）
- 介面文字全部繁體中文，專有名詞附英文原名

## 資料集（詳見 DATA-SOURCES.md）

| 代號 | 來源 | 內容 |
|---|---|---|
| Van Criekinge 2023 | Sci Data 10:852 | 健康成人 138 人跨年齡 ＋ 中風 50 人 |
| Shida 2023 | Front Neurosci 17:992585 | 帕金森 ON/OFF、凍結／非凍結（含手臂） |
| Bertaux 2022 | Sci Data 9:399 | 髖關節炎 ＋ 健康對照（含手臂） |
| Fukuchi 2018 | PeerJ 6:e4640 | 跑步機控制速度 |
| Sanchis-Sales 2024 | Sci Data 11:1307 | 足弓三型，多節段足部，只有站立期 |

## 目前狀態（2026-10-31）

- v1.12.2：上肢已加入（64 塊骨頭），手臂擺幅實測、靜態姿勢文獻常數，肘靜態角三檔可切
- v1.12.3（2026-11-19）：骨骼網格授權標示改為 CC BY 4.0（BodyParts3D 2025-02-27 起的現行授權）
- v1.13.0（2026-11-19）：配色與字體改用練健康品牌規範正式色值（strength #00547A 等），只換介面外殼；資料語意色（關節標記、警告、對照組）不動。不放練健康 logo，維持個人作品（見 build/retheme_lkk2.py）
- v1.13.1（2026-11-19）：補上從未定義的 --warn（淺色面板 #A8430F、深色與 3D 舞台 #ff8a6b），借用／模型／未知的標示恢復上色
- 足弓三型（站立期、走路合成、推進期放大）已完成
- 已知限制列在 README「已知限制」段，不要重複造輪子去解已經標為限制的東西，除非有新資料

## 下一步候選（由宇劭決定優先序，未定）

- 3D 解剖圖（anatomy.of.motion 風格：灰模＋重點肌肉上色）——目前另案討論，是否併入本 repo 未定
- 課堂使用回饋後的介面調整
- 其他候選請在這裡補

## 跟宇劭合作的方式

- 他是物理治療師，看得懂生物力學，直接講機制與數據，不用鋪陳
- 回覆用繁體中文
- 做完簡短回報：改了哪裡、版號、檢查有沒有過；不要重述已知設定
- 不確定的設計決定（例如某個值該標實測還是模型）先問，不要自己定
