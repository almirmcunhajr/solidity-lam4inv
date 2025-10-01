// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LoopExample {
    constructor(int x, int octant1, int octant2, int oddExp, int evenExp, int term, int count, int multFactor, int temp) {
        octant1 = 0;
        octant2 = 314159 / 8;
        require(x > octant1, "failed pre-condition");
        require(x < octant2, "failed pre-condition");
        oddExp = x;
        evenExp = 1;
        term = x;
        count = 2;
        multFactor = 0;

        while (unknown()) {
            term = term * (x / count);
            if (((count / 2) % 2) == 0)
                multFactor = 1;
            else
                multFactor = -1;

            evenExp = evenExp + multFactor * term;

            count = count + 1;

            term = term * (x / count);

            oddExp = oddExp + multFactor * term;

            count = count + 1;
        }

        assert(oddExp >= evenExp);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}