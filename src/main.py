import argparse
import os
import re
from dotenv import load_dotenv

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
from bmc.esbmc import ESBMC
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

def run_experiment(
        code_file_path: str,
        z3_solver: Z3Solver, 
        pipeline: list[tuple[LLM, float]],
        bmc: BMC,
        max_chat_interactions: int,
        log_level: str
):
    code_handler = get_solidity_code_handler(code_file_path)
    formula_handler = get_solidity_formula_handler()
    vc_generator = get_solidity_vc_generator(code_file_path)
    z3_inv_smt_solver = InvSMTSolver(z3_solver, vc_generator)
    generator = Generator(code_handler)
    predicate_filtering = PredicateFiltering(code_handler, formula_handler, bmc)
    runner = Runner(
        inv_smt_solver=z3_inv_smt_solver, 
        predicate_filtering=predicate_filtering, 
        generator=generator, 
        pipeline=pipeline,
        formula_handler=formula_handler,
        code_handler=code_handler, 
        presence_penalty_scale=0.2,
        max_chat_interactions=max_chat_interactions,
        log_level=log_level
    )
    
    invariant = runner.run()

    return invariant

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

def main():
    parser = argparse.ArgumentParser(description="Run benchmarks")

    parser.add_argument("--pipeline", type=parse_pipeline, default=f'{ChatGPTModel.GPT_4O.value}, 0; {ChatGPTModel.GPT_4O_MINI.value}, 40; {ChatGPTModel.O3_MINI.value}, 300; {DeepseekModel.DEEPSEEK_R1.value}, 600', help="Pipeline of LLM models with their timeouts in seconds, formatted as: model, timeout; model, timeout;... Example: gpt-4,120;deepseek,300")
    parser.add_argument("--smt-timeout", type=int, default=50, help="Timeout for the SMT check")
    parser.add_argument("--bmc-timeout", type=float, default=5, help="Timeout for BMC")
    parser.add_argument("--bmc-max-steps", type=int, default=10, help="Maximum number of steps for BMC")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["INFO", "CRITICAL", "ERROR", "WARNING", "DEBUG"], help="Logging level")
    parser.add_argument("--max-chat-interactions", type=int, default=-1, help="Max chat interactions with the LLM model")
    parser.add_argument("--file", type=str, help="Code file path")

    args = parser.parse_args()

    pipeline = [(get_llm(model), threshold) for model, threshold in args.pipeline]
    z3_solver = Z3Solver(args.smt_timeout)
    esbmc = ESBMC(config.esbmc_bin_path, args.bmc_timeout, args.bmc_max_steps)

    run_experiment( args.file, z3_solver, pipeline, esbmc, args.max_chat_interactions, args.log_level)

if __name__ == "__main__":
    main()
