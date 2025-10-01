pragma solidity ^0.8.20;

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
        assert(1 <= i + k);
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encode(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}