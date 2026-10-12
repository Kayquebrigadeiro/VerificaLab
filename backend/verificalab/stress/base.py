"""Contratos comuns para adapters de ferramentas de stress."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import ClassVar

from verificalab.core.runner import RunResult
from verificalab.stress.registry import MaxLimits, ToolRegistry

StressResult = RunResult


@dataclass(frozen=True, slots=True)
class StressRequest:
    target: str
    duration_s: int = 5
    threads: int = 1
    port: int | None = None
    path: str = "/"
    extra_args: tuple[str, ...] = ()


class StressAdapter(ABC):
    """Base para executar ferramentas com limites declarados no catálogo."""

    tool_id: ClassVar[str]

    def clamp(self, req: StressRequest) -> StressRequest:
        if not isinstance(req, StressRequest):
            raise TypeError("req deve ser StressRequest")
        if type(req.duration_s) is not int or req.duration_s <= 0:
            raise ValueError("duration_s deve ser um inteiro positivo")
        if type(req.threads) is not int or req.threads <= 0:
            raise ValueError("threads deve ser um inteiro positivo")

        tool = ToolRegistry.load().get(self.tool_id)
        if tool is None:
            raise ValueError(f"ferramenta ausente do catálogo: {self.tool_id}")
        limits = tool.max_limits or MaxLimits(
            duration_s=tool.default_limits.duration_s,
            threads=tool.default_limits.threads,
        )
        return replace(
            req,
            duration_s=min(req.duration_s, limits.duration_s),
            threads=min(req.threads, limits.threads),
        )

    @abstractmethod
    def build_cmd(self, req: StressRequest) -> list[str]:
        """Monta argumentos sem shell para a ferramenta configurada."""

    @abstractmethod
    def run(self, req: StressRequest) -> RunResult:
        """Autoriza, limita e executa o teste."""
