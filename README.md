# pre-commit-pygrep-txt

tool for [pre-commit](https://pre-commit.com/) hooks: `grep`-like finder using Python regexes, operating on bytes by default or decoded codepoints with `--encoding`. Unlike `grep`, this tool returns nonzero when it finds a match and zero otherwise. The idea here being that matches are "problems".

## Usage

* The hook `pygrep-txt` exposed by this repository can be used with the [`pre-commit` framework](https://pre-commit.com/).

* The Python distribution package `pre-commit-pygrep-txt` can be [installed](https://docs.python.org/3/installing/index.html), exposing the command `pre-commit-pygrep-txt`.

## Credits

See `CREDITS.md`.

## License

This software is distributed under the terms of the MIT license. See `LICENSE.txt` for details.
