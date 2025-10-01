// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int n, int sum, int i) {
        require(n >= 1, "failed pre-condition");
        require(n <= 1000, "failed pre-condition");
        sum = 0;
        i = 0;
        while (i < n) {
            sum = sum + i;
            i = i + 1;
        }
        assert(2 * sum == n * (n - 1));
    }
}