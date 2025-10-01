// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LoopExample {
    constructor(int x1, int x2, int x3, int v1, int v2, int v3, int t) {
        x1 = 100;
        x2 = 75;
        x3 = -50;
        t = 0;
        require(v3 >= 0, "failed pre-condition");
        require(v1 <= 5, "failed pre-condition");
        require((v1 - v3) >= 0, "failed pre-condition");
        require(v2 * 2 - v1 - v3 == 0, "failed pre-condition");
        require(v2 + 5 >= 0, "failed pre-condition");
        require(v2 <= 5, "failed pre-condition");
        while (v2 + 5 >= 0 && v2 <= 5) {
            x1 = x1 + v1;
            x3 = x3 + v3;
            x2 = x2 + v2;
            if (x2 * 2 - x1 - x3 >= 0) {
                v2 = v2 - 1;
            } else if (x2 * 2 - x1 - x3 <= 0) {
                v2 = v2 + 1;
            }
            t = t + 1;
        }
        assert(v1 <= 5);
    }

    function unknown() private view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}