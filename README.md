# Faster Whisper API

Faster WhisperモデルをFastAPI経由でAPI化したプロジェクトです。

## 特徴
- 音声ファイルのアップロードと文字起こし
- ffmpegによる音声変換（16kHz, モノラル）
- APIキーによる認証機能
- Dockerで簡単にデプロイ可能

## 使い方

### 環境変数
- `API_KEY`: API認証用キー（デフォルト："default_api_key"）
- `MODEL`: Whisperモデル名（デフォルト："base"）
- `USE_CUDA`: CUDA使用設定（"true"または"false"、デフォルト："false"）
- `THRESHOLD_DB`: 音量閾値（デフォルト：-50）
- `LANGUAGE`: 言語設定（デフォルト："ja" , https://github.com/openai/whisper/blob/main/whisper/tokenizer.py#L10-L111 )

### Dockerで実行
1. Dockerイメージのビルド
```
docker build -t faster-whisper-api .
```

2. コンテナの起動
- CPU
```
docker run -p 8000:8000 -e API_KEY=your_api_key faster-whisper-api
```
- CUDA
```
docker run -p 8000:8000 --gpus all -e USE_CUDA=true -e API_KEY=your_api_key faster-whisper-api
```

### エンドポイント
- **POST /transcribe**  
音声ファイル（multipart/form-data）をアップロードし、文字起こし結果を取得。

```
curl -X POST "http://localhost:8000/transcribe" \
  -H "Authorization: your_api_key" \
  -F "file=@/path/to/audio_file.mp3"
```

```
{
  "text": "ここに文字起こしされたテキストが入ります。"
}
```
