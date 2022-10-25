"""Manifests that describe models available in a Garden"""
from typing import Optional, List, Dict
from enum import Enum

from pydantic import BaseModel, Field, FilePath


class ProviderChoices(str, Enum):
    """Types of execution provides that support a model step"""

    funcx = 'funcx'


class FlavorChoices(str, Enum):
    """Types of steps known to Garden"""

    python = 'python'
    tensorflow = 'tensorflow'


class Model(BaseModel):
    """Description of the entire process of running a model and where that model came from"""

    steps: List['Step'] = Field(default_factory=list, description='Sequential operations used to ')
    citation: Optional['DataCite'] = Field(None, description='Information needed to acknowledge the academic contributions behind a Model')


class DataCite(BaseModel):
    """Information describing how to reference the Model and resources related to it.

    Implements Version 4.4 of the `DataCite Schema <https://schema.datacite.org/>`_"""

    title: list[str] = Field(..., description='Title for the artifact')


class Step(BaseModel):
    """A step within a model pipeline."""

    provider: ProviderChoices = Field('funcx', description='Service used to execute this step')
    flavor: FlavorChoices = Field(..., description='Type of step being executed')

    description: FlavorChoices = Field(..., description='Purpose of this step')

    input_args: List['DataType'] = Field(..., description='Descriptions of positional arguments')
    input_kwargs: Dict[str, 'DataType'] = Field(default_factory=dict, description='Descriptions of named arguments')
    output: 'DataType' = Field(description='Type of the data produced by the step')

    # TODO (wardlt): Add a function that gathers all necessary files/creates a ZIP?


class DataType(BaseModel):
    """Description of data type, either input or output"""

    type: str = Field(..., description='Name of the data type')

    # TODO (wardlt): Add a function which validates the data type?


# --> Example Implementations of Steps Types

class TensorflowModelStep(Step):
    """A step which runs a TensorFlow Model"""

    flavor = 'tensorflow'
    savedmodel_path: FilePath = Field(..., description='Path to the directory containing the architecture and weights')
    function_name: str = Field('DEFAULT', description='Name of the function from the model to be served')


class StaticPythonStep(Step):
    """A step which runs a Python static function"""

    flavor = 'python'
    module: str = Field(..., description='Module containing the function')
    name: str = Field(..., description='Name of the function')


# --> Example Implementations of Data Types

class AnyType(DataType):
    """A type that matches anything"""

    type = 'any'


class Float(DataType):
    """A floating-point number"""
    type = 'float'


class Tensor(DataType):
    """A rectangular array of data"""

    type = 'tensor'
    dtype: DataType = Field(..., description='Type of items contained within the array')
