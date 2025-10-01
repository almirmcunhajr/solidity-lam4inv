// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(uint i, uint j, uint k) {
        i = 0;
        j = 0;
        k = 0;

        while (k < 268435455) {
            i = i + 1;
            j = j + 2;
            k = k + 3;
        }

        assert(k == 3 * i);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}