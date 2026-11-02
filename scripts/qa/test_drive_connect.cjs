// Offline safety and UI regression for Drive Google sign-in.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const root = path.join(__dirname,"..","..");
const script = fs.readFileSync(path.join(root,"site/studio/drive_connect.js"),"utf8");
const page = fs.readFileSync(path.join(root,"site/studio/index.html"),"utf8");
const pages = fs.readFileSync(path.join(root,".github/workflows/motion-pages.yml"),"utf8");
const flow = fs.readFileSync(path.join(root,".github/workflows/drive-oauth-exchange.yml"),"utf8");
new vm.Script(script,{filename:"site/studio/drive_connect.js"});
assert.match(page,/<script src="drive_connect\.js"><\/script>/);
for (const id of ["driveGoogleStart","driveAuthCode","driveGoogleFinish","driveConnectStatus"])
  assert.match(page,new RegExp('id="'+id+'"'),id+" not present");
assert.match(script,/https:\/\/accounts\.google\.com\/o\/oauth2\/v2\/auth/);
assert.match(script,/redirect_uri","https:\/\/developers\.google\.com\/oauthplayground/);
assert.match(script,/GDRIVE_AUTH_CODE/);
assert.match(script,/encrypted_value:status\.encrypted_value,key_id:status\.key_id/);
assert.match(script,/GDRIVE_REFRESH_TOKEN/);
assert.match(script,/sessionStorage\.setItem\(NONCE_KEY/);
assert.doesNotMatch(script,/localStorage\.setItem\([^,]+,\s*(code|refresh|token)\b/);
assert.match(flow,/GDRIVE_AUTH_CODE:\s*\$\{\{ secrets\.GDRIVE_AUTH_CODE \}\}/);
assert.match(flow,/python3 -m scripts\.drive_oauth_exchange/);
assert.match(pages,/node --check site\/studio\/drive_connect\.js/);
assert.match(pages,/PUBLIC_GOOGLE_CLIENT_ID: \$\{\{ secrets\.YOUTUBE_OAUTH_CLIENT_ID \}\}/);
assert.match(pages,/_site\/studio\/google_client\.json/);
console.log("Google Drive consent UI safety PASS");
