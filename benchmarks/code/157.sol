// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int a, int j, int m) {
        a = 0;
        j = 1;
        require(m > 0, "failed pre-condition");
        while (j <= m) {
            if (unknown()) {
                a = a + 1;
            } else {
                a = a - 1;
            }
            j = j + 1;
        }
        if (j > m) {
            assert(a >= 0 - m);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}