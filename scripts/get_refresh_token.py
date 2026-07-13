#!/usr/bin/env python3
"""OAuthリフレッシュトークンをローカルで一度だけ取得するヘルパー。

Google CloudでOAuthクライアント(種類: デスクトップアプリ)を作成し、
その client_secret_*.json をダウンロードしてから実行する:

  pip install google-auth-oauthlib
  python3 scripts/get_refresh_token.py path/to/client_secret.json

ブラウザが開いてGoogleアカウントで許可すると、コンソールに
CLIENT_ID / CLIENT_SECRET / REFRESH_TOKEN が表示される。これらを
GitHubのリポジトリSecretsに登録する。取得後このスクリプトと鍵JSONは
コミットしない(リポジトリに含めない)こと。
"""
import sys

from google_auth_oauthlib.flow import InstalledAppFlow

# drive.file: このアプリが作成/開いたファイルだけに限定した最小権限。
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def main(client_secret_path: str) -> None:
    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
    # ローカルサーバでコールバックを受け、access_type=offlineでrefresh_tokenを得る。
    creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

    print("\n=== GitHub Secrets に登録する値 ===")
    print(f"GDRIVE_CLIENT_ID     = {creds.client_id}")
    print(f"GDRIVE_CLIENT_SECRET = {creds.client_secret}")
    print(f"GDRIVE_REFRESH_TOKEN = {creds.refresh_token}")
    print("\nGDRIVE_FOLDER_ID は保存先フォルダのURL(folders/以降)を別途登録。")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使い方: python3 scripts/get_refresh_token.py client_secret.json")
        sys.exit(1)
    main(sys.argv[1])
