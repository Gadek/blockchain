import hashlib
import json
from time import time
from urllib.parse import urlparse

import requests


class Blockchain:
    def __init__(self,register_ip):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        if register_ip == "127.0.0.1":
            # Create the genesis block
            self.genesis_block(previous_hash='1', proof=100)
        else:
            self.register_node(register_ip)
            self.resolve_conflicts()


    def register_node(self, address):
        """
        Add a new node to the list of nodes
        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_block(self, block):
        # Check that the hash of the block is correct
        if block['previous_hash'] != self.hash(self.last_block):
            print("block['previous_hash'] != self.hash(self.chain[-1])")
            return False

        # Check that the Proof of Work is correct
        if not self.valid_proof(block):
            print("self.valid_proof(block)")
            return False
        return True
    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            # block_values = [block["index"], block["timestamp"], block["transactions"], block["proof"], block["previous_hash"]]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                print("block['previous_hash'] != self.hash(last_block)")
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(block):
                print("self.valid_proof(block)")
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None
        print("sasiedzi", neighbours)

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                print("length > max_length", length > max_length)
                print("self.valid_chain(chain)", self.valid_chain(chain))

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def genesis_block(self, proof, previous_hash, hash="0"):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': "",
            'proof': 0,
            'previous_hash': "0",
            'hash': "0"
        }
        block['hash'] = self.proof_of_work(block)
        self.chain.append(block)
        # block = {
        #     'index': len(self.chain) + 1,
        #     'timestamp': time(),
        #     'transactions': self.current_transactions,
        #     'proof': proof,
        #     'previous_hash': previous_hash or self.hash(self.chain[-1]),
        #     'hash': "0"
        # }
        # block['hash'] = self.hash(block)

        # Reset the current list of transactions
        # self.current_transactions = []
        #
        # self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'amount': amount,
            'recipient': recipient,
            'sender': sender,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :pa ram block: Block
        """
        block_values = [block['index'], block['timestamp'], block['transactions'], block['proof'], block['previous_hash']]
        encoded_block_values = f'{block_values}'.encode()
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        # block_string = json.json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block_values).hexdigest()

    def proof_of_work(self, block):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof
        """

        block["proof"] = 0

        while self.valid_proof(block) is False:
            block["proof"] += 1

        return self.valid_proof(block)

    @staticmethod
    def valid_proof(block):
        """
        Validates the Proof
        :param last_proof: Previous Proof
        :param proof: Current Proof
        :return: True if correct, False if not.
        """

        block_values = [block["index"], block["timestamp"], block["transactions"], block["proof"], block["previous_hash"]]

        guess = f'{block_values}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        print(guess_hash)
        if guess_hash[:3] == "000":
            return guess_hash
        else:
            return False
