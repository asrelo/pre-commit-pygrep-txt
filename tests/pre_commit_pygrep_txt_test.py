import pytest

from pre_commit_pygrep_txt import main


@pytest.fixture
def some_files(tmpdir):
    tmpdir.join('f1').write_binary(b'foo\nbar\n')
    tmpdir.join('f2').write_binary(b'[INFO] hi\n')
    tmpdir.join('f3').write_binary(b"with'quotes\n")
    tmpdir.join('f4').write_binary(b'foo\npattern\nbar\n')
    tmpdir.join('f5').write_binary(b'[INFO] hi\npattern\nbar')
    tmpdir.join('f6').write_binary(b"pattern\nbarwith'foo\n")
    tmpdir.join('f7').write_binary(b"hello'hi\nworld\n")
    tmpdir.join('f8').write_binary(b'foo\nbar\nbaz\n')
    tmpdir.join('f9').write_binary(b'[WARN] hi\n')
    with tmpdir.as_cwd():
        yield


@pytest.fixture(params=((), ('--encoding', 'utf-8')))
def extra_args(request):
    return request.param


@pytest.mark.usefixtures('some_files')
@pytest.mark.parametrize(
    ('pattern', 'expected_retcode', 'expected_out'),
    (
        ('baz', 0, ''),
        ('foo', 1, 'f1:1:foo\n'),
        ('bar', 1, 'f1:2:bar\n'),
        (r'(?i)\[info\]', 1, 'f2:1:[INFO] hi\n'),
        ("h'q", 1, "f3:1:with'quotes\n"),
    ),
)
def test_main(cap_out, pattern, expected_retcode, expected_out, extra_args):
    ret = main.main((pattern, 'f1', 'f2', 'f3', *extra_args))
    out = cap_out.get()
    assert ret == expected_retcode
    assert out == expected_out


@pytest.mark.usefixtures('some_files')
def test_negate_by_line_no_match(cap_out, extra_args):
    ret = main.main((
        'pattern\nbar', 'f4', 'f5', 'f6', '--negate', *extra_args,
    ))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f4\nf5\nf6\n'


@pytest.mark.usefixtures('some_files')
def test_negate_by_line_two_match(cap_out, extra_args):
    ret = main.main(('foo', 'f4', 'f5', 'f6', '--negate', *extra_args))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f5\n'


@pytest.mark.usefixtures('some_files')
def test_negate_by_line_all_match(cap_out, extra_args):
    ret = main.main(('pattern', 'f4', 'f5', 'f6', '--negate', *extra_args))
    out = cap_out.get()
    assert ret == 0
    assert out == ''


@pytest.mark.usefixtures('some_files')
def test_negate_by_file_no_match(cap_out, extra_args):
    ret = main.main((
        'baz', 'f4', 'f5', 'f6', '--negate', '--multiline', *extra_args,
    ))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f4\nf5\nf6\n'


@pytest.mark.usefixtures('some_files')
def test_negate_by_file_one_match(cap_out, extra_args):
    ret = main.main((
        'foo\npattern', 'f4', 'f5', 'f6', '--negate', '--multiline',
        *extra_args,
    ))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f5\nf6\n'


@pytest.mark.usefixtures('some_files')
def test_negate_by_file_all_match(cap_out, extra_args):
    ret = main.main((
        'pattern\nbar', 'f4', 'f5', 'f6', '--negate', '--multiline',
        *extra_args,
    ))
    out = cap_out.get()
    assert ret == 0
    assert out == ''


@pytest.mark.usefixtures('some_files')
def test_ignore_case(cap_out, extra_args):
    ret = main.main(('--ignore-case', 'info', 'f1', 'f2', 'f3', *extra_args))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f2:1:[INFO] hi\n'


@pytest.mark.usefixtures('some_files')
def test_multiline(cap_out, extra_args):
    ret = main.main((
        '--multiline', r'foo\nbar', 'f1', 'f2', 'f3', *extra_args,
    ))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f1:1:foo\nbar\n'


@pytest.mark.usefixtures('some_files')
def test_multiline_line_number(cap_out, extra_args):
    ret = main.main(('--multiline', r'ar', 'f1', 'f2', 'f3', *extra_args))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f1:2:bar\n'


@pytest.mark.usefixtures('some_files')
def test_multiline_dotall_flag_is_enabled(cap_out, extra_args):
    ret = main.main(('--multiline', r'o.*bar', 'f1', 'f2', 'f3', *extra_args))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f1:1:foo\nbar\n'


@pytest.mark.usefixtures('some_files')
def test_multiline_multiline_flag_is_enabled(cap_out, extra_args):
    ret = main.main((
        '--multiline', r'foo$.*bar', 'f1', 'f2', 'f3', *extra_args,
    ))
    out = cap_out.get()
    assert ret == 1
    assert out == 'f1:1:foo\nbar\n'
