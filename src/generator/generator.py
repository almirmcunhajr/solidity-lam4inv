from typing import Optional
import re

from llm.llm import LLM, ChatOptions, Chat
from inv_smt_solver.counter_example import CounterExample, CounterExampleKind
from code_handler.code_handler import CodeHandler

class Generator:
    def __init__(self, code_handler: CodeHandler):
        self.code_handler = code_handler
        self._chat = Chat()

    def get_messages(self):
        return self._chat.messages

    def _get_base_llm_message(self) -> str:
        return f"""{self.code_handler.get_code()}
Print loop invariants as valid {self.code_handler.get_language().value} assertions that help prove the assertion.

In order to get a correct answer, You may want to consider both the situation of not entering the loop and the situation of jumping out of the loop.

If some of the preconditions are also loop invariant, you need to add them to your answer as well.

Use boolean operators if necessary. Don't explain. Your answer should contain only '{self.code_handler.get_assert_format()}' lines.
"""
    
    def _format_feedback(self, fails: list[tuple[str, CounterExample]]) -> str:
        fails_prompt = ""
        for (candidate, counter_example) in fails:
            if counter_example.kind == CounterExampleKind.NOT_REACHABLE:
                fails_prompt += f'   - "{candidate}": The invariant I can\'t be can be derived based on the pre-condition P, i.e. P ⇒ I was not satisfied. For this property, in order to get a correct answer, you may want to consider the initial situation where the program won\'t enter the loop. The counter example is: {counter_example}\n'
            elif counter_example.kind == CounterExampleKind.NOT_PROVABLE:
                fails_prompt += f'   - "{candidate}": The invariant I is not provable. After unsatisfying loop condition B, the post-condition Q can\' be proven, i.e. (I ∧ ¬ B) ⇒ Q was not satisfied. For this property, in order to get a correct answer, you may want to consider the special case of the program executing to the end of the loop. The counter example is: {counter_example}\n'
            elif counter_example.kind == CounterExampleKind.NOT_INDUCTIVE:
                fails_prompt += f'   - "{candidate}": The invariant I is not inductivene, i.e., when the program state satisfies the loop condition B, the new state obtained after the loop execution S is not satisfied, i.e. {{I ∧ B}} S {{I}} was not satisfied. For this property, in order to get a correct answer, You may want to consider the special case of the program executing to the end of the loop. The counter example is: {counter_example}\n'
        return fails_prompt
    
    def _get_feedback_llm_message(self, last_fails: list[tuple[str, CounterExample]]) -> str:
        return f"""Your previous proposals were verified and have failed as they break some properties of a correct loop invariant:
{self._format_feedback(last_fails)}

**IMPORTANT:** Only generate loop invariants that **have not failed before**!
"""
        
    def _parse_llm_response(self, output: str) -> list[str]:
        expressions = []
        pattern = re.compile(self.code_handler.get_assert_pattern())
        matches = pattern.findall(output)
        for match in matches:
            expressions.append(match)
        return expressions

    def generate(self, llm: LLM, feedback: Optional[list[tuple[str, CounterExample]]] = None, chat_options: Optional[ChatOptions] = None) -> list[str]:
        if feedback:
            message = self._get_feedback_llm_message(feedback)
        else:
            message = self._get_base_llm_message()
        self._chat.add_user_message(message)

        response = llm.chat(self._chat, chat_options)
        self._chat.add_assistant_response(response)

        return self._parse_llm_response(response)

    def reset(self):
        self._chat.reset()
