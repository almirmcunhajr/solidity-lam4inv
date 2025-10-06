import argparse
import logging
import os
import re
from typing import Optional
from dotenv import load_dotenv

from crosscheck.crosscheck import CrossCheck
from code_handler.code_handler import CodeHandler
from code_handler.formula_handler import FormulaHandler
from runner import Runner
from config import config
from smt.z3_solver import Z3Solver
from inv_smt_solver.inv_smt_solver import InvSMTSolver
from llm.llm import LLM
from llm.openai import OpenAI, ChatGPTModel, DeepseekModel
from generator.generator import Generator
from code_handler.solidity_code_handler import SolidityCodeHandler
from code_handler.solidity_formula_handler import SolidityFormulaHandler
from vc.solidity_generator import SolidityGenerator
from bmc.solc import Solc
from bmc.bmc import BMC
from predicate_filtering.predicate_filtering import PredicateFiltering

results_dir = "benchmarks/results"

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

chatgpt_models = [model.value for model in list(ChatGPTModel)]
deepseek_models = [model.value for model in list(DeepseekModel)]
all_models = chatgpt_models + deepseek_models

def get_solidity_code_handler(code_file_path: str, contract_name: str, function_name: str) -> SolidityCodeHandler:
    with open(code_file_path, "r") as f:
        code = f.read()
    return SolidityCodeHandler(code, contract_name, function_name)

def run(
        code_handler: CodeHandler,
        formula_handler: FormulaHandler,
        z3_inv_smt_solver: InvSMTSolver,
        generator: Generator,
        predicate_filtering: PredicateFiltering,
        pipeline: list[tuple[LLM, float]],
        max_chat_interactions: int,
        logger: logging.Logger,
        output_path: Optional[str] = None
):
    runner = Runner(
        inv_smt_solver=z3_inv_smt_solver, 
        predicate_filtering=predicate_filtering, 
        generator=generator, 
        pipeline=pipeline,
        formula_handler=formula_handler,
        code_handler=code_handler, 
        presence_penalty_scale=0.2,
        logger=logger,
        max_chat_interactions=max_chat_interactions,
        output_path=output_path
    )
    
    invariant = runner.run()

    runner.reset()

    return invariant

def run_results_analysis(bounds: tuple[int, int], logger: logging.Logger):
    if not os.path.exists(results_dir):
        logger.error(f"Results directory {results_dir} does not exist")
        return

    solutions_found_regex = re.compile(r'Solution found by (.*):')
    solutions_by_model: dict[str, int] = {}
    for benchmark_index in range(bounds[0], bounds[1]+1):
        result_file_path = f"{results_dir}/{benchmark_index}.txt"
        if not os.path.exists(result_file_path):
            logger.warning(f"Result file {result_file_path} does not exist")
            continue
        with open(result_file_path, "r") as f:
            result = f.read()

        match = solutions_found_regex.search(result)
        if match:
            model = match.group(1)
            if model not in solutions_by_model:
                solutions_by_model[model] = 0
            solutions_by_model[model] += 1
            continue

        logger.warning(f"No solution found in the result file {result_file_path}")

    logger.info("Results analysis:")
    for model, count in solutions_by_model.items():
        logger.info(f"Model {model} found {count} solutions")
    logger.info(f"Total solutions found: {sum(solutions_by_model.values())} out of {bounds[1] - bounds[0] + 1} benchmarks")

def run_benchmark(
        z3_solver: Z3Solver,
        formula_handler: FormulaHandler,
        pipeline: list[tuple[LLM, float]],
        bmc: BMC,
        max_chat_interactions: int,
        benchmark_index: int,
        logger: logging.Logger
):

    code_file_path = f"benchmarks/code/{benchmark_index}.sol"
    result_file_path = f"benchmarks/results/{benchmark_index}.txt"
    
    contract_name = "LoopExample"
    function_name = "constructor"

    code_handler = get_solidity_code_handler(code_file_path, contract_name, function_name)
    vc_generator = SolidityGenerator(code_file_path, logger, contract_name, function_name)
    z3_inv_smt_solver = InvSMTSolver(z3_solver, vc_generator, logger)
    generator = Generator(code_handler)
    predicate_filtering = PredicateFiltering(code_handler, formula_handler, bmc, logger)

    print(f"Running benchmark for benchmark {benchmark_index}")
    try:
        inv_formula = run(
            code_handler=code_handler,
            formula_handler=formula_handler,
            z3_inv_smt_solver=z3_inv_smt_solver,
            generator=generator,
            predicate_filtering=predicate_filtering,
            pipeline=pipeline,
            max_chat_interactions=max_chat_interactions,
            logger=logger,
            output_path=result_file_path
        )
        if inv_formula is None:
            logger.error(f"Benchmark {benchmark_index} failed to find an invariant")
            if os.path.exists(result_file_path):
                os.remove(result_file_path)
            return
    except Exception as e:
        logger.error(f"Benchmark {benchmark_index} failed with error: {e}")
        if os.path.exists(result_file_path):
            os.remove(result_file_path)
        return

    inv_formula = formula_handler.extract_formula(inv_formula)
    inv = formula_handler.to_smt_lib2(inv_formula)

    crosscheck = CrossCheck(z3_solver)

    crosscheck_vc_template_path = f"benchmarks/cross-checks-templates/{benchmark_index}.txt"
    with open(crosscheck_vc_template_path, "r") as f:
        crosscheck_vc_template = f.read()

    crosscheck_ce = crosscheck.check(inv, crosscheck_vc_template)
    if crosscheck_ce is not None:
        logger.error(f"Cross check failed for the benchmark {benchmark_index}")
        os.remove(result_file_path)

    print(f"Cross check succeeded for the benchmark {benchmark_index}")

    print(f"Benchmark {benchmark_index} finished")

