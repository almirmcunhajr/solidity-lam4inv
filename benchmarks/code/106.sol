// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int a, int m, int j, int k) {
        require(a <= m, "failed pre-condition");
        require(j < 1, "failed pre-condition");
        k = 0;
        while (k < 1) {
            if (m < a) {
                m = a;
            }
            k = k + 1;
        }
        assert(a <= m);
    }

    function unknown() external view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}