# Tokenizing Industrial Assets: Multi-File Binding using an Average Perceptual Hash

# Abstract

The increasing digitalization in manufacturing and trends like the Industrial Metaverse drive the need for secure decentralized asset exchanges and industrial asset intellectual property (IP) rights protection. Utilizing distributed ledgers and non-fungible tokens (NFTs) linked by a hash enables the management and authentication of assets. However, challenges arise in authenticating the same asset's different versions and file formats using a single hash.
In this work, we propose a new NFT structure that allows binding multiple files existing in different file formats, representing the same digital asset by combining a Merkle Tree (MT) with a calculated average perceptual hash (APH). While the MT proves bitwise integrity, the APH verifies functional integrity for asset authentication. We evaluate our approach for exchanging Printed Circuit Board (PCB) designs in a decentralized ecosystem by calculating unique PCB fingerprints and the APH. Our results show a robust identification and integrity verification of PCB designs depending on the manipulation type. Our approach for asset authentication is generalizable to all asset classes with an appropriate perceptual hash.

# Content

- /reports: Calculated reports
- /src: Code
- /assets: Gerber files and converted images

Credits:
Dataset is based on the PCB designs from:
https://github.com/DangerousPrototypes/dangerous-prototypes-open-hardware
