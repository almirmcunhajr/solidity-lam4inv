// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int invalid, int unowned, int nonexclusive, int exclusive, int RETURN) {
        unowned = 0;
        nonexclusive = 0;
        exclusive = 0;
        require(invalid >= 1, "failed pre-condition");

        while (!((nonexclusive + unowned) >= 1 && invalid >= 1)) {
            if (invalid >= 1) {
                if (unknown()) {
                    nonexclusive = nonexclusive + exclusive;
                    exclusive = 0;
                    invalid = invalid - 1;
                    unowned = unowned + 1;
                } else {
                    exclusive = 1;
                    unowned = 0;
                    nonexclusive = 0;
                }
            } else if ((nonexclusive + unowned) >= 1) {
                invalid = invalid + unowned + nonexclusive - 1;
                nonexclusive = 0;
                exclusive = exclusive + 1;
                unowned = 0;
            }
        }
        
        if ((nonexclusive + unowned) >= 1 && invalid >= 1) {
            assert((invalid + unowned + exclusive) >= 1);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}