from .Utils import get_file_hash

from pathlib import Path
import subprocess


class AnswerComparator:
    def __init__(self, comparator_path=Path().home(), arguments_format=''):
        """
        :param comparator_path: path to comparator executable. If path is empty, then
        result files are compared by MD5-hashsum
        :param arguments_format: string format for passing arguments to comparator.
        For example if comparator_path is './a.out', format is '123 qwe {0} {1}'
        and files are file1 and file2
        then the resulting command would be ['./a.out', '123', 'file1', 'file2']
        """
        self.comparatorPath = comparator_path
        self.argumentsFormat = arguments_format

    def are_equal(self, file1: Path, file2: Path) -> (bool, str):
        if not (file1.exists() and file2.exists()):
            return False, f'one of the files `{file1}\' and `{file2}\' can not be found'

        if self.comparatorPath != Path().home():
            args = self.argumentsFormat.format(file1, file2).split(' ')
            res = subprocess.run([str(self.comparatorPath), *args],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            return res.returncode == 0

        return get_file_hash(file1) == get_file_hash(file2)
