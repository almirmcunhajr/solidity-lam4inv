import os
from dataclasses import dataclass

@dataclass
class Config:
    solc_bin_path: str
    deepseek_api_url: str

config = Config(
    solc_bin_path="solc",
    deepseek_api_url="https://api.deepseek.com"
)
