// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int j, int n, int k, int b) {
        n = 0;
        b = 0;
        require(k > 0, "failed pre-condition");
        require(k < 20000001, "failed pre-condition");
        require(i == j, "failed pre-condition");

        while (n < (2 * k)) {
            n = n + 1;
            if (b == 1) {
                b = 0;
                i = i + 1;
            } else {
                b = 1;
                j = j + 1;
            }
        }

        if (n >= (2 * k)) 
            assert(i == j);
    }

    function unknown() public view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}