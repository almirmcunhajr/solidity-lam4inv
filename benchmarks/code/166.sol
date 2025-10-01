// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y, int k, int j, int i, int n, int m) {
        m = 0;
        j = 0;
        require((x + y) == k, "failed pre-condition");
        while (j < n) {
            if (j == i) {
                x = x + 1;
                y = y - 1;
                j = j + 1;
                if (unknown()) {
                    m = j;
                }
            } else if (j != i) {
                x = x - 1;
                y = y + 1;
                j = j + 1;
                if (unknown()) {
                    m = j;
                }
            }
        }
        if (j >= n) {
            assert((x + y) == k);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}