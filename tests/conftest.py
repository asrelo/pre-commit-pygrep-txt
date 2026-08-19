import functools
import io
from unittest import mock

import pytest

from pre_commit_pygrep_txt import output


class Fixture:

    def __init__(self, stream: io.BytesIO) -> None:
        self._stream = stream

    def get_bytes(self) -> bytes:
        data = self._stream.getvalue()
        self._stream.seek(0)
        self._stream.truncate()
        return data.replace(b'\r\n', b'\n')

    def get(self) -> str:
        return self.get_bytes().decode()


@pytest.fixture
def cap_out():
    stream = io.BytesIO()
    write = functools.partial(output.write, stream=stream)
    write_line_b = functools.partial(output.write_line_b, stream=stream)
    with mock.patch.multiple(output, write=write, write_line_b=write_line_b):
        yield Fixture(stream)
