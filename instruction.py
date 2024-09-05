from __future__ import annotations
from typing import Union
from exceptions import InvalidArithmeticCommand \
                        , InvalidMemoryCommand \
                        , InvalidPointerIndex \
                        , InvalidCommand

import re

class Instruction:

    def __init__(self, code : str) -> None:

        split_code = code.split()
        arithmetic_pattern = re.compile(r'^(add|sub|neg|eq|gt|lt|and|or|not)$')
        memory_pattern = re.compile(r'^(push|pop)\s(local|argument|static|constant|this|that|pointer|temp)\s([0-9]+)$')

        if len(split_code) == 1:

            match = arithmetic_pattern.match(code)
            if not match:
                raise InvalidArithmeticCommand("Invalid Arithmetic command: It must be one of : add, sub, neg, eq, gt, lt, and, or, not")

            self.__type = Arithmetic_instruction 
            self.__arithmetic_ins = match.group(1)
            print(self.type, self.arithmetic_ins)
            
        elif len(split_code) == 3:
            match = memory_pattern.match(code)
            if not match:
                raise InvalidMemoryCommand("Invalid Memory command: It must be of the type: push|pop segment i where segment is one of argument, local, static, constant, this, that, pointer, temp and i is a non-negative integer.")

            self.__type = Memory_instruction
            self.__memory_ins = match.group(1)
            self.__memory_segment = match.group(2)
            self.__memory_index = match.group(3)
            print(self.type, self.memory_ins, self.memory_index, self.memory_segment)

            # if segment is pointer then index can be only 0 or 1
            if self.__memory_segment == 'pointer' and self.__memory_index != '1' and self.__memory_index != '0':

                raise InvalidPointerIndex("Pointer index value can either be 0 or 1")
        else:
            raise InvalidCommand("Command has be either arithmetic or memory")

    @property
    def memory_segment(self) -> Union[str,None]:
        return self.__memory_segment if self.type == Memory_instruction else None

    @property
    def memory_index(self) -> Union[str,None]:
        return self.__memory_index if self.type == Memory_instruction else None

    @property
    def memory_ins(self) -> Union[str,None]:
        return self.__memory_ins if self.type == Memory_instruction else None

    @property
    def arithmetic_ins(self) -> Union[str,None]:
        return self.__arithmetic_ins if self.type == Arithmetic_instruction else None

    @property
    def is_arithmetic_instruction(self) -> bool:
        return self.type == Arithmetic_instruction

    @property
    def is_memory_instruction(self) -> bool:
        return self.type == Memory_instruction

    @property
    def type(self) -> Union[Arithmetic_instruction,Memory_instruction]:
        return self.__type

class Arithmetic_instruction():
    pass

class Memory_instruction():
    pass
