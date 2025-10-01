// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int sn, int x) {
        sn = 0;
        x = 0;
        while (unknown()) {
            x = x + 1;
            sn = sn + 1;
        }
        if (sn != x) {
            assert(sn == -1);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}