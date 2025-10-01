// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int x, int y, int n) {
        n = 0;
        require(x >= 0, "failed pre-condition");
        require(y >= 0, "failed pre-condition");
        require(x == y, "failed pre-condition");
        while (x != n) {
            x = x - 1;
            y = y - 1;
        }
        if (x == n) {
            assert(y == n);
        }
    }

    function unknown() external view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}