#!/usr/bin/env bash
#
# Upload the 193 reveal photos to the Cloudflare R2 bucket that backs cdn.goodtohearthename.co.uk.
# Photos are served at  https://cdn.goodtohearthename.co.uk/images/<id>.jpg  (see RemoteImageCache
# on Android / RemotePhotoCache on iOS). Silhouettes stay bundled and are NOT uploaded.
#
# One-time Cloudflare setup (dashboard, ~15 min) — see REMOTE_IMAGES_SETUP.md:
#   1. R2 -> Create bucket (e.g. "gthn-photos").
#   2. Bucket -> Settings -> Public access -> connect custom domain "cdn.goodtohearthename.co.uk".
#   3. R2 -> Manage API Tokens -> create a token with Object Read & Write for that bucket.
#
# Then export these and run this script:
#   export R2_ACCOUNT_ID=xxxxxxxxxxxxxxxx
#   export R2_BUCKET=gthn-photos
#   export AWS_ACCESS_KEY_ID=<R2 token access key id>
#   export AWS_SECRET_ACCESS_KEY=<R2 token secret>
#   scripts/upload_photos_r2.sh
#
# Requires the AWS CLI (`brew install awscli`). R2 is S3-compatible.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/app/src/main/assets/images"     # complete, canonical set (all 193 referenced photos)
CONTENT="$ROOT/app/src/main/assets/content.json"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

: "${R2_ACCOUNT_ID:?set R2_ACCOUNT_ID}"
: "${R2_BUCKET:?set R2_BUCKET}"
: "${AWS_ACCESS_KEY_ID:?set AWS_ACCESS_KEY_ID (R2 token)}"
: "${AWS_SECRET_ACCESS_KEY:?set AWS_SECRET_ACCESS_KEY (R2 token)}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-auto}"   # R2 expects a region; "auto" works
ENDPOINT="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Stage only the photos actually referenced by content.json (skips orphan files).
python3 - "$CONTENT" "$SRC" "$STAGE" <<'PY'
import json, os, shutil, sys
content, src, stage = sys.argv[1], sys.argv[2], sys.argv[3]
players = json.load(open(content))["footballers"]
missing = []
for p in players:
    f = p["image"]
    s = os.path.join(src, f)
    if os.path.exists(s):
        shutil.copy2(s, os.path.join(stage, f))
    else:
        missing.append(f)
print(f"staged {len(players)-len(missing)}/{len(players)} photos")
if missing:
    print("MISSING (fix before upload):", missing); sys.exit(1)
PY

# Sync to R2. Long immutable cache since filenames are stable; if a photo is ever REPLACED,
# use a versioned filename (<id>_v2.jpg) and update content.json rather than shortening this.
aws s3 sync "$STAGE/" "s3://${R2_BUCKET}/images/" \
  --endpoint-url "$ENDPOINT" \
  --content-type "image/jpeg" \
  --cache-control "public, max-age=31536000, immutable" \
  --size-only

echo "Done. Spot-check: https://cdn.goodtohearthename.co.uk/images/steve_bruce.jpg"
