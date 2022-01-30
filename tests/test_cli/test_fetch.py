import random
import shutil

from click.testing import Result

from prisma import binaries
from tests.utils import Runner


# TODO: this could probably mess up other tests if one of these
# tests fails mid run, as the global binaries are deleted


def assert_success(result: Result) -> None:
    assert result.exit_code == 0
    assert result.output.endswith(
        f'Downloaded binaries to {binaries.GLOBAL_TEMP_DIR}\n'
    )

    for binary in binaries.BINARIES:
        assert binary.path.exists()


def test_fetch(runner: Runner) -> None:
    """Basic usage, binaries are already cached"""
    assert_success(runner.invoke(['py', 'fetch']))


def test_fetch_one_binary_missing(runner: Runner) -> None:
    """Downloads a binary if it is missing"""
    binary = random.choice(binaries.BINARIES)
    assert binary.path.exists()
    binary.path.unlink()
    assert not binary.path.exists()

    assert_success(runner.invoke(['py', 'fetch']))


def test_fetch_force(runner: Runner) -> None:
    """Passing --force re-downloads an already existing binary"""
    binary = random.choice(binaries.BINARIES)
    assert binary.path.exists()
    old_stat = binary.path.stat()

    assert_success(runner.invoke(['py', 'fetch', '--force']))

    new_stat = binary.path.stat()

    # modified time
    assert old_stat.st_mtime_ns != new_stat.st_mtime_ns

    # ensure downloaded the same as before
    assert old_stat.st_size == new_stat.st_size


def test_fetch_force_no_dir(runner: Runner) -> None:
    """Passing --force when the base directory does not exist"""
    binaries.remove_all()
    shutil.rmtree(str(binaries.GLOBAL_TEMP_DIR))

    binary = binaries.BINARIES[0]
    assert not binary.path.exists()

    assert_success(runner.invoke(['py', 'fetch', '--force']))