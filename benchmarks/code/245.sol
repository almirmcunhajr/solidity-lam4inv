// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int last, int a, int b, int c, int st) {
        a = 0;
        b = 0;
        c = 200000;
        require((st == 0 && last < c) || (st == 1 && last >= c), "failed pre-condition");
        while (unknown()) {
            if (st == 0 && c == last + 1) {
                a = a + 3;
                b = b + 3;
            } else {
                a = a + 2;
                b = b + 2;
            }
            if (c == last && st == 0) {
                a = a + 1;
                c = c + 1;
            }
        }
        assert(c == 200000);
    }

    function unknown() private view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}