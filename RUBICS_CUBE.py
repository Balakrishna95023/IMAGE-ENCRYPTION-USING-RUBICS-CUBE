from PIL import Image
from random import randint
import numpy as np
import json
import base64

class RubikCubeCrypto:

    def __init__(self, image: Image) -> None:
        self.image = image.convert('RGB')
        self.rgb_array = np.array(self.image)
        self.new_rgb_array = np.copy(self.rgb_array)
        self.m, self.n = self.rgb_array.shape[0], self.rgb_array.shape[1]

    def create_key(self, alpha: float, itermax: int, key_filename: str = 'key.txt') -> None:
        self.Kr = [randint(0, pow(2, alpha) - 1) for _ in range(self.m)]
        self.Kc = [randint(0, pow(2, alpha) - 1) for _ in range(self.n)]
        self.itermax = itermax

        key_dict = {
            "Kr": self.Kr,
            "Kc": self.Kc,
            "itermax": itermax
        }

        serialized_key_dict = json.dumps(key_dict)
        encoded_key = base64.b64encode(serialized_key_dict.encode())
        with open(key_filename, "wb") as binary_file:
            binary_file.write(encoded_key)

    def load_key(self, key_filename: str) -> None:
        with open(key_filename, 'r') as key_file:
            data = key_file.read()
        decoded_key = base64.b64decode(data).decode()
        decoded_dict = json.loads(decoded_key)
        self.Kr = decoded_dict["Kr"]
        self.Kc = decoded_dict["Kc"]
        self.itermax = decoded_dict["itermax"]

    def roll_row(self, encrypt_flag: bool = True) -> None:
      direction_multiplier = 1 if encrypt_flag else -1

      for i in range(self.m):
          rModulus = np.sum(self.new_rgb_array[i, :, 0]) % 2
          gModulus = np.sum(self.new_rgb_array[i, :, 1]) % 2
          bModulus = np.sum(self.new_rgb_array[i, :, 2]) % 2

          # Roll rows based on modulus and direction_multiplier * Kc[i]
          self.new_rgb_array[i, :, 0] = np.roll(self.new_rgb_array[i, :, 0],
                                                 direction_multiplier * -self.Kc[i]) if (rModulus == 0) \
              else np.roll(self.new_rgb_array[i, :, 0], direction_multiplier * self.Kc[i])

          self.new_rgb_array[i, :, 1] = np.roll(self.new_rgb_array[i, :, 1],
                                                 direction_multiplier * -self.Kc[i]) if (gModulus == 0) \
              else np.roll(self.new_rgb_array[i, :, 1], direction_multiplier * self.Kc[i])

          self.new_rgb_array[i, :, 2] = np.roll(self.new_rgb_array[i, :, 2],
                                                 direction_multiplier * -self.Kc[i]) if (bModulus == 0) \
              else np.roll(self.new_rgb_array[i, :, 2], direction_multiplier * self.Kc[i])


    def roll_column(self, encrypt_flag: bool = True) -> None:
        direction_multiplier = 1 if encrypt_flag else -1

        for i in range(self.n):
            rModulus = np.sum(self.new_rgb_array[:, i, 0]) % 2
            gModulus = np.sum(self.new_rgb_array[:, i, 1]) % 2
            bModulus = np.sum(self.new_rgb_array[:, i, 2]) % 2

            self.new_rgb_array[:, i, 0] = np.roll(self.new_rgb_array[:, i, 0],
                                                   direction_multiplier * -self.Kc[i]) if (rModulus == 0) \
                else np.roll(self.new_rgb_array[:, i, 0], direction_multiplier * self.Kc[i])

            self.new_rgb_array[:, i, 1] = np.roll(self.new_rgb_array[:, i, 1],
                                                   direction_multiplier * -self.Kc[i]) if (gModulus == 0) \
                else np.roll(self.new_rgb_array[:, i, 1], direction_multiplier * self.Kc[i])

            self.new_rgb_array[:, i, 2] = np.roll(self.new_rgb_array[:, i, 2],
                                                   direction_multiplier * -self.Kc[i]) if (bModulus == 0) \
                else np.roll(self.new_rgb_array[:, i, 2], direction_multiplier * self.Kc[i])

    def xor_pixels(self) -> None:
        for i in range(self.m):
            for j in range(self.n):
                xor_operand_1 = self.Kc[j] if i % 2 == 1 else self.rotate_180(self.Kc[j])
                xor_operand_2 = self.Kr[i] if j % 2 == 0 else self.rotate_180(self.Kr[i])
                self.new_rgb_array[i, j, 0] = self.new_rgb_array[i, j, 0] ^ xor_operand_1 ^ xor_operand_2
                self.new_rgb_array[i, j, 1] = self.new_rgb_array[i, j, 1] ^ xor_operand_1 ^ xor_operand_2
                self.new_rgb_array[i, j, 2] = self.new_rgb_array[i, j, 2] ^ xor_operand_1 ^ xor_operand_2

    def rotate_180(self, n: int) -> int:
        bits = "{0:b}".format(n)
        return int(bits[::-1], 2)

    def encrypt(self, alpha: int = 8, itermax: int = 10, key_filename: str = 'key.txt') -> Image:
        self.create_key(alpha, itermax, key_filename)
        for _ in range(itermax):
            self.roll_row(encrypt_flag=True)
            self.roll_column(encrypt_flag=True)
            self.xor_pixels()
        #WIDTH:321, HEIGHT:200
        new_image = Image.fromarray(self.new_rgb_array.astype(np.uint8))
        return new_image

    def decrypt(self, key_filename: str) -> Image:
        self.load_key(key_filename)
        for _ in range(self.itermax):
            self.xor_pixels()
            self.roll_column(encrypt_flag=False)
            self.roll_row(encrypt_flag=False)

        new_image = Image.fromarray(self.new_rgb_array.astype(np.uint8))
        return new_image
from PIL import Image

# Load an image
input_image = Image.open("Input.png")
original_size = (input_image.width, input_image.height)
input_image = input_image.resize((321, 200))
# Create an instance of RubikCubeCrypto
crypto = RubikCubeCrypto(input_image)

# Encrypt the image
encrypted_image = crypto.encrypt()

# Save or display the encrypted image
encrypted_image.save("encrypted_image.jpg")
encrypted_image.show()
# Decrypt the image
decrypted_image = crypto.decrypt("key.txt")
decrypted_image = decrypted_image.resize(original_size)
# Save or display the decrypted image
decrypted_image.save("decrypted_image.png")
decrypted_image.show()

