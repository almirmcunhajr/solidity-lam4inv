// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LoopExample {
    constructor(int a, int b, int res, int cnt) {
        res = a;
        cnt = b;
        require(a <= 1000000, "failed pre-condition");
        require(b >= 0, "failed pre-condition");
        require(b <= 1000000, "failed pre-condition");
        while (cnt > 0) {
            cnt = cnt - 1;
            res = res + 1;
        }
        assert(res == a + b);
    }
}