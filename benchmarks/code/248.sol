// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int idBitLength, int material_length, int nlen, int j, int k) {
        require(nlen == idBitLength / 32, "failed pre-condition");
        require(idBitLength >= 0, "failed pre-condition");
        require(material_length >= 0, "failed pre-condition");
        j = 0;
        while ((j < idBitLength / 8) && (j < material_length)) {
            j = j + 1;
        }
        assert((j / 4) <= nlen);
    }
}