# 五款原創 Banner · 365 × 160

本頁在 `compact/index.html`，以 HTTP(S) 開啟。原生 ESM，無需 npm 或 build。原有首頁 600 × 400 廣告保留。

## 給 PM

1. 上方選預設格式，或在每張卡片下方切換 JS iframe、MP4、WebP、Spine 2D。
2. 「下載／嵌入」提供 MP4／WebP 單檔，及可獨立上傳的 JS／Spine ZIP。
3. 檔案放到公開 HTTPS 主機後，複製嵌入語法。可填入點擊後的活動網址。
4. 「選擇此格式」只存本機；頁尾匯出五款的選擇供討論。

## 五款內容

只重做這五款，保留活動標題與數字。人物、背景、立體標題、光效全部重新生成，未使用 temp 的人物、背景或特效貼圖。

| 主題 | 保留文字 | 新美術與動態 |
| --- | --- | --- |
| 頭框 | 德古拉榮耀／尊爵十強頭框 | 吸血鬼皇室猴敬禮、眨眼，紅寶石光環 |
| 轉盤 | 全台獨家／1000X 轉盤連開中／投注榜開打 | 風暴王者抬手，旋轉電環與金幣 |
| APP | 雙平台上架／下載APP／現領1288金幣 | 送禮小熊貓開禮盒，紫色傳送門 |
| LINE | 關注官方LINE@／天天領優惠／領$2000 | 玉龍遞金幣、眨眼，翡翠葉光環 |
| 西部 | 中西強檔・巔峰對決／1,500,00／流水投注榜 | 狐狸警長與女遊俠左右對峙、抬帽 |

西部數字 `1,500,00` 按原素材保留，未擅自修正位數。

## 四種輸出

四種格式共用同一個 Spine 分層場景及 4 秒時間軸，每款120格／30 FPS。

- **Spine 2D**：真正的 Spine 3.8 JSON、atlas、runtime；11–16 個獨立圖層、12–17 根骨骼。完整透明人物姿勢序列配合父骨骼定位；光環、金幣、星光、標題與 CTA 有各自的旋轉、位移、縮放、透明度時間軸。不是整張 Banner 換圖，也不是人體關節網格綁定。
- **JS iframe**：8 張靜態 WebP 圖集，原生 JS 切換120格，不含 video。
- **MP4**：H.264、730 × 320（2×）、30 FPS、yuv420p、faststart、無聲、無控制項。
- **動畫 WebP**：365 × 160、4 秒循環；暫停預覽時切換為靜態海報。

APP 重新生成16格，選用其中連貫的10格開盒姿勢直接播放，沒有光流或透明度混圖；人物動作為10格／秒並安排停頓，場景和輸出仍為30 FPS。其他人物使用光流補間，補間格不是額外 AI 生成。APP 與西部依完整透明輪廓分離人物，不使用等高格線裁切；等比例縮放並保留頭頂、腳底安全邊界。西部捨去比例不一致的末兩格，使用前六格及反向返回。

## 原始素材與重用

- `original-source/`：12 張選用的生成原圖，含5人物圖集、5背景、特效圖集及標題圖集。
- `CREATION.json`：完整提示詞與檔案對應。image_gen 無模型選擇器，無法核實 GPT-Image 2.5 版本。
- `assets/<id>/`：每款各自的成品與 ZIP；`catalog.json` 的 `spinePath` 指向各款分層素材，可獨立替換人物、背景、標題或特效。
- `vendor/spine-player.js`：沿用專案已有 Spine 3.8 播放器，首次約476 KB，同頁共用；Spine ZIP 內含播放器。
- `catalog.json`：規格及原始檔案 bytes，不含ZIP複本、CSS/JS、HTTP壓縮或GPU記憶體。

Spine 使用 region attachment 序列及骨骼圖層動畫，可由 runtime 載入；不含 `.spine` 編輯器工程檔。

## 製作工具

網站運行不需要製作工具。`tools/create-original.py` 從原圖切格、對齊、補間及製作 Spine；`tools/sample-original.cjs` 用實際 runtime 採樣；`tools/export-original.py` 輸出三種點陣格式；`tools/package.py` 更新下載包。

離線製作需要 Pillow、numpy、OpenCV、Node、ffmpeg。中間檔放在專案外 `codex-archives/five-original-production/`，網站不依賴該路徑。成品需人工視覺驗收。

