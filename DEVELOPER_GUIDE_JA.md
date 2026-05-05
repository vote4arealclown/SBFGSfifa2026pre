# 開発者ガイド — Smart Bet Field Guide System 2026

> **コントリビューター、メンテナー、およびプラットフォームを拡張したい方のためのガイド。**

---

## 目次

1. [アーキテクチャ概要](#アーキテクチャ概要)
2. [開発環境構築](#開発環境構築)
3. [データベース層](#データベース層)
4. [データ取り込みパイプライン](#データ取り込みパイプライン)
5. [新規データソースの追加](#新規データソースの追加)
6. [レポートモジュール](#レポートモジュール)
7. [ベッティングユーティリティ](#ベッティングユーティリティ)
8. [TUI開発](#tui開発)
9. [CLI開発](#cli開発)
10. [テストと検証](#テストと検証)
11. [リリースチェックリスト](#リリースチェックリスト)

---

## アーキテクチャ概要

```
┌─────────────────────────────────────────────────────────────┐
│                        プレゼンテーション層                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  TUI         │  │  CLI         │  │  Jupyter     │      │
│  │  (Textual)   │  │  (argparse)  │  │  (pandas)    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                      ビジネスロジック層                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  reports.py  │  │betting_utils │  │  seed_field  │      │
│  │  (クエリ)    │  │  (オッズ,EV) │  │  _guide.py   │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────┐
│                        データ層                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SQLite (fifa2026_repo.db)               │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │    │
│  │  │ players │ │ matches │ │ events  │ │  venues  │  │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐  │    │
│  │  │  tiers  │ │ penalty │ │scenarios│ │glossary  │  │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └──────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                      データソース                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Historical   │  │ Field Guide  │  │  Future:     │      │
│  │ Open Data    │  │  Reference   │  │  Odds API,   │      │
│  │  (2022 WC)   │  │   (manual)   │  │  Weather,    │      │
│  │              │  │              │  │  Transferm.  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 設計原則

1. **ローカルファースト:** すべてがあなたのマシン上で動作します。コアデータセットにAPIキーは不要です。
2. **モジュール化:** 各モジュールは単一の責任を持ちます。`ingest_data.py`を別のデータソースに差し替えてもUIに触れる必要はありません。
3. **SQLite:** ゼロ構成のデータベース。Docker、Postgres、クラウドは不要です。
4. **拡張性:** 新しいレポート、テーブル、データソースがクリーンに追加できます。

---

## 開発環境構築

### 前提条件

- Python 3.10以上
- `make`（任意、Makefileの便利機能用）
- `uv` または `pip`（パッケージ管理用）

### 開発セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/sbfg2026.git
cd sbfg2026

# 仮想環境を作成
python3 -m venv .venv
source .venv/bin/activate

# すべての追加機能付きで編集可能モードでインストール
pip install -e ".[analytics,notebook,dev]"

# リファレンスデータを登録
python src/seed_field_guide.py

# テストを実行
make test
```

### プロジェクトレイアウト規約

```
src/
  database.py            # スキーマ + 接続（ビジネスロジックなし）
  ingest_<source>.py     # 外部データソースごとに1ファイル
  seed_<domain>.py       # リファレンスデータドメインごとに1ファイル
  reports.py             # すべてのSQLクエリはpandas DataFrameを返す
  betting_utils.py       # 純粋関数、副作用なし
  cli.py                 # argparseコマンドがreports + utilsを呼び出す
  tui_app.py             # Textual画面がreports + utilsを構成する
  i18n.py                # 多言語対応（EN/ES/JA）
```

---

## データベース層

### 新規テーブルの追加

1. `database.py`の`SCHEMA_SQL`に`CREATE TABLE`文を追加。
2. `python src/database.py`を実行してスキーマを適用。
3. `seed_*.py`スクリプトにシードデータを追加。
4. `reports.py`にレポート関数を追加。
5. CLI（`cli.py`）とTUI（`tui_app.py`）に接続。

### 接続管理

常にコンテキストマネージャーを使用してください：

```python
from database import get_connection

with get_connection() as conn:
    rows = conn.execute("SELECT * FROM players WHERE goals > 5").fetchall()
    for row in rows:
        print(dict(row))
```

コンテキストマネージャーは自動的に以下を処理します：
- `sqlite3.Row`ファクトリー（辞書風アクセス）
- 接続クリーンアップ

---

## データ取り込みパイプライン

### 新規データソースの追加

`src/ingest_<source>.py`を以下のパターンに従って作成：

```python
"""<Source Name>からデータを取り込む。"""

from database import execute_many, get_connection

SOURCE_ID = "my_source"

def ingest_my_source(db_path=None):
    print(f"[1/1] {SOURCE_ID}から取り込み中...")
    # データ取得
    records = []
    # ... 変換 ...
    query = "INSERT OR REPLACE INTO my_table (...) VALUES (?, ?)"
    execute_many(query, records, db_path)
    print(f"  -> {len(records)} 件取り込み完了")

def run_full_ingestion(db_path=None):
    from database import init_database
    db = init_database(db_path)
    ingest_my_source(db)
    return db

if __name__ == "__main__":
    run_full_ingestion()
```

---

## レポートモジュール

### 規約

すべてのレポート関数は：
1. `pandas.DataFrame`を返す
2. SQL→DataFrame変換に`_df_from_query()`を使用
3. オプションの`db_path`パラメータを受け入れる
4. 記述的な名前を持つ：`report_<what>_<filter>()`

### TUIへのレポート追加

1. `reports.py`にレポート関数を作成。
2. `tui_app.py`に`ReportScreen`プッシュを追加：

```python
def action_show_my_report(self) -> None:
    self.app.push_screen(ReportScreen("My Report", report_players_by_cards(3)))
```

3. `MainScreen.BINDINGS`にキーバインディングを追加：

```python
Binding("m", "show_my_report", "My Report"),
```

4. `MainScreen.compose()`にメニュー項目を追加：

```python
yield Static("[b]m[/b]  My Report", classes="menu-item")
```

---

## ベッティングユーティリティ

すべてのベッティングユーティリティは**純粋関数**です（データベースアクセスなし、副作用なし）。これにより、CLI、TUI、ノートブック全体でテスト可能かつ再利用可能になります。

### オッズ変換

```python
from betting_utils import parse_odds

odds = parse_odds("+150")
print(odds.decimal)        # 2.500
print(odds.american)       # 150
print(odds.implied_prob)   # 0.400
```

### ケリー基準

```python
from betting_utils import kelly_criterion

stake_pct, recommendation = kelly_criterion(
    model_prob=0.45,      # あなたの推定確率
    odds_decimal=2.20,    # 提供されている小数オッズ
    fraction=0.25         # クォーターケリー（保守的）
)
# 返り値: (0.0156, "Weak edge—bet 1.56% of bankroll or pass")
```

---

## TUI開発

### Textualフレームワーク

TUIは[Textual](https://textual.textualize.io/)を使用しています。これはターミナルアプリ向けのモダンなPythonフレームワークです。

### 多言語対応（i18n）

すべてのUI文字列は`src/i18n.py`に集約されています。新しい言語を追加するには：

1. `_TRANSLATIONS`に新しいトップレベルキーを追加（例：`"ja"`）。
2. `_COLUMN_MAP`に列マッピングを追加。
3. `python src/tui_app.py --lang ja`で起動。

現在サポートされている言語：
- `en` — 英語
- `es` — スペイン語
- `ja` — 日本語

### 画面タイプ

| 画面 | 用途 |
|:---|:---|
| `ReportScreen` | 任意のpandas DataFrame |
| `PlayerDetailScreen` | 選手の完全プロフィール（Markdownレンダリング） |
| `SearchScreen` | 入力 + 結果テーブル |
| `VenueScreen` | 会場データテーブル |
| `MarkdownReportScreen` | 静的Markdownコンテンツ |

### 開発モードでのTUI実行

Textualには組み込みの開発者コンソールがあります：

```bash
textual run --dev src/tui_app.py
```

これにより、DOMインスペクタとCSSホットリロード付きの別コンソールウィンドウが開きます。

---

## CLI開発

### 新規コマンドの追加

1. ハンドラ関数を記述：

```python
def cmd_my_command(args):
    df = report_my_report(args.limit)
    print(tabulate(df, headers="keys", tablefmt="grid", showindex=False))
```

2. サブパーサーを登録：

```python
p = subparsers.add_parser("mycommand", help="Description")
p.add_argument("--limit", type=int, default=20)
p.set_defaults(func=cmd_my_command)
```

3. テスト：

```bash
.venv/bin/python src/cli.py mycommand --limit 10
```

---

## テストと検証

### 手動検証

```bash
make test          # 基本的なインポート + 件数検証
python src/cli.py counts   # すべてのテーブルが投入されたことを確認
```

### データ品質チェック

任意の取り込み後に以下のクエリを実行：

```sql
-- 出場時間があるがゴールがない選手（多数であるべき）
SELECT COUNT(*) FROM players WHERE minutes_played > 0;

-- xGがあるがゴールがない選手（未達成選手）
SELECT player_name, goals, xg FROM players WHERE xg > 2 AND goals = 0;

-- イベントがない試合（0であるべき）
SELECT COUNT(*) FROM matches m WHERE NOT EXISTS (
    SELECT 1 FROM match_events e WHERE e.match_id = m.match_id
);
```

---

## リリースチェックリスト

gitにプッシュまたはリリースする前に：

- [ ] `make test`がパスする
- [ ] `make reports`ですべての16個のCSVファイルが生成される
- [ ] `./tui.sh`と`./tui_es.sh`と`./tui_ja.sh`が起動し、すべての画面が正しく遷移する
- [ ] `src/cli.py counts`が期待される件数を表示する
- [ ] READMEが最新である
- [ ] DEVELOPER_GUIDEが現在のアーキテクチャを反映している
- [ ] `.gitignore`が`data/*.db`、`reports/*.csv`、`.venv/`を除外している
- [ ] `pyproject.toml`のバージョンが必要に応じて更新されている
- [ ] ソースにハードコードされたパスやAPIキーがない

---

## 貢献

1. リポジトリをフォーク
2. フィーチャーブランチを作成：`git checkout -b feature/my-feature`
3. 変更を加える
4. リリースチェックリストを実行
5. プルリクエストを送信

質問がある場合は、issueを開くかメンテナーに連絡してください。

---

*最終更新日: 2026-05-05*
