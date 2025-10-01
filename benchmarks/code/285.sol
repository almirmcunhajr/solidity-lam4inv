// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(int x, int y, int z) {
        x = 0;
        y = 0;
        z = 0;

        while (x > 0) {
            x++;
            y++;
            z -= 2;
        }

        assert(x + y + z == 0);
    }

    function unknown() public view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}