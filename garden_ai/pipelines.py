from __future__ import annotations

import logging
from functools import reduce
from inspect import signature
from typing import Any, List, Tuple, cast
from uuid import UUID, uuid4

from pydantic import Field, validator
from pydantic.dataclasses import dataclass

from garden_ai.steps import DataclassConfig, Step
from garden_ai.utils import safe_compose

logger = logging.getLogger()


@dataclass(config=DataclassConfig)
class Pipeline:
    """
    The `Pipeline` class represents a sequence of steps
    that form a pipeline. It has a list of authors, a title,
    and a list of steps. The __call__ method can be used
    to execute the pipeline by calling each Step in order
    with the output of the previous Step as the input to the
    next Step. The register method can be used to register
    each Step in the pipeline.

    Args:
    authors (List[str]): A list of the authors of the pipeline.
    title (str): The title of the pipeline.
    steps (List[Step]): A list of the steps in the pipeline.

    """

    title: str = Field(...)
    authors: List[str] = Field(...)
    steps: Tuple[Step, ...] = Field(...)
    contributors: List[str] = Field(default_factory=list, unique_items=True)
    doi: str = cast(str, Field(default_factory=lambda: None))
    uuid: UUID = Field(default_factory=uuid4)
    # note: tuple vs list decision; a list of authors is conceptually more mutable than
    # the list of steps ought to be, but maybe we should just use tuples everywhere?

    def _composed_steps(*args, **kwargs):
        """ "This method intentionally left blank"

        We define this as a stub here, instead setting it as an attribute in
        `__post_init_post_parse__`, which is the earliest point after we
        validate that the steps are composable that we could modify the Pipeline
        object.
        This indirection is only necessary because `__call__` itself is looked
        up at the class level, so can't be set dynamically for different instances.
        """
        raise NotImplementedError

    @validator("steps")
    def check_steps_composable(cls, steps):
        if len(steps) == 0:
            raise ValueError("Cannot have no steps in a pipeline.")
        try:
            reduce(safe_compose, reversed(steps))
        except TypeError as e:
            logger.error(e)
            raise
        return steps

    def register_pipeline(self):
        """register this `Pipeline`'s complete Step composition as a funcx function
        TODO
        """
        raise NotImplementedError

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self._composed_steps(*args, **kwargs)

    def __post_init_post_parse__(self):
        """Build a single composite function from this pipeline's steps.

        I think it seems reasonable for the default to compose each Step
        together like this so that the entire pipeline can be run as the same
        funcx function, but we might want to think about how/why we might let
        users opt out of this behavior in certain cases.
        """
        self._composed_steps = reduce(safe_compose, reversed(self.steps))
        self.__signature__ = signature(self._composed_steps)
        self._sync_author_metadata()
        return

    def _sync_author_metadata(self):
        known_authors = set(self.authors)
        known_contributors = set(self.contributors)
        for step in self.steps:
            new_contributors = set(step.authors) | set(step.contributors)
            known_contributors |= new_contributors - known_authors
        self.contributors = list(known_contributors)
        return

    def register(self):
        raise NotImplementedError
