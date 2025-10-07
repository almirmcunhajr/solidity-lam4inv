// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int idBitLength, int materialLength, int nlen, int j, int k) {
        require(nlen == idBitLength / 32, "failed pre-condition");
        require(idBitLength >= 0, "failed pre-condition");
        require(materialLength >= 0, "failed pre-condition");
        j = 0;
        while ((j < idBitLength / 8) && (j < materialLength)) {
            j = j + 1;
        }
        assert(0 <= j);
    }

    function unknown() internal view returns (bool) {
        bytes32 rand = keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number));
        return uint256(rand) % 2 == 0;
    }
}