載入時間包含解碼和快取，並非純下載速度；比較冷載入請停用快取。WebP 是否播放仍需目視確認。

整站部署需包含 `compact/` 與 `src/url.js`；下載 ZIP 是獨立成品。`?format=js|mp4|webp|spine` 指定初始模式。

## 交付壓縮

素材匯出後執行 `python3 compact/tools/optimize-delivery.py`，再執行 `python3 compact/tools/package.py`。壓縮工具從未壓縮的製作影格編碼，保留標題解析度、降低過高的圖集像素密度，並合併 APP 重複姿勢的貼圖區域；不改時間軸或播放尺寸。已完成壓縮的版本會略過，避免反覆有損壓縮。原始美術保留供修改，不包含在客戶下載包內。

每次新製作更新 catalog 時移除 `imageCompression` 標記並填新 revision，再執行壓縮流程。壓縮前後大小記於 `COMPRESSION.json`。

## 新增：惡魔血域

依合作廠商參考圖製作的第六款，遊戲標題「惡魔血域 / curse and rebirth」。12個透明胸像表情依序冷笑、露齒、奸笑、收回笑容；沒有光流或透明混圖。8隻蝙蝠各自有飛行路徑與8格拍翼，共13根骨骼、12圖層。

原圖及內建 imagegen 的生成提示詞在 `original-source/vampire/`；`tools/create-vampire.py` 建立分層場景，後續沿用採樣、四格式輸出與交付壓縮流程。這是依參考重新繪製的角色與標題，非直接提取廠商工程素材。


## 新增：18 品牌兩款簡體 Banner

- `shield18`：18神之盾现世，骑士举盾挥剑、巨龙吐息、护盾亮起、宝箱金币跃出。
- `casino18`：棋牌激情加码，女主角托手眨眼、骰子翻转、纸牌浮动、金币抛洒。

沿用用户提供的 `參考/logo.png`，没有重绘 Logo。其余素材由内建 imagegen 依参考重新绘制。画面采用简体中文，原始主视觉参考中的 18、18,888 保留；最新尺寸见文末交付规格。角色保留完整轮廓，以脚底／腰线对齐，独立部件由 Spine 骨骼驱动，角色关键姿势直接切换，不使用光流或交叉渐变。Spine RuntimeJSON/atlas，可播放；不含 `.spine` 编辑器工程。

生成提示词与文件对应：`original-source/luck18-prompts.json`。原图分别在 `original-source/shield18/` 和 `original-source/casino18/`。成品分别在 `assets/shield18/` 和 `assets/casino18/`，下载包没有原始大图或其他活动素材。

离线重制：`create-luck18.py` → `sample-original.cjs shield18 casino18` → `export-original.py shield18 casino18` → `deliver-luck18.py` → `optimize-delivery.py` → `package.py shield18 casino18`。后两个参数只更新本次下载包。网页无需 build。

18 品牌节奏修订：人物错开进场，约0.9秒起标题弹入，1.25秒起金币接续，3.65秒后退场。删除底部额外 CTA 小字；原活动标题内容保留。四格式共用时间轴，poster 使用2.5秒完整构图。

节奏差异修订：神盾标题0.92秒登场；棋牌人物更快进场，骰子0.42秒起错开落下，标题延至1.42秒弹入，眨眼动作同步延后0.62秒，金币1.8秒接续，棋牌3.4秒起退场。两款循环仍为4秒，所有交付格式一致。

## 18 品牌最终投放尺寸

`shield18` 和 `casino18` 现为 **764×288**，WebP、JS 每格与 Spine 画布使用该尺寸；高清 MP4 为1528×576，4秒循环，节奏差异保留。重新铺排背景与图层位置，人物、Logo及字图统一等比缩放，未拉伸原图。catalog 的 `width` / `height` 驱动预览、复制语法和独立下载包；其余六款仍为365×160。

## 18 品牌高清修订

显示尺寸保持764×288，MP4改为1528×576、H.264 两遍编码，目标约900 KB；重新从原始美术生成高密度人物、背景和标题图层，不是放大旧影片。WebP及JS仍为764×288，Spine图集也使用较高密度素材。神盾标题及Logo中心统一为x=382。

MP4 网络交付预算：`videoTargetBytes=900000`，`tools/encode-mp4.py` 直接从渲染原帧两遍编码，保留1528×576、30FPS、4秒、无音轨。神盾900871 bytes，棋牌900448 bytes。
