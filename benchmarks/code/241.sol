// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    int256 private constant SCALE = 1e18;

    constructor(int256 x, int256 octant, int256 oddExp, int256 evenExp, int256 term, uint256 count, int256 multFactor, int256 temp) {
        octant = int256(3141590000000000000) / 3;
        require(x > 0, "failed pre-condition");
        require(x < octant, "failed pre-condition");
        oddExp = x;
        evenExp = SCALE;
        term = x;
        count = 2;
        multFactor = 0;

        while (unknown()) {
            int256 xOverCount = x / int256(count);
            term = (term * xOverCount) / SCALE;

            if (((count / 2) % 2) == 0) {
                multFactor = 1;
            } else {
                multFactor = -1;
            }

            evenExp = evenExp + multFactor * term;

            count = count + 1;

            xOverCount = x / int256(count);
            term = (term * xOverCount) / SCALE;

            oddExp = oddExp + multFactor * term;

            count = count + 1;
        }

        assert(oddExp >= evenExp);
    }

    function unknown() private view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}