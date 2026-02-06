from abc import ABC, abstractmethod
import typing
import pandas as pd

class AbstractStrategy(ABC):
    def __init__(self):
        self.params: typing.Dict[str, typing.Dict] = {}

    @abstractmethod
    def backtest(self, df: pd.DataFrame, **kwargs) -> typing.Tuple[float, float]:
        pass

    def get_params(self) -> typing.Dict[str, typing.Dict]:
        return self.params
        
    def validate_params(self, params: typing.Dict) -> typing.Dict:
        """Override this method to add custom constraint validation logic"""
        return params
