// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int n, int x, int y) {
        require(n >= 0, "failed pre-condition");
        i = 0;
        x = 0;
        y = 0;
        while (i < n) {
            i = i + 1;
            if (unknown()) {
                x = x + 1;
                y = y + 2;
            } else {
                x = x + 2;
                y = y + 1;
            }
        }
        assert(3 * n == x + y);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}