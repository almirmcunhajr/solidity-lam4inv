
    pragma solidity ^0.8.0;
    contract SimpleLoop {
        uint public a;
        uint public b;
        function loop(uint x) public {
            a = 0;
            b = 10;
            for (uint i = 0; i < x; i++) {
                a = a + 1;
                b = b - 1;
            }
            assert(a == x);
        }
    }
    