// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(int c, int n) {
        c = 0;
        require(n > 0, "failed pre-condition");
        while (unknown()) {
            if (unknown()) {
                if (c > n) {
                    c = c + 1;
                }
            } else {
                if (c == n) {
                    c = 1;
                }
            }
        }
        if (c != n) {
            assert(c <= n);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
        }
}