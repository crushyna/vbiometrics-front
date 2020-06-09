import hashlib
from helpers import AdditionalFunctions

BLOCK_SIZE_OF_SHA512 = 128


class HashFunctions:

    def __init__(self, block_size_of_sha512=BLOCK_SIZE_OF_SHA512):
        self.block_size_of_sha512 = block_size_of_sha512

    def hmac_sha512(self, key_K, data):
        if len(key_K) > self.block_size_of_sha512:
            raise ValueError('The key must be <= self.block_size_of_sha512 bytes in length')
        padded_K = key_K + b'\x00' * (self.block_size_of_sha512 - len(key_K))
        ipad = b'\x36' * self.block_size_of_sha512
        opad = b'\x5c' * self.block_size_of_sha512
        h_inner = hashlib.sha512(AdditionalFunctions.xor(padded_K, ipad))
        h_inner.update(data)
        h_outer = hashlib.sha512(AdditionalFunctions.xor(padded_K, opad))
        h_outer.update(h_inner.digest())
        return h_outer.digest()

    def calculate_hmac(self, key, message):
        # test 1
        k = bytes(key, 'utf-8')
        message = bytes(message, 'utf-8')
        result = self.hmac_sha512(k, message)
        return result.hex()
        # add tests as desired

    def calculate_md5(self, input):
        data = input.encode("utf-8")
        md5 = hashlib.md5(data)
        return md5.digest().hex()

    @staticmethod
    def calculate_sha512(input):
        data = input.encode("utf-8")
        sha512 = hashlib.sha512(data)
        return sha512.digest().hex()