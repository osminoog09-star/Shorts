"""One-time local OAuth helper. Never commit its output or put tokens in chat.
Run on your own computer. Requires google-auth-oauthlib.
Create a Google Cloud Desktop OAuth client, enable YouTube Data API v3,
and download its client JSON locally. Do NOT upload that JSON to this repo.
"""
import argparse,getpass,json,sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
import requests
p=argparse.ArgumentParser();p.add_argument('--client',required=True,help='Path to private Desktop OAuth client JSON');p.add_argument('--lang',required=True,choices=['ru','en']);a=p.parse_args()
f=InstalledAppFlow.from_client_secrets_file(a.client,['https://www.googleapis.com/auth/youtube.upload','https://www.googleapis.com/auth/youtube.readonly'])
c=f.run_local_server(port=0,access_type='offline',prompt='consent select_account',open_browser=True)
r=requests.get('https://www.googleapis.com/youtube/v3/channels',params={'part':'snippet','mine':'true'},headers={'Authorization':'Bearer '+c.token},timeout=40);r.raise_for_status()
for channel in r.json().get('items',[]):print('Confirmed channel:',channel['id'],channel['snippet']['title'])
if not c.refresh_token:sys.exit('No refresh token. Revoke the old consent, then repeat on your own computer.')
print('\nKeep the following value private. Add it as GitHub Actions secret YOUTUBE_REFRESH_TOKEN_'+a.lang.upper()+'. Do not paste it into chat or a public repository.')
print(c.refresh_token)
