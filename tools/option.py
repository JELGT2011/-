from enum import Enum


class Base(Enum):

    @classmethod
    def to_input(cls):
        return {c.value: c.name for c in cls.__iter__()}

    @classmethod
    def from_input(cls, s):
        return cls(str(s))


class DynamicOption(Base):
    BET = '1'
    CHECK = '2'
    RAISE = '3'
    FOLD = '4'


class FixedOption(Base):
    YES = '1'
    NO = '2'
