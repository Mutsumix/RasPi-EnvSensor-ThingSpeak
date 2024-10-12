# RasPi-EnvSensor-ThingSpeak

## 概要
このプロジェクトは、ラズベリーパイを使用してOMRONの環境センサーからデータを収集し、ThingSpeakプラットフォームにアップロードするものです。

## 機能
- OMRONセンサーからの環境データ（温度、湿度、照度、気圧、騒音、CO2濃度）の定期的な読み取り
- 収集したデータのThingSpeakへのアップロード

## 必要なハードウェア
- ラズベリーパイ（3B+以上推奨）
- OMRONの環境センサー（型番：2JCIE-BU01）

## セットアップ手順

### 1. 必要なライブラリのインストール
```
pip install -r requirements.txt
```

### 2. 設定ファイルの準備
`config.yml.example` を `config.yml` にコピーし、必要な情報を入力します。
```
cp config.yml.example config.yml
nano config.yml
```

### 3. ThingSpeakの設定
- ThingSpeakのアカウントを作成し、新しいチャンネルを作成します。
- チャンネルの設定で、以下のフィールドを追加します：
  1. Field 1: Temperature（温度）
  2. Field 2: Humidity（湿度）
  3. Field 3: Light（照度）
  4. Field 4: Pressure（気圧）
  5. Field 5: Noise（騒音）
  6. Field 6: CO2（二酸化炭素濃度）
- 各フィールドの単位を適切に設定します（例：温度は°C、湿度は%など）。
- チャンネルの設定を保存します。
- チャンネルのWrite API Keyをメモしておきます。このキーは`config.yml`ファイルで使用します。

注意: フィールドの順序と名前が、プログラムで送信するデータの順序と一致していることを確認してください。

### 4. config.ymlの編集
`config.yml` ファイルを開き、以下の情報を入力します：
- ThingSpeakのAPI Key
- センサーのポート設定
- データ送信の間隔

### 5. プログラムの実行
```
python main.py
```

## 使用方法
プログラムを実行すると、設定した間隔でセンサーデータを読み取り、ThingSpeakにアップロードします。

データの確認：
- ThingSpeakの公開チャンネルページでデータを確認できます。

## トラブルシューティング
- センサーからデータが取得できない場合：
  - センサーの接続とポート設定を確認してください。
  - `config.yml` のポート設定が正しいか確認してください。

- ThingSpeakへのデータ送信に失敗する場合：
  - インターネット接続を確認してください。
  - ThingSpeakのAPI Keyが正しいか確認してください。

## ライセンス
MIT

## 貢献
バグ報告や機能改善の提案は、Issueを通じて行ってください。プルリクエストも歓迎します。

## 作者
[Mutsumix](https://github.com/Mutsumix)
