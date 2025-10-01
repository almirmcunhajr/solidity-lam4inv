// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int y) {
        require((x >= 0), "failed pre-condition");
        require((x <= 10), "failed pre-condition");
        require((y <= 10), "failed pre-condition");
        require((y >= 0), "failed pre-condition");

        while (unknown()) {
            x = x + 10;
            y = y + 10;
        }

        if (y == 0) {
            assert(x != 20);
        }
    }

    function unknown() private view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}