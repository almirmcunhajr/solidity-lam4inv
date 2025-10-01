// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(int x, int n, int m) {
        x = 0;
        m = 0;
        require(n > 0, "failed pre-condition");
        while (x < n) {
            if (unknown()) {
                m = x;
            }
            x = x + 1;
        }
        if (x >= n && n > 0) {
            assert(0 <= m);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}