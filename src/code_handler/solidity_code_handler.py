import re
from typing import LiteralString

from code_handler.code_handler import CodeHandler, Language

class SolidityCodeHandler(CodeHandler):
    def __init__(self, code: str, contract_name: str, function_name: str):
        self._code = code
        self._contract_name = contract_name
        self._function_name = function_name

        self.language = Language.Solidity

    def get_code(self) -> str:
        return self._code

    def get_language(self) -> Language:
        return self.language
    
    def get_assert_format(self) -> str:
        return 'assert(...);'

    def get_assert_pattern(self) -> str:
        return r'assert\s*\(.*?\);'
    
    def get_preconditions(self) -> list[str]:
        if self._function_name == 'constructor':
            function_signature_pattern = re.compile(r'constructor\s*\(.*?\)\s*{')
        else:
            function_signature_pattern = re.compile(rf'function\s+{self._function_name}\s*\(.*?\)\s*.*?{{')
        
        for i in range(0, len(self._code.splitlines())):
            line = self._code.splitlines()[i]
            if function_signature_pattern.match(line.strip()):
                function_code, _ = self._jump_scope(self._code.splitlines(), i)

                assertions = []
                pre_loop_code = function_code.split('while')[0]

                assignments_pattern = re.compile(r'(\w+)\s*=\s*(\w+)')
                assignments_matches = assignments_pattern.findall(pre_loop_code)
                for match in assignments_matches:
                    assertions.append(f'assert({match[0]} == {match[1]})')

                require_pattern = re.compile(r'require\s*\(\s*([^,)]*)')
                require_matches = require_pattern.findall(pre_loop_code)
                for match in require_matches:
                    assertions.append(f'assert({match})')

                return assertions
        
        raise ValueError(f"Function '{self._function_name}' not found in the provided code.")

    def _jump_scope(self, lines: list[str], start_index: int, balance = 0) -> tuple[str, int]:
        content = ''
        for i in range(start_index, len(lines)):
            line = lines[i]
            content += f'{line}\n'
            if '{' in line:
                balance += 1
            elif '}' in line:
                balance -= 1
            if balance == 0:
                return content, i
        raise ValueError("No matching closing brace found.")
    
    def add_invariant_assertions(self, formula: str):
        assertion = f'assert({formula});'
        code = ''
        function_start_index = -1
        contract_start_index = -1
        
        if self._function_name == 'constructor':
            function_signature_pattern = re.compile(r'constructor\s*\(.*?\)\s*{')
        else:
            function_signature_pattern = re.compile(rf'function\s+{self._function_name}\s*\(.*?\)\s*.*?{{')

        contract_pattern = re.compile(rf'contract\s+{self._contract_name}\s*{{')

        lines = self._code.splitlines()
        i = 0
        while i < len(lines):
            if contract_pattern.match(lines[i].strip()):
                contract_start_index = i

            if function_signature_pattern.match(lines[i].strip()) and contract_start_index != -1:
                function_start_index = i

            if 'while' in lines[i] and function_start_index != -1:
                code += f'{assertion}\n{lines[i]}\n{assertion}\n'
                jumped_code, i = self._jump_scope(lines, i+1, balance=1)
                code += f'{jumped_code}{assertion}\n'
                _, i = self._jump_scope(lines, function_start_index)

            code += f'{lines[i]}\n'
            i += 1

        return code
