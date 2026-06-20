# 🛰️ site-ops — リモート管制システム

全20サイトの死活監視・自動更新・自動修正を GitHub Actions で実行。
ブラウザだけで出張先から全操作可能。ローカルPC不要。

## 出張先での使い方

### 毎日やること：何もなし（全自動）

- **朝 8:00 / 夜 20:00** に全サイト自動チェック
- 問題あり → GitHub Issue 自動作成 → **メール通知が届く**
- 問題なし → 何も届かない（正常）
- ダッシュボードは自動更新される

### 状況確認したいとき

📊 **ダッシュボード** → https://jpn-x.github.io/site-ops/

### エラーが来たとき

1. メール or GitHub通知でアラートを確認
2. ダッシュボードでどのサイトか確認
3. 以下の修正アクションをブラウザから実行：

| やりたいこと | 手順 |
|-------------|------|
| データ更新を再実行 | [Actions → Trigger Site Update](https://github.com/jpn-x/site-ops/actions/workflows/trigger-update.yml) → Run workflow |
| サイトを再デプロイ | [Actions → Auto Fix](https://github.com/jpn-x/site-ops/actions/workflows/auto-fix.yml) → `re-deploy-pages` |
| キャッシュクリア＋再デプロイ | 同上 → `clear-cache-redeploy` |
| 今すぐヘルスチェック | [Actions → Site Health Check](https://github.com/jpn-x/site-ops/actions/workflows/health-check.yml) → Run workflow |

### もっと深い修正が必要なとき

**claude.ai/code** にアクセスして Claude Code を使う。
GitHub上で直接コード修正→コミット→自動デプロイも可能。

## 監視対象サイト（20サイト）

### 自動更新あり（平日）
- 日証金ダイジェスト（jpn-x/taisyaku-news）
- ストップ高・安一覧（stopstock/stop-data）

### ツール系
X高度検索 / 株クラNetwork / TDnet Web / ストップ高ギャップ分析 / TSE Watch / JRE車両管理 / 株スクリーナー / 株ストップ / Kabu Watch / IPOロックアップ / ワラント・レーダー

### ダッシュボード系
車保険 / Fund Board / Family Board / Holdings Radar / Kabu Tracker

### ポータル
My Works / Tool Directory

## 技術構成

```
GitHub Actions (cron: 毎日2回)
  → 全サイトHTTP監視
  → 自動更新ワークフロー状態チェック
  → ダッシュボード自動生成 (GitHub Pages)
  → エラー時 GitHub Issue 自動作成 → メール通知
```

| Secret | 用途 |
|--------|------|
| `OPS_TOKEN` | 他org操作用 GitHub Token（設定済み） |
