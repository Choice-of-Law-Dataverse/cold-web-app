"""Base classes and utilities for prompt management."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class PromptMetadata:
    """Metadata for a prompt template."""

    name: str
    description: str
    version: str
    required_params: list[str]
    legal_system: str | None = None
    jurisdiction: str | None = None
    prompt_type: str | None = None


class BasePrompt(ABC):
    """Base class for all prompt templates."""

    def __init__(self, metadata: PromptMetadata):
        self.metadata = metadata
        self._validate_template()

    @abstractmethod
    def get_template(self) -> str:
        """Return the prompt template string."""

    def _validate_template(self) -> None:
        """Validate that the template contains all required parameters."""
        template = self.get_template()
        missing_params = []

        for param in self.metadata.required_params:
            placeholder = f"{{{param}}}"
            if placeholder not in template:
                missing_params.append(param)

        if missing_params:
            raise ValueError(
                f"Prompt '{self.metadata.name}' is missing required parameters: {missing_params}"
            )

    def format(self, **kwargs: Any) -> str:
        """Format the prompt template with provided parameters."""
        # Validate that all required parameters are provided
        missing = set(self.metadata.required_params) - set(kwargs.keys())
        if missing:
            raise ValueError(
                f"Missing required parameters for prompt '{self.metadata.name}': {missing}"
            )

        return self.get_template().format(**kwargs)

    def get_info(self) -> dict[str, Any]:
        """Get information about this prompt."""
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "version": self.metadata.version,
            "required_params": self.metadata.required_params,
            "legal_system": self.metadata.legal_system,
            "jurisdiction": self.metadata.jurisdiction,
            "prompt_type": self.metadata.prompt_type,
        }


class PromptRegistry:
    """Registry for managing and accessing prompts."""

    def __init__(self):
        self._prompts: dict[str, BasePrompt] = {}
        self._index: dict[str, dict[str, list[str]]] = {
            "legal_system": {},
            "jurisdiction": {},
            "prompt_type": {},
        }

    def register(self, prompt: BasePrompt) -> None:
        """Register a prompt in the registry."""
        key = self._make_key(
            prompt.metadata.legal_system,
            prompt.metadata.jurisdiction,
            prompt.metadata.prompt_type,
        )

        self._prompts[key] = prompt

        # Update indices
        if prompt.metadata.legal_system:
            if prompt.metadata.legal_system not in self._index["legal_system"]:
                self._index["legal_system"][prompt.metadata.legal_system] = []
            self._index["legal_system"][prompt.metadata.legal_system].append(key)

        if prompt.metadata.jurisdiction:
            if prompt.metadata.jurisdiction not in self._index["jurisdiction"]:
                self._index["jurisdiction"][prompt.metadata.jurisdiction] = []
            self._index["jurisdiction"][prompt.metadata.jurisdiction].append(key)

        if prompt.metadata.prompt_type:
            if prompt.metadata.prompt_type not in self._index["prompt_type"]:
                self._index["prompt_type"][prompt.metadata.prompt_type] = []
            self._index["prompt_type"][prompt.metadata.prompt_type].append(key)

    def get(
        self,
        legal_system: str | None = None,
        jurisdiction: str | None = None,
        prompt_type: str | None = None,
    ) -> BasePrompt | None:
        """Get a prompt by legal system, jurisdiction, and type."""
        # Try to find the most specific match first
        # 1. Try exact match with jurisdiction
        if jurisdiction:
            key = self._make_key(legal_system, jurisdiction, prompt_type)
            if key in self._prompts:
                return self._prompts[key]

        # 2. Try match with legal system only
        if legal_system:
            key = self._make_key(legal_system, None, prompt_type)
            if key in self._prompts:
                return self._prompts[key]

        # 3. Try match with prompt type only
        key = self._make_key(None, None, prompt_type)
        if key in self._prompts:
            return self._prompts[key]

        return None

    def list_by_legal_system(self, legal_system: str) -> list[BasePrompt]:
        """List all prompts for a legal system."""
        keys = self._index["legal_system"].get(legal_system, [])
        return [self._prompts[key] for key in keys]

    def list_by_jurisdiction(self, jurisdiction: str) -> list[BasePrompt]:
        """List all prompts for a jurisdiction."""
        keys = self._index["jurisdiction"].get(jurisdiction, [])
        return [self._prompts[key] for key in keys]

    def list_by_type(self, prompt_type: str) -> list[BasePrompt]:
        """List all prompts of a specific type."""
        keys = self._index["prompt_type"].get(prompt_type, [])
        return [self._prompts[key] for key in keys]

    def list_all(self) -> list[BasePrompt]:
        """List all registered prompts."""
        return list(self._prompts.values())

    def _make_key(
        self,
        legal_system: str | None,
        jurisdiction: str | None,
        prompt_type: str | None,
    ) -> str:
        """Create a unique key for a prompt."""
        parts = [
            legal_system or "default",
            jurisdiction or "default",
            prompt_type or "default",
        ]
        return ":".join(parts)


# Global registry instance
_registry = PromptRegistry()


def get_registry() -> PromptRegistry:
    """Get the global prompt registry."""
    return _registry
