from collections import UserDict
from typing import List, Optional
from datetime import datetime, timedelta


class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value: str):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Телефон повинен містити 10 цифр")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value: str):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(birthday_date)
        except ValueError:
            raise ValueError(
                "Неправильний формат дати. Використовуйте DD.MM.YYYY"
            )


class Record:
    def __init__(self, name: str):
        self.name: Name = Name(name)
        self.phones: List[Phone] = []
        self.birthday: Optional[Birthday] = None

    def add_phone(self, phone: str) -> None:
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        self.phones = [
            p for p in self.phones if p.value != phone
        ]

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Телефон не знайдено")

    def find_phone(self, phone: str) -> Optional[Phone]:
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday_str: str) -> None:
        self.birthday = Birthday(birthday_str)

    def show_birthday(self) -> str:
        if self.birthday:
            return self.birthday.value.strftime("%d.%m.%Y")
        return "День народження не вказано"

    def __str__(self) -> str:
        phones_str = "; ".join(p.value for p in self.phones)
        birthday_str = (
            self.show_birthday() if self.birthday else "не вказано"
        )
        return (
            f"Contact name: {self.name.value}, "
            f"phones: {phones_str}, "
            f"birthday: {birthday_str}"
        )


class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Контакт не знайдено")

    def get_upcoming_birthdays(self) -> List[str]:
        upcoming = []
        today = datetime.now().date()
        week_later = today + timedelta(days=7)

        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.value

                try:
                    this_year_bday = bday.replace(year=today.year)
                except ValueError:
                    this_year_bday = bday.replace(
                        year=today.year,
                        day=28
                    )

                birthday_date = this_year_bday.date()

                if today <= birthday_date <= week_later:
                    upcoming.append(record.name.value)

        return upcoming


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, IndexError, KeyError) as error:
            return f"Помилка: {error}"

    return wrapper


@input_error
def add_contact(args: List[str], book: AddressBook) -> str:
    name, phone, *_ = args
    record = book.find(name)

    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone:
        record.add_phone(phone)

    return message


@input_error
def change_phone(args: List[str], book: AddressBook) -> str:
    name, old_phone, new_phone, *_ = args
    record = book.find(name)

    if record is None:
        raise KeyError("Контакт не знайдено")

    record.edit_phone(old_phone, new_phone)
    return "Phone updated."


@input_error
def show_phone(args: List[str], book: AddressBook) -> str:
    name, *_ = args
    record = book.find(name)

    if record is None:
        raise KeyError("Контакт не знайдено")

    return "; ".join(p.value for p in record.phones)


@input_error
def show_all(book: AddressBook) -> str:
    if not book.data:
        return "Адресна книга порожня."

    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args: List[str], book: AddressBook) -> str:
    name, birthday_str, *_ = args
    record = book.find(name)

    if record is None:
        raise KeyError("Контакт не знайдено")

    record.add_birthday(birthday_str)
    return "Birthday added."


@input_error
def show_birthday(args: List[str], book: AddressBook) -> str:
    name, *_ = args
    record = book.find(name)

    if record is None:
        raise KeyError("Контакт не знайдено")

    return record.show_birthday()


@input_error
def birthdays(args: List[str], book: AddressBook) -> str:
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return (
            "Ніхто не святкує день народження наступного тижня."
        )

    return "Вітаємо: " + ", ".join(upcoming)


def parse_input(user_input: str) -> List[str]:
    return user_input.strip().split()


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")

        if not user_input.strip():
            continue

        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        if command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_phone(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
