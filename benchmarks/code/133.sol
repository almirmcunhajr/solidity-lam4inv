// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int n, int x) {
        x = 0;
        require(n >= 0, "failed pre-condition");
        while (x < n) {
            x = x + 1;
        }
        assert(x == n);
    }

    function unknown() public view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}