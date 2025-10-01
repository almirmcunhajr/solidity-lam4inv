// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LoopExample {
    constructor(int lo, int mid, int hi) {
        require(mid > 0, "failed pre-condition");
        lo = 0;
        hi = 2 * mid;
        while (mid > 0) {
            lo = lo + 1;
            hi = hi - 1;
            mid = mid - 1;
        }
        assert(lo == hi);
    }

    function unknown() public view returns (bool) {
        uint256 rand = uint256(keccak256(abi.encodePacked(block.timestamp, block.prevrandao, block.number)));
        return rand % 2 == 0;
    }
}