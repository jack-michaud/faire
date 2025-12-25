class Check:
    _passed: bool
    _value: bool

    def __init__(self, default: bool, passed: bool) -> None:
        self._passed = passed
        self._value = default

    def mark(self, value: bool) -> None:
        self._value = value

    def did_pass(self) -> bool:
        return self._value == self._passed


class EvalResult:
    # Used the writing-services skill
    used_service_skill = Check(default=False, passed=True)

    # Used |None instead of Optional
    used_none_instead_of_optional = Check(default=False, passed=True)

    def to_dict(self) -> dict:
        """Convert eval results to a dictionary for logging."""
        return {
            "used_service_skill": self.used_service_skill.did_pass(),
            "used_none_instead_of_optional": self.used_none_instead_of_optional.did_pass(),
        }
