// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LoopExample {
    constructor(int s) {
        s = 0;
        while (unknown()) {
            if (s != 0) {
                s = s + 1;
            }
        }
        assert(s == 0);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}