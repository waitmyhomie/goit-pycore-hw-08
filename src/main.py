import pickle
from collections import UserDict
from datetime import datetime, timedelta

def input_error(handler):
    def wrapper(*args, **kwargs):
        try:
            return handler(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return str(e)
    return wrapper

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if self.validate_phone(value):
            super().__init__(value)
        else:
            raise ValueError("Phone number must be exactly 10 digits.")

    @staticmethod
    def validate_phone(value):
        return value.isdigit() and len(value) == 10

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        try:
            self.phones.append(Phone(phone))
        except ValueError as e:
            print(e)

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        print("Phone not found.")
        return False

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                try:
                    self.phones[i] = Phone(new_phone)
                    return True
                except ValueError as e:
                    print(e)
                    return False
        print("Old phone not found.")
        return False

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        try:
            self.birthday = Birthday(birthday)
        except ValueError as e:
            print(e)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        print("Record not found.")
        return False

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = datetime.now()
        next_week = today + timedelta(days=days)
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)
                if today <= birthday_this_year <= next_week:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Not enough arguments. Usage: add [name] [phone]")
    name, phone, *rest = args
    birthday = rest[0] if rest else None

    if birthday:
        try:
            Birthday(birthday)
        except ValueError as e:
            return f'Failed to add contact. {e}'
    
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
        
    if birthday:
        try:
            record.add_birthday(birthday)
        except ValueError as e:
            return f'Failed to add contact. {e}'
    if phone:
        record.add_phone(phone)

    return message

@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    record.add_birthday(birthday)
    return f"Birthday added for contact {name}."

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return f"Contact {name} not found."
    if record.birthday:
        return f"{name}'s birthday is on {record.birthday.value.strftime('%d.%m.%Y')}"
    else:
        return f"Birthday for contact {name} is not set."

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays in the next week."
    result = "Upcoming birthdays:\n"
    for record in upcoming_birthdays:
        result += f"{record.name.value} on {record.birthday.value.strftime('%d.%m.%Y')}\n"
    return result

def parse_input(user_input):
    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Return a new address book if the file is not found

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)  # Save data before exiting
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            if len(args) < 3:
                print("Not enough arguments. Usage: change [name] [old_phone] [new_phone]")
                continue
            name, old_phone, new_phone = args
            record = book.find(name)
            if record:
                if record.edit_phone(old_phone, new_phone):
                    print(f"Phone number for {name} updated.")
                else:
                    print("Failed to update phone number.")
            else:
                print(f"Contact {name} not found.")
        elif command == "phone":
            if not args:
                print("Not enough arguments. Usage: phone [name]")
                continue
            name, *_ = args
            record = book.find(name)
            if record:
                print(f"{name}'s phone numbers: {', '.join(phone.value for phone in record.phones)}")
            else:
                print(f"Contact {name} not found.")

        elif command == "all":
            for name, record in book.data.items():
                print(record)

        elif command == "add-birthday":
            if len(args) < 2:
                print("Not enough arguments. Usage: add-birthday [name] [birthday]")
                continue
            print(add_birthday(args, book))

        elif command == "show-birthday":
            if not args:
                print("Not enough arguments. Usage: show-birthday [name]")
                continue
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
