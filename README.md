# export-chromium-history

Export browsing history from Chromium-based browsers and convert it into a Safari-importable format.

## Background

Chrome and Chromium-based browsers do not provide a direct way to export browsing history. This tool reads the local `History` SQLite database and converts records into a Safari-compatible JSON format, enabling cross-browser history migration.

| Migration Direction | Approach |
|----------|------|
| Chromium → Safari | Export with this tool → Import into Safari |
| Safari → Chromium | Use Chromium's built-in import feature |

## Requirements

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) package manager

## Usage

### 1. Locate the History file

Chromium-based browsers store their browsing history in a SQLite file named `History`.

**Method 1: Check in the browser**

1. Enter `chrome://version` in the address bar
2. Find **Profile Path**
3. The `History` file is located in that directory

**Method 2: Search from the command line**

```bash
# Example: search for Atlas browser
find ~/Library/Application\ Support/com.openai.atlas/ -name "History" -type f
```

**Common paths (macOS):**

| Browser | Path |
|--------|------|
| Chrome | `~/Library/Application Support/Google/Chrome/Default/History` |
| Dia | `~/Library/Application Support/Dia/User Data/Default/History` |
| Arc | `~/Library/Application Support/Arc/User Data/Default/History` |
| Atlas | `~/Library/Application Support/com.openai.atlas/browser-data/host/user-xxxxxxxxx/History` |
| Helium | `~/Library/Application Support/net.imput.helium/Default/History` |

### 2. Run the export

```bash
# Export the last 7 days (default)
uv run export_chromium_history.py --path "/path/to/History"

# Export the last 30 days
uv run export_chromium_history.py --path "/path/to/History" --days 30
```

**Parameters:**

| Parameter | Description | Default |
|------|------|--------|
| `--path` | Path to the History file | Required |
| `--days` | Number of days to export | 7 |

### 3. Output

After the export completes, an `output_YYYYMMDD_HHMMSS/` folder is created in the current directory, containing:

```
output_20260128_195533/
├── BrowserHistory_001.json
├── BrowserHistory_002.json
└── ...
```

## Import into Safari

1. Open Safari → **File** → **Import Browsing Data from File or Folder...**
2. Select the `output_*/` folder (select the whole folder, not a single JSON file)
3. Finish the import

## License

MIT
