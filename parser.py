from __future__ import annotations
from typing import Union, List
from instruction import Instruction

import re

class Parser:

    def __init__(self, filename: str) -> None:

        with open(filename, 'r') as infile:
            lines = [i.strip() for i in infile.readlines()]

        # remove comments and count number of commands
        self.__commands = self.__first_scan(lines)
        self.__max_pc = len(self.__commands) - 1
        self.__current_pc = 0
        
    def __first_scan(self, lines: List[str]) -> List[Instruction]:
        comment_pattern = re.compile(r'^(.*?)(//.*)?$')
        all_instructions = []
        for line in lines:

            required_line_to_parse = comment_pattern.search(line).group(1).strip()
            # ignore commented part
            if required_line_to_parse != '':
                all_instructions.append(Instruction(required_line_to_parse))
        return all_instructions

    def advance(self)-> None:
        if self.__current_pc <= self.__max_pc:
            self.__current_pc += 1

    def has_more_commands(self) -> bool:
        return self.__current_pc <= self.__max_pc

    @property
    def pc(self):
        return self.__current_pc

    @property
    def current_command(self) -> Union[Instruction,None]:
        return self.__commands[self.__current_pc] if self.has_more_commands() else None

