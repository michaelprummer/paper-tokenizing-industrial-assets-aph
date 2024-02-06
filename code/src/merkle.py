from pymerkle import BaseMerkleTree, verify_inclusion
import hashlib


def sha256(data):
    return hashlib.sha256(data).digest()


class pMerkleTree(BaseMerkleTree):

    def __init__(self, algorithm='sha256'):
        """
        Storage setup and superclass initialization
        """
        self.hashes = []

        super().__init__(algorithm)

    def _encode_entry(self, data):
        """
        Prepares data entry for hashing
        """
        return data

    def _store_leaf(self, data, digest):
        """
        Stores data hash in a new leaf and returns index
        """
        self.hashes += [digest]

        return len(self.hashes)

    def _get_leaf(self, index):
        """
        Returns the hash stored by the leaf specified
        """
        value = self.hashes[index - 1]

        return value

    def _get_leaves(self, offset, width):
        """
        Returns hashes corresponding to the specified leaf range
        """
        values = self.hashes[offset: offset + width]

        return values

    def _get_size(self):
        """
        Returns the current number of leaves
        """
        return len(self.hashes)

    def m_get_root(self) -> str:
        return self.get_state().hex()

    def m_proof(self, leaf_index: int, size=None) -> bool:
        if size == None:
            size = self.get_size()

        proof = self.prove_inclusion(leaf_index)
        root = self.get_state()
        leaf = self.get_leaf(leaf_index)

        try:
            verify_inclusion(leaf, root, proof)
        except:
            return False

        return True
