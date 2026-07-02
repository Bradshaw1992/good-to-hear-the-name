#!/usr/bin/env python3
"""Generate the daily 1080x1080 silhouette card and cross-post to X + Bluesky.

Single source of truth: same image, same caption, identical timing.

Usage:
    # Dry run — generate image + print caption, do NOT post:
    scripts/.venv/bin/python scripts/make_daily_post.py --player oscar_brazil --day 40 --dry-run

    # Live post to both:
    scripts/.venv/bin/python scripts/make_daily_post.py --player oscar_brazil --day 40

    # Single network:
    scripts/.venv/bin/python scripts/make_daily_post.py --player oscar_brazil --day 40 --only x
    scripts/.venv/bin/python scripts/make_daily_post.py --player oscar_brazil --day 40 --only bluesky

    # Archive reveal style (past day):
    scripts/.venv/bin/python scripts/make_daily_post.py --player ramires --day 36 --archive

Setup once:
    scripts/.venv/bin/pip install tweepy atproto python-dotenv
    cp scripts/.env.example scripts/.env  # then fill in keys
"""
import argparse
import os
import sys

from make_instagram_posts import (
    build_post,
    caption_for,
    hashtags_for,
    load_players,
    OUT as IG_OUT,
    SILS,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(env_path):
        return
    for line in open(env_path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


def post_caption(player, day, is_today):
    """Short caption tuned for X (280) + Bluesky (300). IG uses the full one."""
    pinned = f"https://goodtohearthename.co.uk?day={day}"
    if is_today:
        return (
            f"Day {day}. Today's puzzle.\n\n"
            f"Five clues. Five guesses. Most people need three.\n\n"
            f"Play: {pinned}"
        )
    return (
        f"Day {day} from the archive.\n\n"
        f"Five clues. Five guesses. Most people need three.\n\n"
        f"Play this exact puzzle: {pinned}"
    )


def post_to_x(image_path, text):
    import tweepy
    keys = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
    missing = [k for k in keys if not os.environ.get(k)]
    if missing:
        raise RuntimeError(f"Missing X env vars: {missing}")

    auth = tweepy.OAuth1UserHandler(
        os.environ["X_API_KEY"], os.environ["X_API_SECRET"],
        os.environ["X_ACCESS_TOKEN"], os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    v1 = tweepy.API(auth)
    media = v1.media_upload(image_path)

    v2 = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    resp = v2.create_tweet(text=text, media_ids=[media.media_id])
    tweet_id = resp.data["id"]
    return f"https://x.com/i/web/status/{tweet_id}"


def post_to_bluesky(image_path, text):
    from atproto import Client, client_utils, models
    handle = os.environ.get("BLUESKY_HANDLE")
    pw = os.environ.get("BLUESKY_APP_PASSWORD")
    if not handle or not pw:
        raise RuntimeError("Missing BLUESKY_HANDLE / BLUESKY_APP_PASSWORD")

    client = Client()
    client.login(handle, pw)

    with open(image_path, "rb") as f:
        img_bytes = f.read()

    # Build text with the URL as a clickable facet (Bluesky won't auto-link otherwise).
    tb = client_utils.TextBuilder()
    url_marker = "https://goodtohearthename.co.uk"
    if url_marker in text:
        # find the actual URL (with ?day=N) in the text
        idx = text.find(url_marker)
        # the URL runs to the next whitespace or end
        end = idx
        while end < len(text) and not text[end].isspace():
            end += 1
        before = text[:idx]
        url = text[idx:end]
        after = text[end:]
        tb.text(before).link(url, url).text(after)
    else:
        tb.text(text)

    resp = client.send_image(
        text=tb,
        image=img_bytes,
        image_alt="Silhouette of a footballer with the day's first clue beneath. Good to Hear the Name.",
    )
    # resp.uri looks like at://did:plc:.../app.bsky.feed.post/<rkey>
    rkey = resp.uri.rsplit("/", 1)[-1]
    return f"https://bsky.app/profile/{handle}/post/{rkey}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--player", required=True, help="player id from docs/players.js")
    p.add_argument("--day", required=True, type=int)
    p.add_argument("--archive", action="store_true",
                   help="treat as past-day repost (reveal style caption)")
    p.add_argument("--only", choices=["x", "bluesky"],
                   help="post to only one network")
    p.add_argument("--dry-run", action="store_true",
                   help="generate image + print caption, do not post")
    args = p.parse_args()

    load_env()
    players = load_players()
    if args.player not in players:
        sys.exit(f"unknown player id: {args.player}")
    player = players[args.player]
    sil = os.path.join(SILS, f"{args.player}.jpg")
    if not os.path.exists(sil):
        sys.exit(f"silhouette not found: {sil}")

    out_name = f"daily_{args.player}_day{args.day}.jpg"
    build_post(player, args.day, args.archive, out_name)
    image_path = os.path.join(IG_OUT, out_name)

    is_today = not args.archive
    short = post_caption(player, args.day, is_today)
    ig_caption = caption_for(player, args.day, is_today)
    tags = hashtags_for(player)

    print("\n--- IMAGE ---")
    print(os.path.relpath(image_path, ROOT))
    print("\n--- SHORT CAPTION (X + Bluesky) ---")
    print(short)
    print(f"\n[{len(short)} chars; X limit 280, Bluesky 300]")
    print("\n--- IG CAPTION (paste manually) ---")
    print(ig_caption)
    print("\n--- IG FIRST COMMENT (hashtags) ---")
    print(tags)

    if args.dry_run:
        print("\n(dry run — nothing posted)")
        return

    if args.only != "bluesky":
        try:
            url = post_to_x(image_path, short)
            print(f"\nX posted: {url}")
        except Exception as e:
            print(f"\nX FAILED: {e}")

    if args.only != "x":
        try:
            url = post_to_bluesky(image_path, short)
            print(f"\nBluesky posted: {url}")
        except Exception as e:
            print(f"\nBluesky FAILED: {e}")


if __name__ == "__main__":
    main()
