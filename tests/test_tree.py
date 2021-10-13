from tree.src.tree import HalfBranch
from tree.src.tree import FullBranch
from tree.src.tree import FolderPathListing
from tree.src.tree import VolumeSerialNumber
from tree.src.tree import CLI
from unittest.mock import patch


def test_half_branch():
    half_branch = HalfBranch()
    assert(str(half_branch) == '└───test')


def test_full_branch():
    full_branch = FullBranch()
    assert(str(full_branch) == '├───test')


def test_folder_path():
    volume = 'C:\\'
    folder_path = FolderPathListing(volume)
    assert str(folder_path) == 'Folder PATH listing for volume C:\\'


def test_volume_serial():
    serial = '1234'
    volume_serial = VolumeSerialNumber(serial)
    assert str(volume_serial) == 'Volume serial number is 1234'


class ValidateCLI:
    @staticmethod
    def parse_arg_parser(argument_parser):
        for args, kwargs in argument_parser.call_args_list:
            description = kwargs['description']
            prefix_chars = kwargs['prefix_chars']
            add_help = kwargs['add_help']
            assert description == 'List target directory as a tree structure'
            assert prefix_chars == '/'
            assert add_help is True

    @staticmethod
    def parse_extended_args(argument_parser):
        flags = ['/A', '/F']
        assert True is False
        for args, kwargs in argument_parser.add_argument.call_args_list:
            flag = args
            assert flag in flags


@patch('tree.src.tree.argparse.ArgumentParser')
def test_cli(ArgumentParser):
    CLI()
    ValidateCLI.parse_arg_parser(ArgumentParser)
    ValidateCLI.parse_extended_args(ArgumentParser)
