import sys
import json
import subprocess
from pathlib import Path
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract all subtitle tracks from an MKV file."
    )
    parser.add_argument("input", help="Input MKV file")
    parser.add_argument(
        "--out",
        help="Output directory (default: current directory)",
        default="."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    input_file = Path(args.input).resolve()
    output_dir = Path(args.out).resolve()

    if not input_file.is_file():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    basename = input_file.stem

    try:
        result = subprocess.run(
            ["mkvmerge", "-J", str(input_file)],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print("Error running mkvmerge")
        print(e)
        sys.exit(1)

    data = json.loads(result.stdout)

    tracks_to_extract = []

    for track in data.get("tracks", []):
        if track.get("type") != "subtitles":
            continue

        track_id = track.get("id")
        props = track.get("properties", {})

        language = props.get("language", "und")
        language_ietf = props.get("language_ietf", "")
        codec_id = props.get("codec_id", "")
        codec_name = track.get("codec", "")
        
        if language_ietf:
            language = language_ietf

        if codec_id in ("S_TEXT/ASS", "S_TEXT/SSA") or codec_name == "SubStationAlpha":
            ext = "ass"
        elif codec_id == "S_TEXT/UTF8" or codec_name == "SubRip":
            ext = "srt"
        else:
            ext = "sub"

        output_name = f"{basename}_{track_id}.{language}.{ext}"
        output_path = output_dir / output_name

        print(f"Preparing track {track_id} ({language}, {codec_id or codec_name}) -> {output_path}")

        tracks_to_extract.append(f"{track_id}:{output_path}")

    if not tracks_to_extract:
        print("No subtitle tracks found.")
        return

    cmd = ["mkvextract", "tracks", str(input_file)] + tracks_to_extract

    print("\nRunning mkvextract...\n")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print("Error running mkvextract")
        sys.exit(1)


if __name__ == "__main__":
    main()
