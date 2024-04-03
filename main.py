from abc import ABC, abstractmethod
import pickle
from datetime import datetime
from collections import UserDict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name: str):
        super().__init__(name)      

class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str) or len(value) != 10 or not value.isdigit():
            raise ValueError("Phone number must be a 10-digit string")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            # Перевірка формату дати та перетворення рядка на об'єкт datetime
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self,phone):
        self.phones.append(Phone(phone))
       
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]
    
    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return

    def find_phone(self, phone):
        for p in self.phones:
             if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        # Перевірка на наявність дня народження
        if self.birthday:
            raise ValueError("Birthday already set.")
        # Збереження дня народження
        self.birthday = birthday

    def show_birthday(self):
        # Перевірка на наявність дня народження
        if not self.birthday:
            raise ValueError("No birthday set.")
        # Виведення дня народження
        return self.birthday.value.strftime("%d.%m.%Y")

class AddressBook(UserDict):
    def add_contact(self, args):
        name, phone = args
        if name not in self.data:
            self.data[name] = Record(name)
        self.data[name].add_phone(phone)

    def change_contact(self, args):
        name, new_phone = args
        record = self.data.get(name)
        if record:
            old_phone = record.phones[0].value
            record.remove_phone(old_phone)
            record.add_phone(new_phone)
            return "Phone number updated."
        return "Contact not found."
    
    def show_phone(self, args):
        name = args[0]
        record = self.data.get(name)
        if record:
            return record.phones[0].value
        return "Contact not found."

    def add_birthday(self, name, birthday):
        record = self.data.get(name)
        if record:
            record.add_birthday(birthday)
            return "Birthday added."
        else:
            return "Contact not found."

    def show_birthday(self, name):
        record = self.data.get(name)
        if record and record.birthday:
            return record.show_birthday()
        else:
            raise ValueError("Contact not found or no birthday set.")

    def birthdays(self):
        # Змінна для зберігання списку контактів, яких потрібно привітати
        upcoming_birthdays = []
        # Отримання поточної дати
        today = datetime.combine(datetime.today(), datetime.min.time())
        # Цикл для перевірки днів народження у всіх контактів
        for record in self.values():
            # Перевірка на наявність дня народження
            if record.birthday:
                # Якщо день народження протягом наступного тижня, додати контакт у список
                if (record.birthday.value - today).days <= 7:
                    upcoming_birthdays.append(record.name.value)
        # Повернення списку контактів
        return upcoming_birthdays
    
    def show_all(self):
        all_contacts = []
        for record in self.values():
            contact_info = f"Name: {record.name.value}"
            if record.phones:
                phone_info = ", ".join([phone.value for phone in record.phones])
                contact_info += f", Phones: {phone_info}"
            if record.birthday:
                birthday_info = record.birthday.value.strftime("%d.%m.%Y")
                contact_info += f", Birthday: {birthday_info}"
            all_contacts.append(contact_info)
        return "\n".join(all_contacts)
    
class ConsoleOutputBot(ABC):
    @abstractmethod
    def output(self, message):
        pass

    @abstractmethod
    def return_help(self, book):
        pass

class SimpleBot(ConsoleOutputBot):
    def output(self, message):
        print(message)

    def return_help(self, book):
        return "Commands:\n" \
               "add [name] [phone] - Add a new contact\n" \
               "change [name] [new_phone] - Change phone number\n" \
               "phone [name] - Show phone number\n" \
               "all - Show all contacts\n" \
               "add-birthday [name] [birthday] - Add birthday\n" \
               "show-birthday [name] - Show birthday\n" \
               "birthdays - Show upcoming birthdays"
    
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()
    bot = SimpleBot()


    bot.output("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            bot.output("Good bye!")
            save_data(book)  # Збереження даних перед виходом
            break

        elif command == "hello":
            bot.output("How can I help you?")

        elif command == "add":
            book.add_contact(args)
            bot.output("Contact added.")

        elif command == "change":
            bot.output(book.change_contact(args))

        elif command == "phone":
            bot.output(book.show_phone(args))

        elif command == "all":
            bot.output(book.show_all())

        elif command == "add-birthday":
            name, birthday = args
            bot.output(book.add_birthday(name, Birthday(birthday)))
            
        elif command == "show-birthday":
            name = args[0]
            bot.output(book.show_birthday(name))

        elif command == "birthdays":
            bot.output(book.birthdays())

        else:
            bot.output("Invalid command.")

if __name__ == "__main__":
    main()