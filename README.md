# site-ops

全サイトのリモート管制システム。GitHub Actions + GitHub Pages で構成。

## セットアップ

### 1. リポジトリ作成後、Secretsを設定

Settings → Secrets and variables → Actions に以下を追加:

| Secret | 説明 |
|--------|------|
| `OPS_TOKEN` | GitHub PAT（`repo`, `workflow` スコープ。他orgリポジトリへのアクセス権含む） |
| `MAIL_USERNAME` | Gmail アドレス（送信元） |
| `MAIL_PASSWORD` | Gmail アプリパスワード（2段階認証 → アプリパスワード生成） |
| `NOTIFY_EMAIL` | 通知先メールアドレス |

### 2. GitHub Pages を有効化

Settings → Pages → Source: `Deploy from a branch` → Branch: `main` / `docs`

### 3. 初回実行

Actions → Site Health Check → Run workflow

## ワークフロー

| ワークフロー | 用途 | トリガー |
|-------------|------|---------|
| `health-check.yml` | 全サイト死活監視 + ダッシュボード更新 | 毎日 8:00/20:00 JST + 手動 |
| `trigger-update.yml` | データ更新系サイトの手動更新 | 手動（対象選択可） |
| `auto-fix.yml` | 修正アクション実行 | 手動（リポジトリ・修正タイプ選択） |

## ダッシュボード

https://jpn-x.github.io/site-ops/
