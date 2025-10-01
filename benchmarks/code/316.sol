pragma solidity ^0.8.18;

contract LoopExample {
    constructor(uint n, uint j, uint i, uint k) {
        i = 0;
        k = 0;
        j = 0;
        require(n > 0, "failed pre-condition");
        require(n <= 20000001, "failed pre-condition");
        while (i < n) {
            i = i + 3;
            j = j + 3;
            k = k + 3;
        }
        if (n > 0 && n <= 20000001) {
            assert(i % 20000003 != 0);
        }
    }

    function unknown() internal view returns (bool) {
        uint rand = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}