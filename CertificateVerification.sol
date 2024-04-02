pragma solidity >= 0.8.11 <= 0.8.11;

contract CertificateVerification {
    string public company_details;
    string public certificate_details;

    mapping(address => uint256) public balances;

    event Transfer(address indexed from, address indexed to, uint256 value);

    function setCompanyDetails(string memory cd) public {
        company_details = cd;    
    }

    function getCompanyDetails() public view returns (string memory) {
        return company_details;
    }

    function setCertificateDetails(string memory cd) public {
        certificate_details = cd;    
    }

    function getCertificateDetails() public view returns (string memory) {
        return certificate_details;
    }

    constructor() {
        company_details = "empty";
        certificate_details = "empty";
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function transfer(address to, uint256 value) public {
        require(balances[msg.sender] >= value, "Insufficient balance");
        balances[msg.sender] -= value;
        balances[to] += value;
        emit Transfer(msg.sender, to, value);
    }

    function getBalance(address account) public view returns (uint256) {
        return balances[account];
    }
}
