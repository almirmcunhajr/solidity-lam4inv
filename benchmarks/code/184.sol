// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int i, int j, int n, int k) {
        i = 0;
        j = 0;
        require(n == 1 || n == 2, "failed pre-condition");
        while (i <= k) {
            i = i + 1;
            j = j + n;
        }
        if (i > k && n == 1) {
            assert(i == j);
        }
    }

    function unknown() external view returns (bool) {
        bytes32 rand = keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number));
        return uint256(rand) % 2 == 0;
    }
}