from __future__ import annotations
from instruction import Arithmetic_instruction, \
                        Memory_instruction, \
                        Instruction,\
                        Label, \
                        Goto_instruction,\
                        If_goto_instruction, \
                        Function_instruction, \
                        Return_instruction, \
                        Call_instruction

class Code_writer:
    
    __currentLabelNumber = 0
    __currentReturnNumber = 0
    __memory_command_to_assembly_mapping_pop = {
            'local': "@LCL\nD=M\n",
            'argument': "@ARG\nD=M\n",
            'this':"@THIS\nD=M\n",
            'that':"@THAT\nD=M\n",
            'pointer0': "@THIS\nD=A\n",
            'pointer1': "@THAT\nD=A\n",
            'temp': "@5\nD=A\n",
        }

    __memory_command_to_assembly_mapping_push = {
            'local': "@LCL\n",
            'argument': "@ARG\n",
            'this':"@THIS\n",
            'that':"@THAT\n",
            'pointer0': "@THIS\nD=M\n",
            'pointer1': "@THAT\nD=M\n",
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
    def __add_value_to_d_register(cls, value: str) -> str:
        return f'@{value}\nD=D+A\n'

    @classmethod
    def __decrement_stack_pointer(cls):
        return "@SP\nM=M-1\n"

    @classmethod
    def __store_address_in_d_using_indirect_addressing(cls, ins: Instruction) -> str:
        return f"{cls.__memory_command_to_assembly_mapping_push[ins.memory_segment]}D=M\n@{ins.memory_index}\nA=A+D\nD=M\n"

    @classmethod
    def __load_constant(cls, value: str) -> str:
        return f"@{value}\nD=A\n"
    
    @classmethod
    def __temp_code_push(cls, value: str) -> str:
        return f"@{5+int(value)}\nD=M\n"

    @classmethod
    def __static_code_push(cls, index: str) -> str:
        return f"@{cls.filename}.{index}\nD=M\n"

    @classmethod
    def __static_code_pop(cls, index: str) -> str:
        return f"@{cls.filename}.{index}\nD=A\n"

    @classmethod
    def __pop_value_into_d_register(cls):
        return "@SP\nA=M-1\nD=M\n" 

    @classmethod
    def __indirect_address_temp_and_save_d(cls):
        return "@5\nA=M\nM=D\n"
    
    @classmethod
    def __direct_address_temp_and_save_d(cls):
        return "@5\nM=D\n"

    @classmethod
    def __decrement_address(cls):
        return "A=A-1\n"

    @classmethod
    def __code_for_jump(cls, jump_instruction: str) -> str:
        num = cls.__currentLabelNumber
        cls.__currentLabelNumber += 1
        return f"D=M-D\n@jumpLabel{num}\n{cls.__arithmetic_command_to_assembly_mapping[jump_instruction]}D=0\n@endLabel{num}\n0;JMP\n(jumpLabel{num})\nD=-1\n(endLabel{num})\n"

    @classmethod
    def __move_d_in_sp_minus_two(cls) -> str:
        return "@SP\nA=M-1\nA=A-1\nM=D\n"

    @classmethod
    def __code_to_push_ram_value_onto_stack(cls, address: int) -> str:
        return f'@{address}\nD=M\n' + cls.__push_d_register_onto_stack() + cls.__increment_stack_pointer() 

    @classmethod
    def __return_restore_value(cls, saved_values_address: int, minus_value: int) -> str:
        return f'@{minus_value}\nD=A\n@5\nD=M-D\nA=D\nD=M\n@{saved_values_address}\nM=D\n'

    @classmethod
    def __generate_return_assembly_code(cls) -> str:

        assembly_code_list = []
        # FRAME = LCL
        assembly_code_list.append('@LCL\nD=M\n@5\nM=D\n')
        # RET = *(FRAME-5)
        assembly_code_list.append(cls.__return_restore_value(6, 5))
        # *ARG = pop()
        assembly_code_list.append(cls.__pop_value_into_d_register() + '@ARG\nA=M\nM=D\n')
        # SP=ARG+1
        assembly_code_list.append('@ARG\nD=M+1\n@SP\nM=D\n')
        # THAT= *(FRAME-1)
        assembly_code_list.append(cls.__return_restore_value(4,1))
        # THIS= *(FRAME-2)
        assembly_code_list.append(cls.__return_restore_value(3,2))
        # ARG= *(FRAME-3)
        assembly_code_list.append(cls.__return_restore_value(2,3))
        # LCL= *(FRAME-4)
        assembly_code_list.append(cls.__return_restore_value(1,4))
        # goto RET
        assembly_code_list.append('@6\nA=M\n0;JMP\n')

        return ''.join(assembly_code_list)

    @classmethod
    def __generate_call_function_assembly_code(cls, instruction: Instruction) -> str:
       
        # assembly_code to push return address onto stack
        assembly_code = [f'//push return-address, LCL, ARG, THIS, THAT\n@{instruction.function_name}$return{cls.__currentReturnNumber}\nD=A\n' + cls.__push_d_register_onto_stack() + cls.__increment_stack_pointer()]

        # push LCL, ARG, THIS, THAT
        for i in range(1,5):
            assembly_code.append(cls.__code_to_push_ram_value_onto_stack(i))

        # Change ARG pointer to SP-(n+5)
        assembly_code.append(f'//ARG=SP-n-5\n@{len(instruction)+5}\nD=A\n@SP\nD=M-D\n@ARG\nM=D\n')
        # Change LCL pointer to SP
        assembly_code.append('//LCL=SP\n@SP\nD=M\n@LCL\nM=D\n')

        # goto functionName 
        assembly_code.append(f'@{instruction.function_name}\n0;JMP\n')
        # add (functionName$return) label
        assembly_code.append(f'({instruction.function_name}$return{cls.__currentReturnNumber})\n')

        cls.__currentReturnNumber += 1

        return ''.join(assembly_code)


    @classmethod
    def __generate_function_definition_assembly_code(cls, instruction : Instruction) -> str:
        assembly_code = f'({instruction.function_name})\n'
        for i in range(len(instruction)):
            push_0_instruction = Instruction('push constant 0')
            assembly_code += Code_writer.code(push_0_instruction)
        return assembly_code

    """ Public methods """ 
    @classmethod
    def startup_code(cls) -> str:
        return '// Set SP=256\n@256\nD=A\n@SP\nM=D\n' + cls.code(Instruction('goto Sys.init'))

    @classmethod
    def set_file_name(cls, name: str) -> str:
        cls.filename = name

    @classmethod
    def code(cls, instruction: Instruction) -> str:

        assembly_code = '// ' + str(instruction) + '\n'

        # Handle arithmetic instructions
        if instruction.type == Arithmetic_instruction:

            assembly_code += cls.__pop_value_into_d_register() 

            if instruction.arithmetic_ins not in ['neg', 'not']:
                assembly_code += cls.__decrement_address()

            if instruction.arithmetic_ins in ['eq', 'lt', 'gt']:
                assembly_code += cls.__code_for_jump(instruction.arithmetic_ins) + cls.__move_d_in_sp_minus_two() 
            else:
                assembly_code += cls.__arithmetic_command_to_assembly_mapping[instruction.arithmetic_ins]

            if instruction.arithmetic_ins not in ['neg', 'not']:
                assembly_code += cls.__decrement_stack_pointer()
        # Handle memory instructions
        elif instruction.type == Memory_instruction:

            # Handle push instructions
            if instruction.memory_ins == 'push':

                if instruction.memory_segment == 'constant':
                    assembly_code += cls.__load_constant(instruction.memory_index)
                elif instruction.memory_segment == 'temp':
                    assembly_code += cls.__temp_code_push(instruction.memory_index)
                elif instruction.memory_segment == 'static':
                    assembly_code += cls.__static_code_push(instruction.memory_index)
                elif instruction.memory_segment == 'pointer':
                    assembly_code += cls.__memory_command_to_assembly_mapping_push[f'{instruction.memory_segment}{instruction.memory_index}']
                else:
                    assembly_code += cls.__store_address_in_d_using_indirect_addressing(instruction)

                assembly_code += cls.__push_d_register_onto_stack() + cls.__increment_stack_pointer()

            # Handle pop instructions
            else:

                if instruction.memory_segment != 'constant':

                    if instruction.memory_segment != 'pointer' and instruction.memory_segment != 'static':
                        assembly_code += cls.__memory_command_to_assembly_mapping_pop[instruction.memory_segment] + cls.__add_value_to_d_register(instruction.memory_index)

                    elif instruction.memory_segment == 'pointer':
                        assembly_code += cls.__memory_command_to_assembly_mapping_pop[f'{instruction.memory_segment}{instruction.memory_index}']

                    else:
                        assembly_code += cls.__static_code_pop(instruction.memory_index)

                    assembly_code += cls.__direct_address_temp_and_save_d() + cls.__pop_value_into_d_register() + cls.__decrement_stack_pointer() + cls.__indirect_address_temp_and_save_d()
                else:
                    assembly_code += cls.__decrement_stack_pointer()

        elif instruction.type == Function_instruction:
            assembly_code += cls.__generate_function_definition_assembly_code(instruction)

        elif instruction.type == Call_instruction:
            assembly_code += cls.__generate_call_function_assembly_code(instruction)

        elif instruction.type == Return_instruction:
            assembly_code += cls.__generate_return_assembly_code()
        
        # Handle branching instructions
        else:
            if instruction.type == Label:
                assembly_code += f'({instruction.label})\n'
            elif instruction.type == Goto_instruction:
                assembly_code += f'@{instruction.label}\n0;JMP\n'
            elif instruction.type == If_goto_instruction:
                assembly_code += cls.__pop_value_into_d_register() + cls.__decrement_stack_pointer() + f'@{instruction.label}\nD;JNE\n' 

        return assembly_code

    @staticmethod
    def number_of_assembly_lines(code : str) -> int:

            # Doesn't count commented lines
            return code.count('\n') - code.count('//')
