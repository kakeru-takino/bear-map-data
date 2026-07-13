#!/usr/bin/env python3
"""KMLファイルをGoogle DriveのフォルダにOAuthでアップロードする。

個人のマイドライブに保存するため、サービスアカウントではなくOAuth
リフレッシュトークン方式を使う(SAは容量を持たずマイドライブへの新規
作成に失敗するため)。認証情報は環境変数から受け取る:

  GDRIVE_CLIENT_ID      OAuthクライアントID
  GDRIVE_CLIENT_SECRET  OAuthクライアントシークレット
  GDRIVE_REFRESH_TOKEN  事前に取得したリフレッシュトークン
  GDRIVE_FOLDER_ID      保存先フォルダのID(DriveのURLの folders/ 以降)

同名ファイルが既にフォルダにあれば内容を更新し、無ければ新規作成する。
これによりDrive側は常に「定位置の最新版」に保たれる。
"""
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def build_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GDRIVE_REFRESH_TOKEN"],
        client_id=os.environ["GDRIVE_CLIENT_ID"],
        client_secret=os.environ["GDRIVE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


def find_existing(service, folder_id: str, name: str):
    # 同名・未削除のファイルをフォルダ内から探す。名前のクォートに注意。
    safe = name.replace("'", r"\'")
    query = (
        f"name = '{safe}' and '{folder_id}' in parents and trashed = false"
    )
    resp = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    files = resp.get("files", [])
    return files[0]["id"] if files else None


def upload(service, folder_id: str, path: str) -> None:
    name = os.path.basename(path)
    media = MediaFileUpload(path, mimetype="application/vnd.google-earth.kml+xml")
    existing = find_existing(service, folder_id, name)
    if existing:
        service.files().update(fileId=existing, media_body=media).execute()
        print(f"{name}: 既存ファイルを更新 (id={existing})")
    else:
        meta = {"name": name, "parents": [folder_id]}
        created = (
            service.files().create(body=meta, media_body=media, fields="id").execute()
        )
        print(f"{name}: 新規作成 (id={created['id']})")


def main(paths) -> None:
    folder_id = os.environ["GDRIVE_FOLDER_ID"]
    service = build_service()
    for path in paths:
        if not os.path.exists(path):
            print(f"{path}: 見つからないためスキップ", file=sys.stderr)
            continue
        upload(service, folder_id, path)


if __name__ == "__main__":
    # 引数でアップロード対象ファイルを列挙する。
    main(sys.argv[1:])
