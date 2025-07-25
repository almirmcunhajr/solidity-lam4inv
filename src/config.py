import os
from dataclasses import dataclass

@dataclass
class Config:
    esbmc_bin_path: str
    deepseek_api_url: str

config = Config(
    esbmc_bin_path="esbmc",
    deepseek_api_url="https://api.deepseek.com"
)
