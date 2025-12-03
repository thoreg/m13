"""Upload local database dump to dropbox."""

import dropbox
import sys
import os
from pathlib import Path

from dotenv import load_dotenv


def oauth_dance(DROPBOX_APP_KEY, DROPBOX_APP_SECRET):
    auth_flow = dropbox.DropboxOAuth2FlowNoRedirect(
        DROPBOX_APP_KEY,
        DROPBOX_APP_SECRET,
        token_access_type="offline",  # offline => Refresh-Token
    )
    authorize_url = auth_flow.start()
    print("1. Open this url in browser:\n", authorize_url)
    print("2. Login and copy code to insert it here::")

    auth_code = input("Code: ").strip()
    oauth_result = auth_flow.finish(auth_code)
    print("\nAccess-Token:", oauth_result.access_token)
    print("Refresh-Token:", oauth_result.refresh_token)


def main():
    print("starting ... backup-dropbox!")

    if len(sys.argv) < 2:
        print("Error: 2 params required.")
        print(f"Usage: {sys.argv[0]} <parameter>")
        sys.exit(1)

    dump_name = sys.argv[1]
    print(f"dump name: {dump_name}")

    load_dotenv()

    DROPBOX_APP_KEY = os.environ["DROPBOX_APP_KEY"]
    DROPBOX_APP_SECRET = os.environ["DROPBOX_APP_SECRET"]
    DROPBOX_REFRESH_TOKEN = os.environ["DROPBOX_REFRESH_TOKEN"]

    # oauth_dance(DROPBOX_APP_KEY, DROPBOX_APP_SECRET)
    # return

    # sdk deals with token refresh under the hood
    dbx = dropbox.Dropbox(
        oauth2_refresh_token=DROPBOX_REFRESH_TOKEN,
        app_key=DROPBOX_APP_KEY,
        app_secret=DROPBOX_APP_SECRET,
    )

    # print(dbx.users_get_current_account())

    # local path to dump
    local_path = Path(dump_name)

    # remote path of the target in dropbox
    base_name = os.path.basename(dump_name)
    dropbox_path = f"/m13bm/dumps/{base_name}"

    with local_path.open("rb") as f:
        dbx.files_upload(
            f.read(),
            dropbox_path,
            mode=dropbox.files.WriteMode("overwrite"),
            mute=True,  # optional: no notification
        )

    print(f"✅ upload successful {dropbox_path}")


if __name__ == "__main__":
    main()
