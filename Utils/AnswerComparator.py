from .Utils import get_file_hash

import os
import subprocess


class AnswerComparator:
    def __init__(self, comparator_path='', arguments_format=''):
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

    def are_equal(self, file1, file2) -> bool:
        assert os.path.exists(file1) and os.path.exists(file2)

        if len(self.comparatorPath) != 0:
            args = self.argumentsFormat.format(file1, file2).split(' ')
            res = subprocess.run([self.comparatorPath, *args],
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            return res.returncode == 0

        return get_file_hash(file1) == get_file_hash(file2)
