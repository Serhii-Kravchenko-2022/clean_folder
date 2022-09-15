import sys

import os
from pathlib import Path
import shutil

# create a dictionary of folders and extensions
FILES_DICT = {'images': ['JPEG', 'PNG', 'JPG', 'SVG'],
              'documents': ['DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'],
              'audio': ['MP3', 'OGG', 'WAV', 'AMR'],
              'video': ['AVI', 'MP4', 'MOV', 'MKV'],
              'archives': ['ZIP', 'GZ', 'TAR']
              }
# create a dictionary of folder processing results
result_dict = {'images': [],
               'documents': [],
               'audio': [],
               'video': [],
               'archives': [],
               'known': [],
               'unknown': []
               }


def ext_dict_normalize(files_dict):
    """Change all values in dict to lower case

    :param files_dict: dict
    :return: lower values in dict
    """
    for key, values in files_dict.items():
        for i in range(len(values)):
            values[i] = values[i].lower()


def file_handler(path: Path):
    """ Processing each file based on the dictionary: renaming - by the normalize function
         create folder by dictionary key if missing
         moving the file to this folder, adding it to the list of known extensions depending on the dictionary key
         for archives: create folder by dictionary key, create subfolder by archive name, unpack archive into subfolder
         listing
         for unknown - create a list of unknown extensions

    :param path: path
    :return: make manipulation with files
    """
    global result_dict
    check_known = False
    file_full_name = path.name
    file_ext = file_full_name.split('.')[-1].lower()
    for key, value in FILES_DICT.items():
        # if the extension is present in the dictionary
        if file_ext in value:
            # add to the list of known extensions
            result_dict['known'].append(file_ext)
            check_known = True
            # change the filename using the normalize function
            file_name = normalize(file_full_name.split('.')[0])
            file_full_name = '.'.join([file_name, file_ext])
            # add a file to the dictionary list by destination
            result_dict[key].append(file_full_name)
            # create folder by dictionary key
            new_folder_name = os.path.join(str(base_folder), key)
            os.makedirs(new_folder_name, exist_ok=True)
            # create a new file path with a changed name
            new_file_path = os.path.join(new_folder_name, file_full_name)
            if key == 'archives':
                # creating a folder with the name of the archive and extracting to this folder
                new_arh_folder = os.path.join(new_folder_name, file_name)
                os.makedirs(new_arh_folder, exist_ok=True)
                if file_ext == 'gz':
                    file_ext += 'tar'
                shutil.unpack_archive(str(path), new_arh_folder, file_ext)
                # remove file
                os.remove(str(path))
            else:
                # move file to destination folder
                shutil.move(str(path), new_file_path)
    # if the extension is not in the dictionary, create a list of unknown extensions
    if not check_known:
        result_dict['unknown'].append(file_ext)


def get_dir_elements(path: Path):
    """ we get access to all elements of the directory, taking into account attachments

    :param path: path
    :return: None
    """
    for element in path.iterdir():
        # if file:
        if element.is_file():
            file_handler(element)  # do file processing
        # if folder:
        if element.is_dir():
            if element.name in FILES_DICT:  # do not touch folders from the dictionary
                continue
            # empty folder check
            if not os.listdir(str(element)):
                os.rmdir(str(element))  # delete folder
                continue
            get_dir_elements(element)


def remove_empty_folder(path: Path):
    """ remove all empty folder in path folder

    :param path: path
    :return: None
    """
    for element in path.iterdir():
        if element.is_dir():
            if not os.listdir(str(element)):
                os.rmdir(str(element))  # delete folder
                continue
            remove_empty_folder(element)


def normalize(name: str):
    """ Make transliteration symbols in name, cyrillic letter to latin,
    oder symbols to '_', except number

    :param name: str
    :return: str
    """
    cyrillic_symbols = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
    translation = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t",
                   "u", "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
    translation_dict = {}

    for c, l in zip(cyrillic_symbols, translation):
        translation_dict[ord(c)] = l
        translation_dict[ord(c.upper())] = l.upper()

    name = name.translate(translation_dict)
    for i, letter in enumerate(name):
        if not letter.isalpha() and not letter.isnumeric():
            name = name.replace(letter, '_')
    return name


def main(path):
    """ Main function: Normalize dictionary of extension to lower case
    processes items from a folder
    remove empty folder

    :param path: path
    :return: print result list from result_dictionary
    """
    path = Path(path)
    ext_dict_normalize(FILES_DICT)
    get_dir_elements(path)
    remove_empty_folder(path)
    for key, value in result_dict.items():
        item_name = 'Extension' if key == 'known' or key == 'unknown' else 'File'
        print('=============================================')
        print(f'{item_name} list in folder {key}: ', list(set(result_dict[key])))


if __name__ == '__main__':
    # create a variable with the name of the working folder
    base_folder = sys.argv[1]
    if len(sys.argv) < 2:
        print('Enter path to folder which should be cleaned')
        exit()
    # check if the specified folder exists and is folder
    if not (os.path.exists(base_folder) and Path(base_folder).is_dir()):
        print('Path incorrect')
        exit()
    main(base_folder)
