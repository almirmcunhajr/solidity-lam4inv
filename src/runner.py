import time
import logging
import math
from typing import Optional

from bmc.bmc import InvalidCodeError
from inv_smt_solver.counter_example import CounterExample
from smt.solver import InvalidSMTLIB2FormulaError
from code_handler.formula_handler import InvalidCodeFormulaError
from inv_smt_solver.inv_smt_solver import InvSMTSolver
from generator.generator import Generator
from code_handler.formula_handler import FormulaHandler
from code_handler.code_handler import CodeHandler
from predicate_filtering.predicate_filtering import PredicateFiltering
from llm.llm import LLM, ChatOptions

class Runner:
    def __init__(
        self, 
        inv_smt_solver: InvSMTSolver, 
        predicate_filtering: PredicateFiltering,
        generator: Generator,
        pipeline: list[tuple[LLM, float]],
        formula_handler: FormulaHandler,
        code_handler: CodeHandler,
        presence_penalty_scale: float,
        max_chat_interactions = 0,
        log_level:str = str(logging.INFO)
    ):
        self.inv_smt_solver = inv_smt_solver
        self.predicate_filtering = predicate_filtering
        self.generator = generator
        self.pipeline = pipeline
        self.formula_handler = formula_handler
        self.code_handler = code_handler

        self.presence_penalty_scale = presence_penalty_scale
        self.max_chat_interactions = max_chat_interactions
        
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        console_log_handler = logging.StreamHandler()
        console_log_handler.setLevel(log_level)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_log_handler.setFormatter(formatter)
        
        self._logger.addHandler(console_log_handler)

        self.reset()

    def _log_solution(self, solution: Optional[str], llm: Optional[LLM], start_time: float, predicate_filtering: bool):
        self._logger.info('# Result')
        if solution is None:
            self._logger.info(f'No solution found')
        if solution is not None and predicate_filtering:
            self._logger.info(f'Solution found by the predicate filtering mechanism using the {llm} model: {solution}')
        if solution is not None and not predicate_filtering:
            self._logger.info(f'Solution found by the {llm} model: {solution}')
        
        end_time = time.time()
        self._logger.info(f'{len(self._fail_history)} counter examples were generated for the model proposals, with {self._fail_history_hit} repeated fails')
        self._logger.info(f'The model runtime was {end_time - (self._curr_pipeline_step_activation_time or end_time)} seconds')
        self._logger.info(f'The total runtime was {end_time - start_time} seconds')

    def _handle_solution(self, solution: Optional[str], llm: Optional[LLM], start_time: float, predicate_filtering:bool = False) -> str:
        self._log_solution(solution, llm, start_time, predicate_filtering)
        self.reset()
        return solution if solution else ""
    
    def _next_pipeline_step(self) -> tuple[Optional[LLM], float]:
        if self._curr_pipeline_step_index is None:
            self._curr_pipeline_step_activation_time = time.time()
            self._curr_pipeline_step_index = 0
            return self.pipeline[0]

        time_spent = time.time() - self._curr_pipeline_step_activation_time
        curr_step = self.pipeline[self._curr_pipeline_step_index]
        if time_spent >= curr_step[1] and self._curr_pipeline_step_index == len(self.pipeline) - 1:
            return None, 0
        if time_spent >= curr_step[1]:
            self._reset_generator()
            self._curr_pipeline_step_index += 1
            self._curr_pipeline_step_activation_time = time.time()
        
        return self.pipeline[self._curr_pipeline_step_index]
    
    def _get_presence_penalty(self) -> float:
        return math.tanh(self._fail_history_hit * self.presence_penalty_scale)
    
    def _predicate_filtering(self, candidates: list[str]) -> Optional[str]:
        verify = False
        for candidate in candidates:
            self._logger.info(f'Filtering predicates for candidate {candidate}')
            formula = self.formula_handler.extract_formula(candidate)
            filtered_predicates = self.predicate_filtering.filter(formula, self._logger)
            for predicate in filtered_predicates:
                if predicate not in self._predicate_filtering_verify_set:
                    verify = True
                    self._logger.info(f'Addind predicate {predicate} to verify set')
                self._predicate_filtering_verify_set[predicate] = True
        
        self._logger.info(f'Predicate filtering verify set: {list(self._predicate_filtering_verify_set.keys())}')    
        if verify:
            formula = ' && '.join([f'({predicate})' for predicate in self._predicate_filtering_verify_set.keys()])
            smt_lib2_formula = self.formula_handler.to_smt_lib2(formula)

            self._logger.info(f'Verifying formula: {smt_lib2_formula}')
            self._logger.info(f'For candidate: assert({formula})')
            counter_example = self.inv_smt_solver.get_counter_example(smt_lib2_formula)
            if counter_example is None:
                return f'assert({formula})'

        return None
    
    def _verify_candidates(self, candidates: list[str]) -> tuple[Optional[str], list[tuple[str, CounterExample]]]:
        fails = []
        for candidate in candidates:
            self._logger.info(f'Verifying candidate: {candidate}')

            if candidate in self._fail_history:
                self._fail_history_hit += 1
                fails.append((candidate, (self._fail_history[candidate])))
                self._logger.info(f'Candidate already in fail history: {candidate}')
                continue

            formula = self.formula_handler.extract_formula(candidate)
            smt_lib2_formula = self.formula_handler.to_smt_lib2(formula)
            counter_example = self.inv_smt_solver.get_counter_example(smt_lib2_formula)
            if counter_example is None:
                return candidate, fails
            
            self._logger.info(f'Candidate failed verification')
            fails.append((candidate, counter_example))
            
            self._logger.info(f'Adding candidate to fail history: {candidate}')
            self._fail_history[candidate] = counter_example
        
        return None, fails

    def run(self) -> str:
        start_time = time.time()

        self._logger.info(f'Executing predicate filtering for preconditions')
        preconditions = self.code_handler.get_preconditions()
        solution = self._predicate_filtering(preconditions)
        if solution is not None:
            self._logger.info(f'Predicate filtering found solution: {solution}')
            return self._handle_solution(solution, None, start_time, predicate_filtering=True)
        
        chat_options = ChatOptions()
        while True:
            llm, _ = self._next_pipeline_step()
            if llm is None:
                self._handle_solution(None, None, start_time)
                raise TimeoutError('Pipeline time exceeded')

            chat_options.presence_penalty = self._get_presence_penalty()
            
            self._logger.info(f'Generating loop invariants candidates with model {llm} and presence penalty {chat_options.presence_penalty}')
            candidates = self.generator.generate(feedback=self._last_fails, llm=llm, chat_options=chat_options)
            self._logger.info(f'Generated {len(candidates)} candidates')
            
            try:
                self._logger.info(f'Verifying generated candidates')
                solution, self._last_fails = self._verify_candidates(candidates)
                if solution is not None:
                    return self._handle_solution(solution, llm, start_time)
                
                if self.max_chat_interactions > 0 and len(self.generator.get_messages()) >= self.max_chat_interactions:
                    self._reset_generator()

                self._logger.info(f'Executing predicate filtering')
                solution = self._predicate_filtering(candidates)
                if solution is not None:
                    self._logger.info(f'Predicate filtering found solution: {solution}')
                    return self._handle_solution(solution, llm, start_time, predicate_filtering=True)
            except InvalidCodeFormulaError as e:
                self._logger.error(f'Invalid candidate syntax', e)
                continue
            except InvalidSMTLIB2FormulaError as e:
                self._logger.error(f'Invalid SMT-LIB-2 formula syntax', e)
                continue
            except InvalidCodeError as e:
                self._logger.error(f'Invalid code while filtering predicates for candidate', e)
                continue
            except TimeoutError as e:
                self._logger.error(f'Timeout while verifying candidate', e)
                continue
    
    def _reset_generator(self):
        self._logger.info(f'Resetting generator')
        self._fail_history = {}
        self._fail_history_hit = 0
        self._last_fails: list[tuple[str, CounterExample]] = []
        self.generator.reset()
            
    def reset(self):
        self._predicate_filtering_verify_set = {}
        self._curr_pipeline_step_index = 0
        self._curr_pipeline_step_activation_time = 0
        self._reset_generator()
