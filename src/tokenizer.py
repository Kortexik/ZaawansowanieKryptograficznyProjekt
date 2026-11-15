"""Character encoding shared by data preparation and Kacper's future LSTM."""

import json
from pathlib import Path


class CharacterTokenizer:
    pad_id = 0
    bos_id = 1
    eos_id = 2
    tokens = ["<PAD>", "<BOS>", "<EOS>"] + [chr(i) for i in range(32, 127)]

    def __init__(self):
        self.char_to_id = {char: i for i, char in enumerate(self.tokens[3:], start=3)}

    @property
    def vocab_size(self):
        return len(self.tokens)

    def encode(self, password, pad_to=None):
        try:
            result = [self.bos_id] + [self.char_to_id[char] for char in password] + [self.eos_id]
        except KeyError as error:
            raise ValueError("Hasło zawiera znak spoza drukowalnego ASCII.") from error
        if pad_to is not None:
            if pad_to < len(result):
                raise ValueError("pad_to jest krótsze od hasła ze znacznikami BOS i EOS.")
            result += [self.pad_id] * (pad_to - len(result))
        return result

    def decode(self, token_ids):
        result = []
        for token_id in token_ids:
            if not isinstance(token_id, int) or not 0 <= token_id < self.vocab_size:
                raise ValueError(f"Nieprawidłowy identyfikator tokenu: {token_id!r}")
            if token_id == self.eos_id:
                break
            if token_id not in (self.pad_id, self.bos_id):
                result.append(self.tokens[token_id])
        return "".join(result)

    def save(self, path):
        Path(path).write_text(
            json.dumps({"version": 1, "tokens": self.tokens}, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data != {"version": 1, "tokens": cls.tokens}:
            raise ValueError("Niezgodny format lub alfabet tokenizera.")
        return cls()
