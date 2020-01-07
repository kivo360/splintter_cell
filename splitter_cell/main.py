import re
import os
import click
from operator import itemgetter
from pathlib import Path
from crayons import green, red
from baranomi import Baranomi


class FileIOHandling(object):
    def __init__(self, folder) -> None:
        _folder = self._check_is_absolute(folder)
        self.given_folder = Path(_folder)
        self.given_folder_absolute = self.given_folder.absolute()
        self.is_exist = self.given_folder_absolute.exists()

        self._glob = ""
        self._globs = []

    @property
    def glob(self):
        return self._glob
    
    @glob.setter
    def glob(self, _glob):
        self._glob = _glob

    @property
    def exists(self):
        return self.is_exist
    
    @property
    def glob_paths(self):
        return self._globs

    @glob_paths.setter
    def glob_paths(self, _globs):
        self._globs = _globs
    
    @property
    def sorted_globs(self):
        file_dict_arr = self.sort_by_number_dicts()
        if len(file_dict_arr) == 0:
            return []
        file_list = list(map(lambda x:  f"{x.get('parent', '.')}/{x.get('file_name')}", sorted(file_dict_arr, key=itemgetter('index'))))
        return file_list

    def sorting_scheme(self):
        pass

    def _check_is_absolute(self, _folder):
        """ Checks if the folder is absolute or not. """
        if os.path.isabs(_folder):
            return _folder

        current_path = Path.cwd() / f'{_folder}'
        return current_path

    def search_glob(self):
        if self.exists == True:
            click.echo(green("File path exists"))
            current_glob_paths = list(self.given_folder_absolute.glob(self.glob))
            abs_glob_paths = [x.absolute() for x in current_glob_paths]
            self.glob_paths = abs_glob_paths
            return self.glob_paths
        return self.glob_paths
    

    def sort_by_number_dicts(self):
        file_dict_arr = []
        if len(self.glob_paths) == 0:
            return file_dict_arr
        for file in self.glob_paths:
            fname = file.name
            numbers = [int(s) for s in re.findall(r'\b\d+\b', fname)]
            if len(numbers) > 0:
                item = {
                    "file_name": fname,
                    "index": numbers[0],
                    "parent": file.parents[0]
                }
                file_dict_arr.append(item)
        return file_dict_arr
    


@click.command()
@click.option('--folder', prompt='Which folder?', default="", help='The person to greet.')
@click.option('--glob', prompt='What glob command do you plan on using?', help='The files youre trying to join')
@click.option('--output', prompt='What output file name', help="The file output name")
def hello(folder, glob, output):
    """Get a folder we want to search in, then get the glob necessary to find all of the files we want to merge together."""
    file_io_handler = FileIOHandling(folder)

    file_io_handler.glob = glob
    file_io_handler.search_glob()
    file_list = file_io_handler.sorted_globs
    if len(file_list) > 0:
        click.echo(file_list)
        (
            Baranomi()
            .load_file_list_as_bytes(file_list)
            .join()
            .save(output)
        )
    else:
        click.echo(red("No files found."))


if __name__ == '__main__':
    hello()