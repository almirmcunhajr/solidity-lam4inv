// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y) {
        require(x <= 5, "failed pre-condition");
        require(x >= 4, "failed pre-condition");
        require(y <= 5, "failed pre-condition");
        require(y >= 4, "failed pre-condition");
        while (unknown()) {
            if (x >= 0 && y >= 0) {
                x = x - 1;
            } else if (x < 0 && y >= 0) {
                y = y - 1;
            } else if (y < 0) {
                x = x + 1;
                y = y - 1;
            }
        }
        assert(y <= 5);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}