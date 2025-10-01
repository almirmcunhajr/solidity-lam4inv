pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int w, int x, int y, int z) {
        x = w;
        z = x + 1;
        y = w + 1;
        require(x > 0, "failed pre-condition");
        require(y > 0, "failed pre-condition");
        require(z > 0, "failed pre-condition");
        require(w > 0, "failed pre-condition");
        while (unknown()) {
            y = y + 1;
            z = z + 1;
        }
        assert(y == z);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}