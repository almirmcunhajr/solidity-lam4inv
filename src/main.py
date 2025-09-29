import argparse
import os
import re
from typing import Optional
from dotenv import load_dotenv

from code2inv.code2inv import Code2Inv
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

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

chatgpt_models = [model.value for model in list(ChatGPTModel)]
deepseek_models = [model.value for model in list(DeepseekModel)]
all_models = chatgpt_models + deepseek_models

def get_solidity_code_handler(code_file_path: str) -> SolidityCodeHandler:
    with open(code_file_path, "r") as f:
        code = f.read()
    return SolidityCodeHandler(code)

def get_solidity_vc_generator(code_file_path: str) -> SolidityGenerator:
    generator = SolidityGenerator(code_file_path)
    return generator

def get_solidity_formula_handler() -> SolidityFormulaHandler:
    return SolidityFormulaHandler()

def run(
        code_handler: CodeHandler,
        formula_handler: FormulaHandler,
        z3_inv_smt_solver: InvSMTSolver,
        generator: Generator,
        predicate_filtering: PredicateFiltering,
        pipeline: list[tuple[LLM, float]],
        max_chat_interactions: int,
        log_level: str,
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
        max_chat_interactions=max_chat_interactions,
        log_level=log_level,
        output_path=output_path
    )
    
    invariant = runner.run()

    return invariant

def run_benchmark(
        z3_solver: Z3Solver,
        formula_handler: FormulaHandler,
        pipeline: list[tuple[LLM, float]],
        bmc: BMC,
        max_chat_interactions: int,
        log_level: str,
        benchmark_index: int
):

    code_file_path = f"benchmarks/code/{benchmark_index}.sol"
    result_file_path = f"benchmarks/results/{benchmark_index}.txt"

    code_handler = get_solidity_code_handler(code_file_path)
    vc_generator = get_solidity_vc_generator(code_file_path)
    z3_inv_smt_solver = InvSMTSolver(z3_solver, vc_generator)
    generator = Generator(code_handler)
    predicate_filtering = PredicateFiltering(code_handler, formula_handler, bmc)

    print(f"Running benchmark for benchmark {benchmark_index}")
    inv_formula = run(
        code_handler=code_handler,
        formula_handler=formula_handler,
        z3_inv_smt_solver=z3_inv_smt_solver,
        generator=generator,
        predicate_filtering=predicate_filtering,
        pipeline=pipeline,
        max_chat_interactions=max_chat_interactions,
        log_level=log_level,
        output_path=result_file_path
    )
    if inv_formula is None:
        return

    inv_formula = formula_handler.extract_formula(inv_formula)
    inv = formula_handler.to_smt_lib2(inv_formula)

    code2inv = Code2Inv(z3_solver)

    code2inv_vc_template_path = f"benchmarks/code2inv-vc-templates/{benchmark_index}.txt"
    with open(code2inv_vc_template_path, "r") as f:
        code2inv_vc_template = f.read()

    code2inv_ce = code2inv.check(inv, code2inv_vc_template)
    if code2inv_ce is not None:
        print(f"Code2Inv VC found a counter example for the result of the benchmark {benchmark_index}: {code2inv_ce}")
    print(f"Result for benchmark {benchmark_index} validated by Code2Inv VCs")

    print(f"Benchmark {benchmark_index} finished")

def run_benchmarks(
        z3_solver: Z3Solver,
        formula_handler: FormulaHandler,
        bmc: BMC,
        pipeline: list[tuple[LLM, float]],
        max_chat_interactions: int,
        log_level: str,
        bounds:tuple[int, int]
):

    for benchmark_index in range(bounds[0], bounds[1]+1):
        run_benchmark(
            z3_solver=z3_solver,
            formula_handler=formula_handler,
            bmc=bmc,
            pipeline=pipeline,
            max_chat_interactions=max_chat_interactions,
            log_level=log_level,
            benchmark_index=benchmark_index,
        )

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
    parser = argparse.ArgumentParser(description="Run benchmarks")

    parser.add_argument("--pipeline", type=parse_pipeline, default=f'{ChatGPTModel.GPT_5_MINI.value}, 300; {ChatGPTModel.GPT_5.value}, 600', help="Pipeline of LLM models with their timeouts in seconds, formatted as: model, timeout; model, timeout;... Example: gpt-4,120;deepseek,300")
    parser.add_argument("--smt-timeout", type=int, default=50, help="Timeout for the SMT check")
    parser.add_argument("--bmc-timeout", type=float, default=5, help="Timeout for BMC")
    parser.add_argument("--bmc-max-steps", type=int, default=10, help="Maximum number of steps for BMC")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["INFO", "CRITICAL", "ERROR", "WARNING", "DEBUG"], help="Logging level")
    parser.add_argument("--max-chat-interactions", type=int, default=-1, help="Max chat interactions with the LLM model")
    parser.add_argument("--file", type=str, help="Code file path")
    parser.add_argument("--output", type=str, default=None, help="Output file path")
    parser.add_argument("--benchmarks", type=parse_range, default=None, help="Optionally run a range of benchmarks, formatted as: start,end. Example: 1,10")

    args = parser.parse_args()

    pipeline = [(get_llm(model), threshold) for model, threshold in args.pipeline]
    z3_solver = Z3Solver(args.smt_timeout)
    solc = Solc(config.solc_bin_path, args.bmc_timeout, args.bmc_max_steps)
    formula_handler = get_solidity_formula_handler()

    if args.benchmarks:
        run_benchmarks(z3_solver, formula_handler, solc, pipeline, args.max_chat_interactions, args.log_level, args.benchmarks)
        return

    if args.file is None:
        parser.error("--file is required if --benchmarks is not provided")

    code_handler = get_solidity_code_handler(args.file)
    vc_generator = get_solidity_vc_generator(args.file)
    z3_inv_smt_solver = InvSMTSolver(z3_solver, vc_generator)
    generator = Generator(code_handler)
    predicate_filtering = PredicateFiltering(code_handler, formula_handler, solc)
    run(
        code_handler=code_handler,
        formula_handler=formula_handler,
        z3_inv_smt_solver=z3_inv_smt_solver,
        generator=generator,
        predicate_filtering=predicate_filtering,
        pipeline=pipeline,
        max_chat_interactions=args.max_chat_interactions,
        log_level=args.log_level,
        output_path=args.output
    )

if __name__ == "__main__":
    main()
