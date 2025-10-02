import tempfile
import os
import logging
from typing import Optional

from bmc.bmc import BMC, InvalidCodeError
from utils.utils import run_command_with_timeout

class Solc(BMC):
    def __init__(self, bin_path: str, timeout: float, logger: logging.Logger, max_k_step: Optional[int] = None):
        self.bin_path = bin_path
        self.timeout = timeout
        self.max_k_step = max_k_step
        self._logger = logger.getChild(self.__class__.__name__)
        pass

    def verify(self, code: str) -> bool:
        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, "main.sol")
        with open(tmp_file, "w") as f:
            f.write(code)
        
        cmd = [self.bin_path, tmp_file, '--model-checker-engine', 'bmc']
        if self.max_k_step:
            cmd.extend(['--model-checker-bmc-loop-iterations', str(self.max_k_step)])
        if self.timeout:
            cmd.extend(['--model-checker-timeout', str(self.timeout*1000)])
        try:
            _, stderr = run_command_with_timeout(cmd, self.timeout)
            if 'Assertion violation' in stderr:
                return False
            if 'proved safe!' in stderr: 
                return True
            raise InvalidCodeError(stderr)
        except TimeoutError:
            self._logger.error("BMC checker timed out")
            return False
