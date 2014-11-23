# -*- coding: utf-8 -*-
"""
    Coinkit
    ~~~~~

    :copyright: (c) 2014 by Halfmoon Labs
    :license: MIT, see LICENSE for more details.
"""

from binascii import hexlify, unhexlify
from pybitcointools import sign as sign_transaction

from ..services import blockchain_info, chain_com, bitcoind
from ..privatekey import BitcoinPrivateKey
from .serialize import serialize_transaction
from .outputs import make_pay_to_address_outputs, make_op_return_outputs
from ..constants import STANDARD_FEE, OP_RETURN_FEE

""" Note: for functions that take in an auth object, here are some examples
    for the various APIs available:
    
    blockchain.info: auth=(api_key, None)
    chain.com: auth=(api_key_id, api_key_secret)
"""

from ..services import BlockchainInfoClient, BitcoindClient, ChainComClient

def get_unspents(address, blockchain_client=BlockchainInfoClient()):
    """ Gets the unspent outputs for a given address.
    """
    if isinstance(blockchain_client, BlockchainInfoClient):
        return blockchain_info.get_unspents(address, blockchain_client)
    elif isinstance(blockchain_client, ChainComClient):
        return chain_com.get_unspents(address, blockchain_client)
    elif isinstance(blockchain_client, BitcoindClient):
        return bitcoind.get_unspents(address, blockchain_client)
    elif isinstance(blockchain_client, BlockchainClient):
        raise Exception('That blockchain interface is not supported.')
    else:
        raise Exception('A BlockchainClient object is required')

def broadcast_transaction(hex_transaction, blockchain_client):
    """ Dispatches a raw hex transaction to the network.
    """
    if isinstance(blockchain_client, BlockchainInfoClient):
        return blockchain_info.broadcast_transaction(hex_transaction, blockchain_client)
    elif isinstance(blockchain_client, ChainComClient):
        return chain_com.broadcast_transaction(hex_transaction, blockchain_client)
    elif isinstance(blockchain_client, BitcoindClient):
        return bitcoind.broadcast_transaction(hex_transaction, blockchain_client)
    elif isinstance(blockchain_client, BlockchainClient):
        raise Exception('That blockchain interface is not supported.')
    else:
        raise Exception('A BlockchainClient object is required')

def make_send_to_address_tx(recipient_address, amount, sender_private_key,
        blockchain_client=BlockchainInfoClient(), fee=STANDARD_FEE,
        change_address=None):
    """ Builds and signs a "send to address" transaction.
    """
    if not isinstance(sender_private_key, BitcoinPrivateKey):
        sender_private_key = BitcoinPrivateKey(sender_private_key)
    # determine the address associated with the supplied private key
    from_address = sender_private_key.public_key().address()
    # get the unspent outputs corresponding to the given address
    inputs = get_unspents(from_address, blockchain_client)
    # get the change address
    if not change_address:
        change_address = from_address
    # create the outputs
    outputs = make_pay_to_address_outputs(recipient_address, amount, inputs,
                                          change_address, fee=fee)
    # serialize the transaction
    unsigned_tx = serialize_transaction(inputs, outputs)
    # sign the unsigned transaction with the private key
    signed_tx = sign_transaction(unsigned_tx, 0, sender_private_key.to_hex())
    # return the signed tx
    return signed_tx

def make_op_return_tx(data, sender_private_key,
        blockchain_client=BlockchainInfoClient(), fee=OP_RETURN_FEE,
        change_address=None, format='bin'):
    """ Builds and signs an OP_RETURN transaction.
    """
    if not isinstance(sender_private_key, BitcoinPrivateKey):
        sender_private_key = BitcoinPrivateKey(sender_private_key)
    # determine the address associated with the supplied private key
    from_address = sender_private_key.public_key().address()
    # get the unspent outputs corresponding to the given address
    inputs = get_unspents(from_address, blockchain_client)
    # get the change address
    if not change_address:
        change_address = from_address
    # create the outputs
    outputs = make_op_return_outputs(data, inputs, change_address,
        fee=fee, format=format)
    # serialize the transaction
    unsigned_tx = serialize_transaction(inputs, outputs)
    # sign the unsigned transaction with the private key
    signed_tx = sign_transaction(unsigned_tx, 0, sender_private_key.to_hex())
    # return the signed tx
    return signed_tx

def send_to_address(recipient_address, amount, sender_private_key,
        blockchain_client=BlockchainInfoClient(), fee=STANDARD_FEE,
        change_address=None):
    """ Builds, signs, and dispatches a "send to address" transaction.
    """
    # build and sign the tx
    signed_tx = make_send_to_address_tx(recipient_address, amount,
        sender_private_key, blockchain_client, fee=fee,
        change_address=change_address)
    # dispatch the signed transction to the network
    response = broadcast_transaction(signed_tx, blockchain_client)
    # return the response
    return response

def embed_data_in_blockchain(data, sender_private_key,
        blockchain_client=BlockchainInfoClient(), fee=OP_RETURN_FEE,
        change_address=None, format='bin'):
    """ Builds, signs, and dispatches an OP_RETURN transaction.
    """
    # build and sign the tx
    signed_tx = make_op_return_tx(data, sender_private_key, blockchain_client,
        fee=fee, change_address=change_address, format=format)
    # dispatch the signed transction to the network
    response = broadcast_transaction(signed_tx, blockchain_client)
    # return the response
    return response


