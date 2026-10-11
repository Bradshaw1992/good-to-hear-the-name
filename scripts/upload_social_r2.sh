#!/usr/bin/env bash
#
# Upload the IG/Facebook photo-post images to the Cloudflare R2 bucket that backs
# cdn.goodtohearthename.co.uk, so a bulk scheduler (Metricool/Publer) can fetch them by URL.
# Served at:  https://cdn.goodtohearthename.co.uk/social/<file>.jpg
#
# Uses the SAME bucket + credentials as scripts/upload_photos_r2.sh (the reveal photos).
# Export the same four env vars, then run:
#   export R2_ACCOUNT_ID=xxxxxxxxxxxxxxxx
#   export R2_BUCKET=gthn-photos
#   export AWS_ACCESS_KEY_ID=<R2 token access key id>
#   export AWS_SECRET_ACCESS_KEY=<R2 token secret>
#   scripts/upload_social_r2.sh
#
# Requires the AWS CLI (`brew install awscli`). R2 is S3-compatible.
# These images are silhouette + text only (no real player photos), so they are safe to host.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/marketing_print/instagram_posts"

: "${R2_ACCOUNT_ID:?set R2_ACCOUNT_ID}"
: "${R2_BUCKET:?set R2_BUCKET}"
: "${AWS_ACCESS_KEY_ID:?set AWS_ACCESS_KEY_ID (R2 token)}"
: "${AWS_SECRET_ACCESS_KEY:?set AWS_SECRET_ACCESS_KEY (R2 token)}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-auto}"
ENDPOINT="https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Only the .jpg post images; skip captions.md / schedule .txt etc.
aws s3 sync "$SRC/" "s3://${R2_BUCKET}/social/" \
  --exclude "*" --include "*.jpg" \
  --endpoint-url "$ENDPOINT" \
  --content-type "image/jpeg" \
  --cache-control "public, max-age=604800" \
  --size-only

echo "Done. Spot-check: https://cdn.goodtohearthename.co.uk/social/day124_tomas_rosicky.jpg"
