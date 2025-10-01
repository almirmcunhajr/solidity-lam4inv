// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y, int xa, int ya) {
        xa = 0;
        ya = 0;

        while (unknown()) {
            x = xa + ya * 2 + 1;
            if (unknown()) {
                y = ya - xa * 2 + x;
            } else {
                y = ya - xa * 2 - x;
            }
            xa = x - y * 2;
            ya = x * 2 + y;
        }

        assert(xa + ya * 2 >= 0);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}