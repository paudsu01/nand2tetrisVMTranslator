from __future__ import annotations
from instruction import Arithmetic_instruction, Memory_instruction, Instruction

class Code_writer:
    
    __currentLabelNumber = 0
    __memory_command_to_assembly_mapping = {
            'local': "@LCL\n",
            'argument': "@ARG\n",
            'this':"@THIS\n",
            'that':"@THAT\n",
            'constant': "D=A",
            'or': "M=M|D\n",
            'eq': "D;JEQ\n",
            'gt': "D;JGT\n",
            'lt': "D;JLT\n",
        }


    __arithmetic_command_to_assembly_mapping = {
            'add': "M=M+D\n",
            'sub': "M=M-D\n",
            'neg':"M=-M\n",
            'not':"M=!M\n",
            'and': "M=M&D\n",
            'or': "M=M|D\n",
            'eq': "D;JEQ\n",
            'gt': "D;JGT\n",
            'lt': "D;JLT\n",
        }


    @classmethod
    def __increment_stack_pointer(cls):
        return "@SP\nM=M+1\n"

    @classmethod
    def __push_d_register_onto_stack(cls):
        # *SP = D
        return "@SP\nA=M\nM=D\n"

    @classmethod
    def __decrement_stack_pointer(cls):
        return "@SP\nM=M-1\n"

    @classmethod
    def __store_address_in_d_using_indirect_addressing(cls, ins: Instruction) -> str:
        return f"@{cls.__memory_command_to_assembly_mapping[ins.memory_ins]}\nD=M\n@{ins.memory_index}\nA=A+D\nD=M"

    @classmethod
    def __load_constant(cls, value: str) -> str:
        return f"@{value}\nD=A\n"

    @classmethod
    def __pop_value_into_d_register(cls):
        return "@SP\nA=M-1\nD=M\n" 

    @classmethod
    def __decrement_address(cls):
        return "A=A-1\n"

    @classmethod
    def __code_for_jump(cls, jump_instruction: str) -> str:
        num = cls.__currentLabelNumber
        cls.__currentLabelNumber += 1
        return f"D=M-D\n@jumpLabel{num}\n{cls.__arithmetic_command_to_assembly_mapping[jump_instruction]}D=0\n@endLabel{num}\n0;JMP\n(jumpLabel{num})\nD=1\n(endLabel{num})\n"

    @classmethod
    def __move_d_in_sp_minus_two(cls) -> str:
        return "@SP\nA=M-1\nA=A-1\nM=D\n"

    @classmethod
    def __comment(cls, instruction):
        if instruction.type == Arithmetic_instruction:
            return f'// {instruction.arithmetic_ins}\n'
        elif instruction.type == Memory_instruction:
            return f'// {instruction.memory_ins} {instruction.memory_segment} {instruction.memory_segment}\n'

    """ Public methods """ 
    @classmethod
    def set_file_name(cls, name: str) -> str:
        cls.filename = name

    @classmethod
    def code(cls, instruction):

        # Handle arithmetic instructions
        if instruction.type == Arithmetic_instruction:

            assembly_code = cls.__comment(instruction) \
                            + cls.__pop_value_into_d_register() \
                            + cls.__decrement_address() \

            if instruction.arithmetic_ins in ['eq', 'lt', 'gt']:
                assembly_code += cls.__code_for_jump(instruction.arithmetic_ins) + cls.__move_d_in_sp_minus_two() 
            else:
                assembly_code += cls.__arithmetic_command_to_assembly_mapping[instruction.arithmetic_ins]

            assembly_code += cls.__decrement_stack_pointer()
            return assembly_code

        # Handle memory instructions
        else:
            if instruction.memory_ins == 'push':
                if instruction.memory_segment == 'constant':
                    assembly_code = cls.__load_constant(instruction.memory_index)
                else:
                    assembly_code = cls.__store_address_in_d_using_indirect_addressing(instruction) 
                assembly_code += cls.__push_d_register_onto_stack() + cls.__increment_stack_pointer()
            else:
                pass


