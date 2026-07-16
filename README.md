# iPhone 年間進捗壁紙 — 完全自動更新版

毎朝、GitHub Actionsがその日の壁紙を生成し、iPhoneのショートカットが画像を取得してロック画面へ設定します。

## 全体構成

1. GitHub Actions：毎日 04:35（日本時間）ごろに `output/latest.png` を更新
2. iPhoneショートカット：毎日 05:00以降に画像URLを取得
3. 「壁紙を設定」アクション：ロック画面へ自動設定

GitHub Actionsの予約実行は数分以上遅れる場合があります。iPhone側は05:15〜05:30にすると安定します。

---

## 1. GitHubに置く

1. GitHubで新しい **Public** リポジトリを作る  
   例：`iphone-year-wallpaper`
2. このフォルダの中身を、そのリポジトリへアップロードする
3. GitHubのリポジトリで **Actions** タブを開き、ワークフローを有効化する
4. `Update iPhone wallpaper` を開き、`Run workflow` を1回実行する
5. 数分後、`output/latest.png` が更新されていることを確認する

### 画像URL

以下の形式です。

`https://raw.githubusercontent.com/GITHUBユーザー名/リポジトリ名/main/output/latest.png`

例：

`https://raw.githubusercontent.com/example/iphone-year-wallpaper/main/output/latest.png`

このURLをSafariで開き、画像が表示されれば準備完了です。

---

## 2. iPhoneショートカットを作る

ショートカット名：`年間進捗壁紙を更新`

アクションを次の順番で追加します。

1. **URL**
   - 上記の `raw.githubusercontent.com/.../output/latest.png` を入力
2. **URLの内容を取得**
   - 方法：`GET`
3. **壁紙を設定**
   - 壁紙：現在のロック画面、または更新したい壁紙ペアを選択
   - 「プレビューを表示」をオフ
   - 画像の切り抜き・拡大が起きる場合は、壁紙設定側で「被写界深度」や拡張をオフ
4. 必要なら **通知を表示**
   - 最初の動作確認時だけ追加し、確認後は削除

※ iOSの表示名により「壁紙を設定」「壁紙写真を設定」など若干名称が異なる場合があります。

最初にショートカットを手動実行し、ネットワーク・写真・壁紙へのアクセスを「常に許可」してください。

---

## 3. 毎朝のオートメーション

1. ショートカットアプリ → **オートメーション**
2. `＋` → **時刻**
3. 時刻：`05:20`
4. 繰り返し：`毎日`
5. 実行内容：`年間進捗壁紙を更新`を実行
6. **すぐに実行**を選択  
   旧表示では「実行の前に尋ねる」をオフ
7. 実行時の通知も不要ならオフ

---

## 4. PCで試す

```bash
pip install -r requirements.txt
python generate_wallpaper.py
```

任意の日付で確認：

```bash
python generate_wallpaper.py --date 2026-12-31 --output output/test.png
```

---

## 5. デザイン変更

`generate_wallpaper.py` の上部で変更できます。

- `WIDTH`, `HEIGHT`：画像サイズ
- `BG`, `WHITE`, `GOLD`：色
- `start_y`：365日グリッドの上下位置
- フッター文言：`今日も、未来の自分への投資。`

現在の解像度は iPhone 14 / 13 / 12 系に合わせた `1170 × 2532` です。
別機種でも壁紙設定時に軽くトリミングされるだけで利用できます。

---

## 注意

- GitHubリポジトリをPublicにすると、生成画像はURLを知っている人が閲覧できます。ただし個人情報は含みません。
- Privateリポジトリのraw画像をショートカットから取得するには認証が必要なため、この構成ではPublicを推奨します。
- GitHub Actionsのcronは厳密な時刻保証ではありません。更新遅延を避けるため、画像生成を04:35、iPhone更新を05:20にずらしています。