def run_benchmarks(
        z3_solver: Z3Solver,
        formula_handler: FormulaHandler,
        bmc: BMC,
        pipeline: list[tuple[LLM, float]],
        max_chat_interactions: int,
        bounds:tuple[int, int],
        logger: logging.Logger
):

    for benchmark_index in range(bounds[0], bounds[1]+1):
        run_benchmark(
            z3_solver=z3_solver,
            formula_handler=formula_handler,
            bmc=bmc,
            pipeline=pipeline,
            max_chat_interactions=max_chat_interactions,
            benchmark_index=benchmark_index,
            logger=logger
        )

    run_results_analysis(bounds, logger)

def get_llm(model:str) -> LLM:
    if model in chatgpt_models:
        if OPENAI_API_KEY is None:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        return OpenAI(ChatGPTModel(model), OPENAI_API_KEY)
    if model in deepseek_models:
        if DEEPSEEK_API_KEY is None:
            raise ValueError("DEEPSEEK_API_KEY environment variable must be set")
        return OpenAI(DeepseekModel(model), DEEPSEEK_API_KEY, base_url=config.deepseek_api_url)
    raise ValueError(f"Model {model} not found")

def parse_pipeline(input: str) -> list[tuple[LLM, float]]:
    pipeline = []
    for step in input.split(";"):
        model, timeout = step.split(",")
        model = model.strip()
        if model not in all_models:
            raise argparse.ArgumentTypeError(f"Model {model} not found")
        timeout = float(timeout.strip())
        pipeline.append((model, timeout))
    return pipeline

def parse_range(input: str) -> tuple[int, int]:
    pattern = re.compile(r'^(\d+)(?:,(\d+))?$')
    match = pattern.match(input)
    if not match:
        raise argparse.ArgumentTypeError("Range must be in the format start,end")
    start, end = match.groups()
    if end is None:
        end = start 
    start = int(start)
    end = int(end)
    if start > end:
        raise argparse.ArgumentTypeError("Start must be less than or equal to end")
    return (start, end)

def main():
    parser = argparse.ArgumentParser(description="Invariant Generation Tool for Solidity Smart Contracts")

    parser.add_argument("--pipeline", type=parse_pipeline, default=f'{ChatGPTModel.GPT_5_NANO.value}, 0; {ChatGPTModel.GPT_5_MINI.value}, 120; {ChatGPTModel.GPT_5.value}, 300; {ChatGPTModel.GPT_4O.value}, 0; {ChatGPTModel.GPT_4O_MINI.value}, 40', help="Pipeline of LLM models with their timeouts in seconds, formatted as: model, timeout; model, timeout;... Example: gpt-4,120;deepseek,300")
    parser.add_argument("--smt-timeout", type=int, default=50, help="Timeout for the SMT check")
    parser.add_argument("--bmc-timeout", type=float, default=5, help="Timeout for BMC")
    parser.add_argument("--bmc-max-steps", type=int, default=10, help="Maximum number of steps for BMC")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["INFO", "CRITICAL", "ERROR", "WARNING", "DEBUG"], help="Logging level")
    parser.add_argument("--max-chat-interactions", type=int, default=-1, help="Max chat interactions with the LLM model")
    parser.add_argument("--file", type=str, help="Code file path")
    parser.add_argument("--contract-name", type=str, default="LoopExample", help="Contract name in the Solidity file")
    parser.add_argument("--function-name", type=str, default="constructor", help="Function name in the Solidity file")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    parser.add_argument("--benchmarks", type=parse_range, default=None, help="Run a range of benchmarks, formatted as: start,end. Example: 1,10")
    parser.add_argument("--analysis", type=parse_range, default=None, help="If provided, runs only the results analysis for the given range of benchmarks, formatted as: start,end. Example: 1,10")

    args = parser.parse_args()

    logger = logging.getLogger("main")
    logger.setLevel(getattr(logging, args.log_level))

    if args.analysis:
        run_results_analysis(args.analysis, logger)
        return

    pipeline = [(get_llm(model), threshold) for model, threshold in args.pipeline]
    z3_solver = Z3Solver(args.smt_timeout)
    solc = Solc(config.solc_bin_path, args.bmc_timeout, logger, args.bmc_max_steps)
    formula_handler = SolidityFormulaHandler()
    
    if args.benchmarks:
        run_benchmarks(z3_solver, formula_handler, solc, pipeline, args.max_chat_interactions, args.benchmarks, logger)
        return

    if args.file is None:
        parser.error("--file is required if --benchmarks is not provided")

    code_handler = get_solidity_code_handler(args.file, args.contract_name, args.function_name)
    vc_generator = SolidityGenerator(args.file, logger, args.contract_name, args.function_name)
    z3_inv_smt_solver = InvSMTSolver(z3_solver, vc_generator, logger)
    generator = Generator(code_handler)
    predicate_filtering = PredicateFiltering(code_handler, formula_handler, solc, logger)
    run(
        code_handler=code_handler,
        formula_handler=formula_handler,
        z3_inv_smt_solver=z3_inv_smt_solver,
        generator=generator,
        predicate_filtering=predicate_filtering,
        pipeline=pipeline,
        max_chat_interactions=args.max_chat_interactions,
        output_path=args.output,
        logger=logger
    )

if __name__ == "__main__":
    main()
