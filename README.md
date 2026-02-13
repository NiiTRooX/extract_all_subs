# extract_all_subs
This script extracts all subtitles of a Matroska file.

## Requirements

- mkvtoolnix executables

## Installation with uv
```
uv tool install git+https://github.com/NiiTRooX/extract_all_subs.git
```

## Usage
```
extract-all-subs /path/to/mkv --out ~/.local/share/subs
```

The `--out` option is optional. If it is not specified, subs will be written to the current directory.
