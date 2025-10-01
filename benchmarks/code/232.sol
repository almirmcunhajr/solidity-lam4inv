// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LoopExample {
    constructor(uint x, uint y) {
        x = 2;
        require(y > 2, "failed pre-condition");
        while (x < y) {
            if (x < y / x) {
                x *= x;
            } else {
                x++;
            }
        }
        assert(x == y);
    }

    function unknown() public view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}