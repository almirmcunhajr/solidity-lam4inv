// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y) {
        require(y > 0 || x > 0, "failed pre-condition");
        while (x + y <= -2) {
            if (x > 0) {
                x++;
            } else {
                y++;
            }
        }
        assert(x > 0 || y > 0);
    }

    function unknown() private view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}