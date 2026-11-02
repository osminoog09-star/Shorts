#!/usr/bin/env python3
"""Read-only audit of existing GitHub OAuth coverage.

Never prints tokens, credential material or sensitive scope strings.
Returns 0 even on unavailable network because this is a diagnostic,
not evidence that an upload worked.
"""
import json
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen

def drive_usable_with_youtube_auth(environ, post=None):
    cid = environ.get("YOUTUBE_OAUTH_CLIENT_ID") or environ.get("YT_CLIENT_ID")
    secret = environ.get("YOUTUBE_OAUTH_CLIENT_SECRET") or environ.get("YT_CLIENT_SECRET")
    refresh = environ.get("YOUTUBE_REFRESH_TOKEN_RU") or environ.get("YT_REFRESH_TOKEN")
    if not all((cid,secret,refresh)):
        return "not_configured"
    def send(url,data):
        req=Request(url,data=urlencode(data).encode(),headers={"Content-Type":"application/x-www-form-urlencoded"},method="POST")
        with urlopen(req,timeout=18) as res:
            return json.load(res)
    try:
        token=send("https://oauth2.googleapis.com/token",{
            "client_id":cid,"client_secret":secret,"refresh_token":refresh,"grant_type":"refresh_token"
        })
        at=token.get("access_token")
        if not at:return "auth_failed"
        req=Request("https://oauth2.googleapis.com/tokeninfo?"+urlencode({"access_token":at}))
        with urlopen(req,timeout=18) as res:
            info=json.load(res)
        scopes=set(info.get("scope","").split())
        if "https://www.googleapis.com/auth/drive" in scopes:
            return "granted_full"
        return "no_drive_scope"
    except Exception:
        return "auth_or_network_unavailable"

def main():
    env=os.environ
    out={
      "rclone_credential_preexisting":bool(env.get("GDRIVE_RCLONE_CONFIG")),
      "drive_refresh_token_preexisting":bool(env.get("GDRIVE_REFRESH_TOKEN")),
      "youtube_oauth_client_preexisting":bool(env.get("YOUTUBE_OAUTH_CLIENT_ID") or env.get("YT_CLIENT_ID")) and bool(env.get("YOUTUBE_OAUTH_CLIENT_SECRET") or env.get("YT_CLIENT_SECRET")),
      "youtube_token_drive_scope":drive_usable_with_youtube_auth(env),
    }
    print("Drive credential audit (presence/scope only): "+json.dumps(out,sort_keys=True))
if __name__=="__main__":
    main()
