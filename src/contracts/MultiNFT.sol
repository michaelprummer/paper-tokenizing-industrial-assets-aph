// SPDX-License-Identifier: UNLICENSED
pragma solidity >=0.8.18;
import { ERC721 } from "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract MultiNFT is ERC721 {
  string public files_merkle_root;
  string public average_perceptual_hash;
  string public metadata_hash;
  

  constructor(
    string memory _files_merkle_root,
    string memory _average_perceptual_hash,
    string memory _metadata_hash
    ) ERC721("MultiFileBinding", "MFB") {
    files_merkle_root = _files_merkle_root;
    average_perceptual_hash = _average_perceptual_hash;
    metadata_hash = _metadata_hash;
  }
  
  function mint(uint256 amount_) public {
    _mint(msg.sender, amount_);
  }

}
