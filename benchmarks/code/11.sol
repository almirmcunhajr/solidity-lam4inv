// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(int x, int y) {
        require(x >= 0, "failed pre-condition");
        require(x <= 10, "failed pre-condition");
        require(y <= 10, "failed pre-condition");
        require(y >= 0, "failed pre-condition");
        while (unknown()) {
            x = x + 10;
            y = y + 10;
        }
        if (x == 20) {
            assert(y != 0);
        }
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}