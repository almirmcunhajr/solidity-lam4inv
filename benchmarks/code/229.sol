// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x) {
        require(x == 1 || x == 2, "failed pre-condition");
        while (unknown()) {
            if (x == 1) {
                x = 2;
            } else if (x == 2) {
                x = 1;
            }
        }
        assert(x <= 8);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}