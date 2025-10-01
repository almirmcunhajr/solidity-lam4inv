// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int j, int k) {
        i = 1;
        j = 1;
        require(k >= 0, "failed pre-condition");
        require(k <= 1, "failed pre-condition");
        while (unknown()) {
            i = i + 1;
            j = j + k;
            k = k - 1;
        }
        assert(i >= 1);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}