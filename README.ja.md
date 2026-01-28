# export-chromium-history

Chromium ベースのブラウザから閲覧履歴をエクスポートし、Safari がインポート可能な形式に変換します。

## 背景

Chrome および Chromium ベースのブラウザは、閲覧履歴を直接エクスポートする機能を提供していません。本ツールはローカルの `History` SQLite データベースを読み取り、記録を Safari 互換の JSON 形式に変換することで、ブラウザ間の履歴移行を実現します。

| 移行方向 | 方法 |
|----------|------|
| Chromium → Safari | 本ツールでエクスポート → Safari にインポート |
| Safari → Chromium | Chromium の内蔵インポート機能を使用 |

## 環境要件

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) パッケージマネージャ

## 使用方法

### 1. History ファイルを特定する

Chromium ベースのブラウザの閲覧履歴は、`History` という名前の SQLite ファイルに保存されています。

**方法 1：ブラウザから確認する**

1. アドレスバーに `chrome://version` を入力
2. **Profile Path** を探す
3. `History` ファイルはそのディレクトリ内にあります

**方法 2：コマンドラインで検索する**

```bash
# 例：Atlas ブラウザを検索
find ~/Library/Application\ Support/com.openai.atlas/ -name "History" -type f
```

**一般的なパス例（macOS）：**

| ブラウザ | パス |
|--------|------|
| Chrome | `~/Library/Application Support/Google/Chrome/Default/History` |
| Dia | `~/Library/Application Support/Dia/User Data/Default/History` |
| Arc | `~/Library/Application Support/Arc/User Data/Default/History` |
| Atlas | `~/Library/Application Support/com.openai.atlas/browser-data/host/user-xxxxxxxxx/History` |
| Helium | `~/Library/Application Support/net.imput.helium/Default/History` |

### 2. エクスポートを実行する

```bash
# 直近 7 日分をエクスポート（デフォルト）
uv run export_chromium_history.py --path "/path/to/History"

# 直近 30 日分をエクスポート
uv run export_chromium_history.py --path "/path/to/History" --days 30
```

**パラメータの説明：**

| パラメータ | 説明 | デフォルト |
|------|------|--------|
| `--path` | History ファイルのパス | 必須 |
| `--days` | エクスポートする日数 | 7 |

### 3. 出力結果

エクスポート完了後、カレントディレクトリに `output_YYYYMMDD_HHMMSS/` フォルダが生成され、次の内容が含まれます：

```
output_20260128_195533/
├── BrowserHistory_001.json
├── BrowserHistory_002.json
└── ...
```

## Safari へのインポート

1. Safari を開く → **ファイル** → **ファイルまたはフォルダから閲覧データを読み込む...**
2. `output_*/` フォルダを選択（単一の JSON ファイルではなく、フォルダ全体を選択）
3. インポートを完了

## License

MIT
