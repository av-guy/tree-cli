import os
import argparse
import win32api
import re

from dataclasses import dataclass


class Tree:
    BRANCHES = [0]
    ROOT = ''
    FILES = False

    @staticmethod
    def generate_pipes(levels):
        spacers = ['   '] * (levels - 2)
        for index in range(levels, 2, -1):
            target = Tree.BRANCHES[index - 2]
            if target > 0:
                spacers[index - 3] = f'{Characters.PIPE}   '
        return ''.join(spacers)

    @staticmethod
    def calculate_levels(dirpath, root):
        try:
            levels = len(
                (split := dirpath.split('\\'))
                [split.index(root):]
            )
        except ValueError:
            levels = len((split := dirpath.split('\\')))
        return (levels, split)

    @staticmethod
    def error(exception_instance):
        dirpath = exception_instance.filename
        levels, _ = Tree.calculate_levels(dirpath, Tree.ROOT)
        Tree.BRANCHES[levels - 1] -= 1

    @staticmethod
    def is_junction(path: str) -> bool:
        try:
            return bool(os.readlink(path))
        except (OSError, ValueError):
            return False

    @staticmethod
    def get_junction_len(dirpath, dirnames):
        return len([
            dirname for dirname in dirnames if
            Tree.is_junction(f'{dirpath}\\{dirname}') is True
        ])

    @staticmethod
    def parse_volume(dirpath):
        return re.search(r'\w:\\', dirpath).group()

    @staticmethod
    def create_header(dirpath):
        dirpath = os.path.abspath(dirpath)
        vlm_info = win32api.GetVolumeInformation(Tree.parse_volume(dirpath))
        vlm_hr, vlm_ser = vlm_info[0], vlm_info[1]
        fpl, vsn = FolderPathListing(vlm_hr), VolumeSerialNumber(vlm_ser)
        print(f'{fpl}\n{vsn}\n{dirpath.upper()}')

    @staticmethod
    def generate_branch(levels, directory):
        spacer = Tree.generate_pipes(levels)
        branch = HalfBranch
        if Tree.BRANCHES[levels - 1] > 1:
            branch = FullBranch
        repr = branch(identifier=directory)
        Tree.BRANCHES[levels - 1] -= 1
        print(f'{spacer}{repr}')

    @staticmethod
    def generate_files(dirpath, levels, files):
        levels, _ = Tree.calculate_levels(f'{dirpath}\\file', Tree.ROOT)
        Tree.extend_branches(levels)
        Tree.BRANCHES[levels] = len(files)
        for file in files:
            spacers = Tree.generate_pipes(levels)
            Tree.BRANCHES[levels] -= 1
            print(f'{spacers}   {file}')

    @staticmethod
    def extend_branches(levels):
        if levels > len(Tree.BRANCHES) - 1:
            Tree.BRANCHES.append(0)

    @staticmethod
    def main(path, root):
        Tree.ROOT = root
        for dirpath, dirnames, files in os.walk(
            path, topdown=True, onerror=Tree.error,
            followlinks=False
        ):
            levels, split = Tree.calculate_levels(dirpath, root)
            Tree.extend_branches(levels)
            junctions = Tree.get_junction_len(dirpath, dirnames)
            Tree.BRANCHES[levels] = len(dirnames) - junctions
            if (directory := split[len(split)-1]) != root:
                Tree.generate_branch(levels, directory)
                if Tree.FILES and len(files) >= 1:
                    Tree.generate_files(dirpath, levels, files)
            else:
                Tree.create_header(dirpath)


class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='List target directory as a tree structure',
            prefix_chars='/',
            add_help=True
        )
        self.__accept_path_arg()
        self.__accept_extended_arg()
        self.__accept_file_arg()
        self.__parse_args()
        self.__collect_parameters()

    def __accept_extended_arg(self):
        self.__ascii = self.parser.add_argument(
            '/A',
            action='store_true',
            help='Use ASCII instead of extended characters'
        )

    def __accept_file_arg(self):
        self.__files = self.parser.add_argument(
            '/F',
            action='store_true',
            help='List both files and directories'
        )

    def __accept_path_arg(self):
        self.__path = self.parser.add_argument(
            'Path',
            metavar='path',
            type=str,
            help='the path used to generate a file/directory tree'
        )

    def __parse_args(self):
        self.args = self.parser.parse_args()

    def __collect_parameters(self):
        self.input_path = self.args.Path
        self.ascii = self.args.A
        self.files = self.args.F


@dataclass
class ExtendedCharacters:
    HALF: str = '└'
    FULL: str = '├'
    TWIG: str = '─'
    PIPE: str = '│'


@dataclass
class ASCIICharacters:
    HALF: str = '\\'
    FULL: str = '+'
    TWIG: str = '-'
    PIPE: str = '|'


@dataclass
class Characters:
    HALF: str = ExtendedCharacters.HALF
    FULL: str = ExtendedCharacters.FULL
    TWIG: str = ExtendedCharacters.TWIG
    PIPE: str = ExtendedCharacters.PIPE


class Branch:
    def __init__(self, identifier='test'):
        self.identifier = identifier
        self.length = 3
        self.branch = f'{self.prefix}{self.twig}'

    @property
    def twig(self):
        __twig = Characters.TWIG
        return __twig * self.length

    def __str__(self):
        return f'{self.branch}{self.identifier}'


class FolderPathListing:
    def __init__(self, volume):
        self.__volume = volume

    def __str__(self):
        return f'Folder PATH listing for volume {self.__volume}'


class VolumeSerialNumber:
    def __init__(self, serial):
        self.__serial = serial

    def __str__(self):
        return f'Volume serial number is {self.__serial}'


class FullBranch(Branch):
    def __init__(self, identifier='test'):
        self.prefix = Characters.FULL
        super().__init__(
            identifier=identifier
        )


class HalfBranch(Branch):
    def __init__(self, identifier='test'):
        self.prefix = Characters.HALF
        super().__init__(
            identifier=identifier
        )


def SwapCharacters(ascii=False):
    if ascii:
        Characters.HALF = ASCIICharacters.HALF
        Characters.FULL = ASCIICharacters.FULL
        Characters.TWIG = ASCIICharacters.TWIG
        Characters.PIPE = ASCIICharacters.PIPE


def Main(input_path, ascii=False, files=False):
    input_path = input_path.replace('/', '\\')
    input_path_split = input_path.split('\\')
    root_key = input_path_split[len(input_path_split)-1]
    if ascii:
        SwapCharacters()
    Tree.FILES = files
    Tree.main(input_path, root_key)
