#!/usr/bin/python3
import argparse
import pathlib
import subprocess

def main_command(args):
    shared_objects_fancy = list(pathlib.Path(args.directory).glob("*.so.*"))
    shared_objects_simple = list(pathlib.Path(args.directory).glob("*.so"))
    files = shared_objects_fancy + shared_objects_simple
    files_no_symlinks = [file for file in files if not pathlib.Path(file).is_symlink()]

    file_exports = ""
    for file in files_no_symlinks:
        file_exports += str(file) + ":"
        with subprocess.Popen(["readelf", "-sW", file], stdout=subprocess.PIPE) as get_exports:
            file_exports += get_exports.stdout.read().decode() + "\n"

    if args.output == ".":
        print(file_exports)
    else:
        try:
            with open(args.output, "w") as file:
                file.write(file_exports)
        except FileNotFoundError as ex:
            print(f"Path [{args.output}] file path invalid")

def search_command(args):
    shared_objects_fancy = list(pathlib.Path(args.directory).glob("*.so.*"))
    shared_objects_simple = list(pathlib.Path(args.directory).glob("*.so"))
    files = shared_objects_fancy + shared_objects_simple
    files_no_symlinks = [file for file in files if not pathlib.Path(file).is_symlink()]
    sucessess = {}

    for file in files_no_symlinks:
        with subprocess.Popen(["readelf", "-sW", file], stdout=subprocess.PIPE) as get_exports:
            file_exports = get_exports.stdout.read().decode() + "\n"
            if args.string in file_exports:
                sucessess.update({file:file_exports})

    if args.output == ".":
        if args.list is False:
            result = ""
            for key in sucessess:
                result += f"{key}: {sucessess[key]}"
            print(result)
        else:
            for key in sucessess:
                print(f"{key}:\n")
    else:
        try:
            with open(args.output, "w") as file:
                if args.list is False:
                    result = ""
                    for key in sucessess:
                        result += f"{key}: {sucessess[key]}"
                    file.write(result)
                else:
                    for key in sucessess:
                        file.write(f"{key}:\n")
        except FileNotFoundError as ex:
            print(f"Path [{args.output}] file path invalid")

def main():
    parser = argparse.ArgumentParser(prog="objectexport", description="Output exports of shared objects in a directory", epilog="Requires readelf")
    parser.add_argument("-d", "--directory", help="The directory to triage shared objects")
    parser.add_argument("-o", "--output", nargs="?", default = ".", help="The file path for the output file")
    parser.set_defaults(func=main_command)
    
    subparsers = parser.add_subparsers(help="Search for a substring in the exports")
    search_parser = subparsers.add_parser("search", help="Search for a substring in the exported functions")
    search_parser.add_argument("-d", "--directory", required=True)
    search_parser.add_argument("-s", "--string", required=True)
    search_parser.add_argument("-o", "--output", nargs="?", default = ".", help="The file path for the output file")
    search_parser.add_argument("-l", "--list", action="store_true", help="List only file names in output")
    search_parser.set_defaults(func=search_command)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
