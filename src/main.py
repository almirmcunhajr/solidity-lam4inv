from vc.generator import Generator

if __name__ == '__main__':
    solidity_code = """
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
    """
    file_name = "SimpleLoop.sol"
    with open(file_name, "w") as f:
        f.write(solidity_code)

    generator = Generator(file_name)
    pre_vc, trans_vc, post_vc = generator.generate('SimpleLoop', 'loop(uint256)', 0, 'test')
    print(trans_vc)
 
