// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int w, int x, int y, int z) {
        x = w;
        z = y;
        require(x > 0, "failed pre-condition");
        require(y > 0, "failed pre-condition");
        require(z > 0, "failed pre-condition");
        require(w > 0, "failed pre-condition");

        while (unknown()) {
            if (unknown()) {
                w = w + 1;
                x = x + 1;
            } else {
                y = y - 1;
                z = z - 1;
            }
        }

        assert(y == z);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}