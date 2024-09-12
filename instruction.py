from __future__ import annotations
from typing import Union
from exceptions import InvalidArithmeticCommand \
                        , InvalidMemoryCommand \
                        , InvalidPointerIndex \
                        , InvalidFunctionCommand \
                        , InvalidCallCommand \
                        , InvalidCommand

import re

class Instruction:

    """ Constructor """
    def __init__(self, code : str) -> None:

        split_code = code.split()

        """ ALL PATTERNS """

        arithmetic_pattern = re.compile(r'^(add|sub|neg|eq|gt|lt|and|or|not)$')
        memory_pattern = re.compile(r'^(push|pop)\s(local|argument|static|constant|this|that|pointer|temp)\s([0-9]+)$')
        label_pattern = re.compile(r'^(label|goto|if-goto) ([.:_a-zA-Z][0-9.:_a-zA-Z]*)$')
        function_pattern = re.compile(r'function ([A-Za-z0-9_]+) (\d+)')
        call_pattern = re.compile(r'call ([A-Za-z0-9_]+) (\d+)')

        if len(split_code) == 1:

            match = arithmetic_pattern.match(code)
            if match:
                self.__type = Arithmetic_instruction 
                self.__arithmetic_ins = match.group(1)

            elif code == "return":
                self.__type = Return_instruction
            else:
                raise InvalidArithmeticCommand("Invalid Arithmetic command: It must be one of : add, sub, neg, eq, gt, lt, and, or, not")
            
        # Memory commands || call f n || function f k
        elif len(split_code) == 3:

            match = memory_pattern.match(code)
            func_match = function_pattern.match(code)
            call_match = call_pattern.match(code)

            if match:

                self.__type = Memory_instruction
                self.__memory_ins = match.group(1)
                self.__memory_segment = match.group(2)
                self.__memory_index = match.group(3)

                # if segment is pointer then index can be only 0 or 1
                if self.__memory_segment == 'pointer' and self.__memory_index != '1' and self.__memory_index != '0':
                    raise InvalidPointerIndex("Pointer index value can either be 0 or 1")

            elif func_match:
                self.__type = Function_instruction
                self.__function_name = func_match.group(1)
                self.__number_of_local_variables = func_match.group(2)

            elif call_match:
                self.__type = Call_instruction
                self.__function_name = call_match.group(1)
                self.__number_of_arguments = call_match.group(2)

            else:
                if code.startswith("push") or code.startswith("pop"):
                    raise InvalidMemoryCommand("Invalid Memory command: It must be of the type: push|pop segment i where segment is one of argument, local, static, constant, this, that, pointer, temp and i is a non-negative integer.")

                elif code.startswith("call"):
                    raise InvalidCallCommand("Invalid Call command: it has to be of the type call f n where f is the name of the function and n is the number of arguments pushed on to the stack")

                elif code.startswith("function"):
                    raise InvalidFunctionCommand("Invalid Function command: it has to be of the type function f k where f is the name of the function and k is the number of local variables")

                else:
                    raise InvalidCommand("Invalid command")

        elif len(split_code) == 2:

            self.__flow_command = True
            match_ = label_pattern.match(code)
            if match_ and code.startswith("label"):
                # label code
                self.__type = Label
                self.__label_name = match_.group(2)

            elif match_ and code.startswith("goto"):
                # goto label code
                self.__type = Goto_instruction
                self.__label_name = match_.group(2)

            elif match_ and code.startswith("if-goto"):
                # if-goto label code
                self.__type = If_goto_instruction
                self.__label_name = match_.group(2)

        else:
            raise InvalidCommand("Command has be either arithmetic, memory or program flow command")

    """ Magic methods """
    def __str__(self) -> str:
        if self.type == Arithmetic_instruction:
            return f'{self.arithmetic_ins}'
        elif self.type == Memory_instruction:
            return f'{self.memory_ins} {self.memory_segment} {self.memory_index}'
        elif self.type == Label:
            return f'Label {self.label}'
        elif self.type == Goto_instruction:
            return f'goto {self.label}'
        elif self.type == If_goto_instruction:
            return f'if-goto {self.label}'

    # Returns number of arguments for call instruction,
    # number of local variables for function instruction, 0 otherwise
    def __len__(self) -> int:

        if self.type == Function_instruction:
            return int(self.__number_of_local_variables)
        elif self.type == Call_instruction:
            return int(self.__number_of_arguments)
        else:
            return 0

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

    @property
    def label(self) -> Union[None,str]:
        return self.__label_name if self.__flow_command else None

    @property
    def function_name(self) -> Union[None,str]:
        return self.__function_name if self.type == Function_instruction or self.type == Call_instruction else None
    
    
class Arithmetic_instruction():
    pass

class Memory_instruction():
    pass

class Label():
    pass

class Goto_instruction():
    pass

class If_goto_instruction():
    pass

class Return_instruction():
    pass

class Function_instruction():
    pass

class Call_instruction():
    pass

