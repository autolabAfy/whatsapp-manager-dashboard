"""
Sync files from GitHub repo into local workspace.
Run this whenever Claude Code has pushed new changes to GitHub.
Usage: python scripts/sync_from_github.py
"""
import urllib.request, urllib.error, json, os, base64

TOKEN = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN', '')
REPO  = 'autolabAfy/zeus-client-app'
ROOT  = '/home/runner/workspace'

# Files/dirs to never overwrite from GitHub (Replit-managed)
SKIP = {'data/', '.replit', 'scripts/post-merge.sh'}

HEADERS = {
    'Authorization': f'token {TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def gh(path):
    req = urllib.request.Request(f'https://api.github.com{path}', headers=HEADERS)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def should_skip(path):
    for s in SKIP:
        if path == s or path.startswith(s):
            return True
    return False

# Get latest commit
branch = gh(f'/repos/{REPO}/branches/main')
sha    = branch['commit']['sha']
msg    = branch['commit']['commit']['message'].split('\n')[0]
print(f'GitHub main: {sha[:10]} — {msg[:65]}')
print()

# Get full tree
tree  = gh(f'/repos/{REPO}/git/trees/{sha}?recursive=1')
blobs = [(f['path'], f['sha']) for f in tree['tree'] if f['type'] == 'blob']

updated = []
skipped = []

for path, blob_sha in blobs:
    if should_skip(path):
        skipped.append(path)
        continue

    # Fetch file content
    file_data = gh(f'/repos/{REPO}/contents/{path}?ref={sha}')
    gh_content = base64.b64decode(file_data['content'])

    local_path = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    # Compare with local
    if os.path.exists(local_path):
        with open(local_path, 'rb') as f:
            local_content = f.read()
        if local_content == gh_content:
            continue  # No change

    with open(local_path, 'wb') as f:
        f.write(gh_content)
    updated.append(path)
    print(f'  UPDATED  {path}')

if not updated:
    print('  Everything already up to date.')

if skipped:
    print(f'\n  Skipped (Replit-managed): {", ".join(skipped)}')

print(f'\nDone. {len(updated)} file(s) updated.')
