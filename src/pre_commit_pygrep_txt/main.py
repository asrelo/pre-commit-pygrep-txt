import argparse
import re
from collections.abc import Sequence
from re import Pattern
from typing import Any
from typing import IO
from typing import NamedTuple

from pre_commit_pygrep_txt import output


def _open_input(filename: str, encoding: str | None) -> IO[Any]:
    if encoding is None:
        return open(filename, 'rb')
    return open(filename, encoding=encoding, newline='')


def _output_line(s: str | bytes) -> None:
    if isinstance(s, bytes):
        output.write_line_b(s)
    else:
        output.write_line(s)


def _process_filename_by_line(
    pattern: Pattern[Any], filename: str, encoding: str | None,
) -> int:
    retv = 0
    with _open_input(filename, encoding) as f:
        for line_no, line in enumerate(f, start=1):
            if pattern.search(line):
                retv = 1
                output.write(f'{filename}:{line_no}:')
                _output_line(
                    (
                        line.rstrip(b'\r\n')
                        if isinstance(line, bytes)
                        else line.rstrip('\r\n')
                    ),
                )
    return retv


def _process_filename_at_once(
    pattern: Pattern[Any], filename: str, encoding: str | None,
) -> int:
    retv = 0
    with _open_input(filename, encoding) as f:
        contents = f.read()
        match = pattern.search(contents)
        if match:
            retv = 1
            newline = (b'\n' if isinstance(contents, bytes) else '\n')
            line_no = contents[:match.start()].count(newline)
            output.write(f'{filename}:{line_no + 1}:')
            matched_lines = match[0].split(newline)
            matched_lines[0] = contents.split(newline)[line_no]
            _output_line(newline.join(matched_lines))
    return retv


def _process_filename_by_line_negated(
    pattern: Pattern[Any], filename: str, encoding: str | None,
) -> int:
    with _open_input(filename, encoding) as f:
        for line in f:
            if pattern.search(line):
                return 0
        else:
            output.write_line(filename)
            return 1


def _process_filename_at_once_negated(
    pattern: Pattern[Any], filename: str, encoding: str | None,
) -> int:
    with _open_input(filename, encoding) as f:
        contents = f.read()
    match = pattern.search(contents)
    if match:
        return 0
    else:
        output.write_line(filename)
        return 1


class Choice(NamedTuple):
    multiline: bool
    negate: bool


FNS = {
    Choice(multiline=True, negate=True): _process_filename_at_once_negated,
    Choice(multiline=True, negate=False): _process_filename_at_once,
    Choice(multiline=False, negate=True): _process_filename_by_line_negated,
    Choice(multiline=False, negate=False): _process_filename_by_line,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            'grep-like finder using Python regexes, operating on bytes by '
            'default or decoded codepoints with --encoding.  Unlike grep, '
            'this tool returns nonzero when it finds a match '
            'and zero otherwise.  The idea here being that matches '
            'are "problems".'
        ),
    )
    parser.add_argument('-i', '--ignore-case', action='store_true')
    parser.add_argument('--multiline', action='store_true')
    parser.add_argument('--negate', action='store_true')
    parser.add_argument(
        '--encoding',
        help='decode input using this encoding; default is byte-oriented mode',
    )
    parser.add_argument('pattern', help='python regex pattern.')
    parser.add_argument('filenames', nargs='*')
    args = parser.parse_args(argv)
    flags = re.IGNORECASE if args.ignore_case else 0
    if args.multiline:
        flags |= re.MULTILINE | re.DOTALL
    pattern_source = args.pattern
    if args.encoding is None:
        pattern_source = pattern_source.encode()
    pattern = re.compile(pattern_source, flags)
    retv = 0
    process_fn = FNS[Choice(multiline=args.multiline, negate=args.negate)]
    for filename in args.filenames:
        retv |= process_fn(pattern, filename, args.encoding)
    return retv
