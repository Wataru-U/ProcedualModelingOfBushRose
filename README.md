# ProcedualModelingOfBushRose
 
## 使い方
 ParameterWindow.py をMayaで実行 

## ファイル構成

```
.
├── plug・ins
│   └── RoseController.py : mayaのプラグインマネージャーで読み込む
└── scripts
    ├── BackCalcBushRose.py : RoseController.py用
    ├── BushRose_cube.py : キューブ状に剪定
    ├── BushRose.py : 普通の
    ├── Vector3.py : ライブラリ用
    ├── window_back_calcuration.py : 逆算、実行用
    ├── window_cube.py : キューブ状に剪定、実行用
    └── window.py : 実行用
```

### RoseController.py
- MELコマンドで```RoseBuild```を実行
- 生成は`RoseRegenerate`
- ランダムなし

### scripts
- windowがついたファイルを使う
- スクリプトエディタで実行する

![高画質2](https://user#images.githubusercontent.com/43666946/201284539#2e3cb53c#d9d4#4cea#a852#397ebed2ed89.jpg)

デモ動画（２倍速）
https://user#images.githubusercontent.com/43666946/203512130#b8ec3ee6#dfcd#4961#b342#6fa12a63665a.mp4

