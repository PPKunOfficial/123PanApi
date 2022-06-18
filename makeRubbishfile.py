import string
import random

number_of_strings = 1
length_of_string = 1000
for x in range(number_of_strings):
    with open("rubbish.file", "w") as f:
        f.write(''.join(random.SystemRandom().choice(
            string.ascii_letters + string.digits) for _ in range(length_of_string)))
