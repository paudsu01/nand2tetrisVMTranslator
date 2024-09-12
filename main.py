from __future__ import annotations
from typing import List
from exceptions import InvalidFileException
from parser import Parser
from code_writer import Code_writer

import argparse
import re

def write_to_file(output_lines: str, output_file: str) -> None:
    with open(output_file, 'w') as out:
        out.write(output_lines)

def main(files: List[str]) -> None:
    output_lines = str()
    assembly_lines_generated = 0
    for file in files:
        file_parser = Parser(file)
        Code_writer.set_file_name(file)
        while file_parser.has_more_commands():

            command = file_parser.current_command
            assembly_code = Code_writer.code(command)
            output_lines += assembly_code
            assembly_lines_generated += Code_writer.number_of_assembly_lines(assembly_code)

            file_parser.advance()
    return output_lines

if __name__ == '__main__':

    ## FILE NAME PARSING
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file.vm', help="Provide vm file to translate to assembly", nargs='+')
    arg_parser.add_argument('outputFile.asm', help="Provide name of output file")
    args = arg_parser.parse_args()
    files = vars(args)['file.vm']
    output_file = vars(args)['outputFile.asm']

    ## FILE VALIDATION ## 
    for file in files:
        if not re.match(r'.*\.vm', file):
            raise InvalidFileException("Provide .vm file to translate to assembly")
    if not re.match(r'.*\.asm', output_file):
        raise InvalidFileException("Provide .vm file to translate to assembly")

    output_lines = main(files)
    write_to_file(output_lines, output_file)
