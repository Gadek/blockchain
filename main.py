
from uuid import uuid4
from time import time
import threading

from flask import Flask, jsonify, request
from blockchain import Blockchain
from flask import request
import requests
import pickle
# Instantiate the Node
app = Flask(__name__)




@app.route('/mine', methods=['GET'])
def mine():

    block = {
        'index': len(blockchain.chain) + 1,
        'timestamp': time(),
        'transactions': blockchain.current_transactions,
        'proof': 0,
        'previous_hash': blockchain.last_block['hash'],
        'hash': "0"
    }

    block['hash'] = blockchain.proof_of_work(block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    # blockchain.new_transaction(
    #     sender="0",
    #     recipient=node_identifier,
    #     amount=1,
    # )
    voters_agree = blockchain.vote(block)

    if voters_agree:
        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
            'hash': block['hash']
        }
    else:
        response = {
            'message': "Did not forge new block",
        }
    return jsonify(response), 200



@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    # if not all(k in values for k in required):
    #    return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/verify', methods=['POST'])
def verify():
    value = request.get_data()
    block = pickle.loads(value)

    print(block)
    is_valid = blockchain.valid_block(block)
    if is_valid:
        response = {'message': f'Block is valid'}
        blockchain.current_transactions = []
        blockchain.chain.append(block)
        return jsonify(response), 201
    if not is_valid:
        response = {'message': f'Block not is valid'}
        return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    from argparse import ArgumentParser


    # Generate a globally unique address for this node
    node_identifier = str(uuid4()).replace('-', '')

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-r', '--register', default="127.0.0.1", type=str, help='ip address of node of existing blockchain')
    args = parser.parse_args()
    port = args.port
    register = args.register
    print("heeej", register)
    # Instantiate the Blockchain
    blockchain = Blockchain(register)

    app.run(host='192.168.56.7', port=port)