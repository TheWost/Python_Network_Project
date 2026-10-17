"""Used for test subject in sending files"""

from utils import clear


class Calculator:
    def __init__(self) -> None:
        self.allowed_operations = ["+", "-", "*", "/", "^", "root"]

    def _ask_for_number(self, number_index: int = 0) -> float:
        while True:
            try:
                return float(
                    input(f"Enter number {number_index if number_index else ''}> ")
                )
            except ValueError:
                print("Must be a int")

    def get_numbers(self) -> tuple:
        number1 = self._ask_for_number(number_index=1)
        number2 = self._ask_for_number(number_index=2)

        return number1, number2

    def get_operation(self) -> str:
        while True:
            op = input(
                f"Enter operation ({', '.join(self.allowed_operations)})> "
            ).strip()
            if op in self.allowed_operations:
                return op
            print(
                f"Invalid operation. Choose from: {', '.join(self.allowed_operations)}"
            )

    def start_calculator(self) -> None:
        while True:
            clear()
            print("=== Calculator ===")
            num1, num2 = self.get_numbers()
            op = self.get_operation()

            match op:
                case "+":
                    result = num1 + num2
                case "-":
                    result = num1 - num2
                case "*":
                    result = num1 * num2
                case "/":
                    result = num1 / num2 if num2 != 0 else "Error (Division by zero)"
                case "^":
                    result = num1**num2
                case "root":
                    result = (
                        num1 ** (1 / num2) if num2 != 0 else "Error (Zero root index)"
                    )
                case _:
                    result = "Error"

            print(f"\nResult: {num1} {op} {num2} = {result}")

            choice = (
                input("\nDo you want to do another calculation? (y/n): ")
                .strip()
                .lower()
            )
            if choice != "y":
                print("Goodbye!")
                break
