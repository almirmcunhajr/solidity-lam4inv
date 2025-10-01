// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y, int i, int j, int k, int m, int n) {
        m = 0;
        j = 0;
        require(k == x + y, "failed pre-condition");
        while (j < n) {
            if (unknown()) {
                m = j;
            }
            if (j == i) {
                x = x + 1;
                y = y - 1;
            } else {
                x = x - 1;
                y = y + 1;
            }
            j = j + 1;
        }
        if (n > 0) {
            assert(m >= 0);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}