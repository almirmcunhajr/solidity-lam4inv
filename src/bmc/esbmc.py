import tempfile
import os
import logging
from typing import Optional

from bmc.bmc import BMC, InvalidCodeError
from utils.utils import run_command_with_timeout

class ESBMC(BMC):
    def __init__(self, bin_path: str, timeout: float, max_k_step: Optional[int] = None):
        self.bin_path = bin_path
        self.timeout = timeout
        self.max_k_step = max_k_step
        pass

    def verify(self, code: str, fmt: str, logger: logging.Logger) -> bool:
        tmp_dir = tempfile.mkdtemp()
        tmp_file = os.path.join(tmp_dir, f"main.{fmt}")
        with open(tmp_file, "w") as f:
            f.write(code)
        
        cmd = [self.bin_path, tmp_file, '--floatbv', '--k-induction']
        if self.max_k_step:
            cmd.extend(['--max-k-step', str(self.max_k_step)])
        try:
            _, stderr = run_command_with_timeout(cmd, self.timeout)
            if 'VERIFICATION FAILED' in stderr:
                return False
            if 'VERIFICATION UNKNOWN' in stderr: 
                return True
            if 'VERIFICATION SUCCESSFUL' in stderr:
                return True
            raise InvalidCodeError(stderr)
        except TimeoutError:
            logger.error("ESBMC timed out")
            return False
