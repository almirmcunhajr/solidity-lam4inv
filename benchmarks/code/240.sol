// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int x, int exp, int term, int result, int count) {
        require(x > -1, "failed pre-condition");
        require(x < 1, "failed pre-condition");
        exp = 1;
        term = 1;
        count = 1;
        result = 2 * (1 / (1 - x));
        while (unknown()) {
            term = term * (x / count);
            exp = exp + term;
            count++;
        }
        assert(result >= exp);
    }

    function unknown() internal view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}