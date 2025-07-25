pragma solidity ^0.8.0;

contract LoopExample {
    uint256 public x;
    uint256 public y;

    constructor() {
        // pre-conditions
        x = 1;
        y = 0;

        // loop body
        while (y < x + 100000) {
            x = x + y;
            y = y + 1;
        }

        // post-condition
        assert(x >= y);
    }
}
