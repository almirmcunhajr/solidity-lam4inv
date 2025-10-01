// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int j, int k, int n, int v) {
        k = 0;
        i = 0;
        require(n > 0, "failed pre-condition");
        require(n < 10, "failed pre-condition");
        while (i < n) {
            if (unknown()) {
                i = i + 1;
                k = k + 4000;
                v = 0;
            } else {
                i = i + 1;
                k = k + 2000;
                v = 1;
            }
        }
        if (i >= n) {
            assert(k > n);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}