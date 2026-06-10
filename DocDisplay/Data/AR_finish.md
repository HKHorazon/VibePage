Face AR 配件功能使用說明與導覽 (Walkthrough)
我們已經為您建立了所有必要的 C# 腳本與 Unity 編輯器自動化工具。以下將指引您如何在 Unity 中一鍵完成設定，並替換為您自己的 3D 模型與調整位置。

🛠️ 第一步：一鍵完成場景與 Prefab 設定
如果您已經打開了含有 AR 物件的場景，請照著以下步驟執行：

回到 Unity 編輯器，等待專案完成編譯。
在頂部選單列，點選 Tools > Face AR > Setup Scene & Prefab。
系統將會自動：
偵測您場景中的 ARFaceManager。
在 Assets/Prefabs/ 資料夾中生成 ARFaceAccessories.prefab。
在 Assets/Materials/ 資料夾中為配件生成 3D URP 材質，使 Placeholder 配件不會呈現粉紅色（材質遺失）。
將 Prefab 自動指派給您的 ARFaceManager。
在場景中建立一個質感深色半透明的 UI Canvas、選單滾動條 (ScrollRect)、以及 FaceAccessoryUI 控制器。
建立適合您專案輸入系統（新版或舊版 Input System）的 EventSystem。
當出現「Face AR Setup Complete」的對話視窗時，點擊 OK 即可。
🎨 第二步：更換您自己的 3D 模型與調整位置
本系統採用 Unity 標準的 階層 (Hierarchy) 架構 進行配件定位。您不需要寫任何程式碼來調整位置，直接在編輯器中用滑鼠拖曳調整即可：

在專案視窗 (Project Window) 中，找到並雙擊開啟 Assets/Prefabs/ARFaceAccessories.prefab 進到 Prefab 編輯模式。
展開 Accessories 子節點，您會看到 3 個配件的錨點物件：
Accessory_Hat（帽子錨點，預設有一扁平紅色圓柱體作為 Placeholder）
Accessory_Glasses（眼鏡錨點，預設有藍綠色鏡框立方體作為 Placeholder）
Accessory_Mustache（鬍子錨點，預設有一棕色膠囊體作為 Placeholder）
更換 3D 模型：
將您自己的 3D 模型（如 .fbx, .obj 等模型或 Prefab）拖曳到對應的錨點物件下（例如將您的帥氣帽子模型拖到 Accessory_Hat 下面，成為它的子物件）。
刪除或隱藏預設的 Placeholder 模型（例如隱藏 Hat_Model）。
調整位置與大小 (Offsets)：
選取您的 3D 模型，使用 Unity 的 移動 (Translate - W鍵)、旋轉 (Rotate - E鍵) 及 縮放 (Scale - R鍵) 工具，將您的模型對齊到您認為合適的位置。
提示：Prefab 的根目錄 (0, 0, 0) 是臉部中心位置（通常介於兩眼之間），您可以以此為基準對齊（例如帽子往上移、眼鏡稍微往前移、鬍子往下移）。
點擊 Prefab 視窗左上角的 < 儲存並退出 Prefab 編輯模式。
📱 第三步：手機測試與建置
確保已開啟 XR Plug-in Management：
前往 Edit > Project Settings > XR Plug-in Management。
Android (Google ARCore) 或 iOS (Apple ARKit) 必須勾選啟用。
前往 Build Settings，將您的 AR 場景加入 Build 列表中。
連接您的手機，點擊 Build And Run。
開啟手機上的應用程式並授予相機權限，對準人臉，即可透過底部的滾動按鈕無縫切換配件，且每個配件會精確載入您在 Prefab 設定的位置與大小。
📂 程式碼檔案連結
為方便您檢閱，本功能共包含以下檔案：

運行腳本：
FaceAccessoryController.cs (臉部配件切換器)
 — 控制單一臉部 Prefab 上的配件開關。
ARFaceAccessorySceneManager.cs (場景控制器)
 — 監聽臉部追蹤事件，保持多臉追蹤狀態與同步當前選定配件。
FaceAccessoryUI.cs (動態 UI 生成與微動畫)
 — 動態產生按鈕，提供現代毛玻璃質感與縮放過渡微動畫。
編輯器腳本：
FaceARSceneSetup.cs (一鍵整合工具)
 — 自動產生帶有 Placeholder 的 Prefab、URP 材質，並建立 UI 與綁定。