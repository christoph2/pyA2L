import pytest

from pya2l import preprocessor


def splitter(text):
    return text.splitlines()


@pytest.fixture(scope="function")
def prep():
    return preprocessor.Preprocessor()


def test_no_comment(prep):
    assert prep(splitter("""no comment contained""")) == """no comment contained"""


def test_cpp_comment1(prep):
    assert (
        prep(splitter("""C++ comment // commented out"""))
        == """C++ comment                 """
    )


def test_cpp_comment2(prep):
    assert (
        prep(
            splitter(
                """C++ comment // commented out
not commented out
"""
            )
        )
        == "C++ comment                 \nnot commented out"
    )


def test_single_line_c_comment1(prep):
    assert (
        prep(splitter("C style comment single line /* commented out */"))
        == "C style comment single line                    "
    )


def test_single_line_c_comment1(prep):
    assert (
        prep(splitter("C style comment single line /* commented out */ after comment"))
        == "C style comment single line                     after comment"
    )


def test_multi_line_c_comment1(prep):
    assert (
        prep(
            splitter(
                """C style comment multiple lines /* commented out
L-1
L-2
L-3
*/"""
            )
        )
        == "C style comment multiple lines                 \n\n\n\n"
    )


def test_multi_line_c_comment2(prep):
    assert (
        prep(
            splitter(
                """C style comment multiple lines /* commented out
L-1
L-2
L-3
*/ after comment"""
            )
        )
        == "C style comment multiple lines                 \n\n\n\n after comment"
    )


def test_cpp_comment_containing_a_c_comment1(prep):
    assert (
        prep(splitter("C++ comment... // /* containing a C comment */"))
        == "C++ comment...                                "
    )


def test_cpp_comment_containing_a_c_comment2(prep):
    assert (
        prep(splitter("C++ comment... // /* containing a C comment */\nafter comment"))
        == "C++ comment...                                \nafter comment"
    )


def test_c_comment_containing_a_cpp_comment1(prep):
    assert (
        prep(splitter("C comment. /* containing a // C++ comment */"))
        == "C comment.                                  "
    )


def test_c_comment_containing_a_cpp_comment2(prep):
    assert (
        prep(splitter("C comment / multiline  /* containing a\n// C++ comment */"))
        == "C comment / multiline                 \n"
    )


def test_c_comment_containing_a_cpp_comment3(prep):
    assert (
        prep(
            splitter(
                "C comment / multiline  /* containing a\n// C++ comment */after comment"
            )
        )
        == "C comment / multiline                 \nafter comment"
    )
