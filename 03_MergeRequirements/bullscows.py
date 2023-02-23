import random
import sys
import urllib.request
import cowsay

def print_random_cow_message(message: str) -> str:
    cow_name = random.choice(cowsay.list_cows())
    print(cowsay.cowsay(message, cow=cow_name))


def ask(prompt: str, valid: list[str] = None) -> str:
    print_random_cow_message(prompt)
    if valid == None:
        return input()
    else:
        while True:
            result = input()
            if result in valid:
                return result
            print('Слово не подходит')


def inform(format_string: str, bulls: int, cows: int) -> None:
    print_random_cow_message(format_string.format(bulls, cows))


def bullscows(guess: str, secret: str) -> (int, int):
    assert len(guess) == len(secret)
    bools = [(guess[i] == secret[i]) for i in range(len(guess))].count(True)
    cows = len(set(guess).intersection(set(secret)))
    return (bools, cows)


def gameplay(ask: callable, inform: callable, words: list[str]) -> int:
    secret_word = random.choice(words)
    tries = 0
    while True:
        guessed_word = ask("Введите слово: ", words)
        if len(guessed_word) != len(secret_word):
            print_random_cow_message('Неправильная длина слова,'
                                     'попробуйте еще раз')
            continue
        tries += 1
        bulls, cows = bullscows(guessed_word, secret_word)
        inform("Быки: {}, Коровы: {}", bulls, cows)
        if guessed_word == secret_word:
            print_random_cow_message(f'Заняло {tries} попыток')
            break


def get_dictionary(name_or_url: str) -> list[str]:
    try:
        with open(name_or_url, 'r') as file:
            dictionary = file.read().split()
            return dictionary
    except FileNotFoundError:
        try:
            response = urllib.request.urlopen(name_or_url)
            dictionary = response.read().decode().split()
            return dictionary
        except Exception as ex:
            raise Exception(f'Словарь не найден: {ex}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_random_cow_message('Не указан словарь')
        exit()
    try:
        dictionary = get_dictionary(sys.argv[1])
        if len(sys.argv) > 2:
            words_len = int(sys.argv[2])
        else:
            words_len = 5
        dictionary = [word for word in dictionary
                      if len(word) == words_len]
        gameplay(ask, inform, dictionary)
    except Exception as ex:
        print(ex)
