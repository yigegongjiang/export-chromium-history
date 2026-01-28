# export-chromium-history

从 Chromium 内核浏览器导出浏览历史记录，并转换为 Safari 可导入的格式。

## 背景

Chrome 及 Chromium 内核浏览器不支持直接导出浏览历史。本工具通过读取本地 `History` SQLite 数据库，将记录转换为 Safari 兼容的 JSON 格式，实现跨浏览器历史迁移。

| 迁移方向 | 方案 |
|----------|------|
| Chromium → Safari | 使用本工具导出 → Safari 导入 |
| Safari → Chromium | Chromium 内置导入功能 |

## 环境要求

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) 包管理器

## 使用方法

### 1. 定位 History 文件

Chromium 内核浏览器的历史记录存储在名为 `History` 的 SQLite 文件中。

**方法一：通过浏览器查看**

1. 地址栏输入 `chrome://version`
2. 找到 **Profile Path**
3. `History` 文件位于该目录下

**方法二：命令行搜索**

```bash
# 示例：搜索 Atlas 浏览器
find ~/Library/Application\ Support/com.openai.atlas/ -name "History" -type f
```

**常见路径参考（macOS）：**

| 浏览器 | 路径 |
|--------|------|
| Chrome | `~/Library/Application Support/Google/Chrome/Default/History` |
| Dia | `~/Library/Application Support/Dia/User Data/Default/History` |
| Arc | `~/Library/Application Support/Arc/User Data/Default/History` |
| Atlas | `~/Library/Application Support/com.openai.atlas/browser-data/host/user-xxxxxxxxx/History` |
| Helium | `~/Library/Application Support/net.imput.helium/Default/History` |

### 2. 执行导出

```bash
# 导出最近 7 天（默认）
uv run export_chromium_history.py --path "/path/to/History"

# 导出最近 30 天
uv run export_chromium_history.py --path "/path/to/History" --days 30
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--path` | History 文件路径 | 必填 |
| `--days` | 导出天数 | 7 |

### 3. 输出结果

导出完成后，当前目录下生成 `output_YYYYMMDD_HHMMSS/` 文件夹，包含：

```
output_20260128_195533/
├── BrowserHistory_001.json
├── BrowserHistory_002.json
└── ...
```

## 导入 Safari

1. 打开 Safari → **文件** → **从文件或文件夹导入浏览数据...**
2. 选择 `output_*/` 文件夹（选择整个文件夹，而非单个 JSON 文件）
3. 完成导入

## License

MIT
