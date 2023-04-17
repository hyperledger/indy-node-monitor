import base58
import base64
import nacl.signing
from indy_vdr.ledger import Request

class DidKey:
    def __init__(self, seed):
        self.seed = seed 
        self.seed = self.seed_as_bytes()
        self.sk = nacl.signing.SigningKey(self.seed)
        self.vk = bytes(self.sk.verify_key)
        self.did = base58.b58encode(self.vk[:16]).decode("ascii")
        self.verkey = base58.b58encode(self.vk).decode("ascii")

    def sign_request(self, req: Request):
        signed = self.sk.sign(req.signature_input)
        req.set_signature(signed.signature)

    def seed_as_bytes(self):
        if not self.seed or isinstance(self.seed, bytes):
            return self.seed
        if len(self.seed) == 64:
            return bytes.fromhex(self.seed)
        if len(self.seed) != 32:
            return base64.b64decode(self.seed)
        return self.seed.encode("ascii")