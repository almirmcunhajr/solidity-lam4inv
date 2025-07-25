import re

from code_handler.code_handler import CodeHandler, Language

class SolidityCodeHandler(CodeHandler):
    def __init__(self, code: str):
        self.code = code
        self.language = Language.Solidity

    def get_code(self) -> str:
        return self.code

    def get_language(self) -> Language:
        return self.language
    
    def get_assert_format(self) -> str:
        return 'assert(...);'

    def get_assert_pattern(self) -> str:
        return r'assert\s*\(.*?\);'
    
    def get_preconditions(self) -> list[str]:
        pre_loop_code = self.code.split('while')[0]
        assignments_pattern = re.compile(r'(\w+)\s*=\s*(\w+)')
        assertions = []
        assignments_matches = assignments_pattern.findall(pre_loop_code)
        for match in assignments_matches:
            assertions.append(f'assert({match[0]} == {match[1]})')

        return assertions
    
    def add_invariant_assertions(self, formula: str):
        assertion = f'assert({formula});'
        code = ''
        loop_scope_balance = None
        for line in self.code.splitlines():
            if 'while' in line:
                loop_scope_balance = 1
                code += f'   {assertion}\n{line}\n       {assertion}\n'
                continue

            if loop_scope_balance and '{' in line:
                loop_scope_balance += 1
            if loop_scope_balance and '}' in line:
                loop_scope_balance -= 1

            if loop_scope_balance == 0:
                code += f'  }}\n  {assertion}\n}}'
                break

            code += f'{line}\n'
            
        if '#include <assert.h>' not in code:
            code = f'#include <assert.h>\n{code}'

        if '#include <stdlib.h>' not in code:
            code = f'#include <stdlib.h>\n{code}'

        code = code.replace('unknown()','rand()%2==0')

        return code
