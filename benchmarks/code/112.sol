// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LoopExample {
    constructor(int i, int n, int sn) {
        sn = 0;
        i = 1;
        require(n >= 1, "failed pre-condition");
        while (i <= n) {
            i = i + 1;
            sn = sn + 1;
        }
        if (sn != n) {
            assert(sn == 0);
        }
    }

    function unknown() public view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return (rand % 2 == 0);
    }
}