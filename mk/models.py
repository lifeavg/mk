# pyright: reportUnnecessaryIsInstance=false
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class BaseModel:

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LogNormal(BaseModel):
    median: int
    sigma: float
    type: str = 'lognormal'

    def __post_init__(self) -> None:
        # if not isinstance(self.median, int):
        #     raise TypeError("Median should be int type")
        # if not isinstance(self.sigma, float):
        #     raise TypeError("Sigma should be float type")
        if self.median < 0 or self.sigma < 0:
            raise ValueError(
                "Median and sigma values should be equal or grater than 0")
        if self.type != 'lognormal':
            raise ValueError("Don't change type attribute value")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Uniform(BaseModel):
    lower: int
    upper: int
    type: str = 'uniform'

    def __post_init__(self) -> None:
        if not isinstance(self.lower, int) or not isinstance(self.upper, int):
            raise TypeError("Lower and upper attributes should be int type")
        if self.lower < 0 or self.upper < 0:
            raise ValueError(
                "Lower and upper values should be equal or grater than 0")
        if self.lower > self.upper:
            raise ValueError("Lower value should be less than upper")
        if self.type != 'uniform':
            raise ValueError("Don't change type attribute value")


@dataclass
class FixedDelay(BaseModel):
    fixedDelay: int

    def __post_init__(self) -> None:
        if not isinstance(self.fixedDelay, int):
            raise TypeError("FixedDelay attribute should be int type")
        if self.fixedDelay < 0:
            raise ValueError(
                "FixedDelay value should be equal or grater than 0")
