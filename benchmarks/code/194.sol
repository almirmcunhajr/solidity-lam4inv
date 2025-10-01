pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int i, int x, int y, int z) {
        x = i;
        y = i;
        z = 0;
        require(i >= 0, "failed pre-condition");
        while (x != 0) {
            x = x - 1;
            y = y - 2;
            z = z + 1;
        }
        assert(y == 0 - z);
    }
}