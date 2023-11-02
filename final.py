from pathlib import Path
import shutil
import sys
import re

CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

TRANS = dict()

for cyrillic, latin in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(cyrillic)] = latin
    TRANS[ord(cyrillic.upper())] = latin.upper()

def normalize(name: str) -> str:  
    translate_name = re.sub(r"[^A-za-z0-9.]", '_', name.translate(TRANS))
    return translate_name

categories = {
    'Images': ['.jpeg', '.png', '.jpg', '.svg'],
    'Videos': ['.avi', '.mp4', '.mov', '.mkv'],
    'Music': ['.mp3', '.ogg', '.wav', '.amr'],
    'Archives': ['.zip', '.tar', '.rar', '.gz'],
    'Documents': ['.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx', 'xls'],
    'Other': []
}

known_ext = set()
unknown_ext = set()

def move_files(src_folder: Path):
    for item in src_folder.iterdir():
        if item.is_file():
            destination_folder = None
            for category, extensions in categories.items():
                if item.suffix.lower() in extensions:
                    destination_folder = src_folder / category
                    if item.suffix.lower() in {'.zip', '.tar', '.rar', '.gz'}:
                        handle_archive(item, destination_folder)
                        item.unlink()
                    destination_folder.mkdir(parents=True, exist_ok=True)
                    shutil.move(item, destination_folder / normalize(item.name))
                    known_ext.add(item.suffix)                
                    break
                elif destination_folder is None:
                    other_folder = src_folder / 'Other'
                    other_folder.mkdir(parents=True, exist_ok=True)
                    shutil.move(item, other_folder / normalize(item.name))
                    unknown_ext.add(item.suffix)
        elif item.is_dir() and item.name not in ('Archives', 'Videos', 'Music', 'Documents', 'Images', 'Other'):
            known, unknown = move_files(item)
            known_ext.update(known)
            unknown_ext.update(unknown)

    remove_empty_folders(src_folder)
    return known_ext, unknown_ext

def handle_archive(file_name: Path, target_folder: Path):
    target_folder.mkdir(exist_ok=True, parents=True)
    folder_for_file = target_folder / normalize(file_name.name.replace(file_name.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(str(file_name.absolute()), str(folder_for_file.absolute()))
    except shutil.ReadError:
        folder_for_file.rmdir()
    return
    
def remove_empty_folders(path):
    for folder in path.iterdir():
        if folder.is_dir():
            remove_empty_folders(folder)
    if not any(path.iterdir()):
        path.rmdir()

if __name__ == '__main__':
    folder_process = Path(sys.argv[1])
    known_ext, unknown_ext = move_files(folder_process.resolve())
    
    print('')
    print('Список всех известных расширений:')
    print(' '.join(map(str, known_ext)), end='\n\n')
    print('Список всех неизвестных расширений:')
    print(' '.join(map(str, unknown_ext)), end='\n\n')