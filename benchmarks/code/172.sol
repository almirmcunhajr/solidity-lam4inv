// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int n, int sum) {
        sum = 0;
        i = 0;
        require(n > 0, "failed pre-condition");
        while (i < n) {
            sum = sum + i;
            i = i + 1;
        }
        if (i >= n) {
            assert(sum >= 0);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}