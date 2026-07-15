"""Operational, dependency-injected handlers for universal-entry lanes.

These handlers perform bounded work without granting authority. External systems
are supplied as callables so entry adapters never own provider, repository, or
custody credentials. The conversational handler doubles as the final synthesis
layer when prior lane results are present.
"""

from __future__ import annotations

import ast
import operator
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Mapping, Protocol, Sequence


class EcosystemRetriever(Protocol):
    def __call__(self, query: str, context: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]: ...


class ExternalLLMProvider(Protocol):
    def __call__(self, prompt: str, context: Mapping[str, Any]) -> Mapping[str, Any]: ...


NON_AUTHORITY = {
    "authorizing": False,
    "execution_authority_granted": False,
    "custody_transferred": False,
    "admissibility_determined": False,
}


def _message(envelope: Mapping[str, Any]) -> str:
    request = envelope.get("request", {})
    if not isinstance(request, Mapping):
        return ""
    value = request.get("message", request.get("content", ""))
    return str(value).strip()


def _completed(**values: Any) -> Dict[str, Any]:
    return {"status": "completed", **NON_AUTHORITY, **values}


def _degraded(reason: str, **values: Any) -> Dict[str, Any]:
    return {"status": "degraded", "reason": reason, **NON_AUTHORITY, **values}


def _unavailable(reason: str, **values: Any) -> Dict[str, Any]:
    return {"status": "unavailable", "reason": reason, **NON_AUTHORITY, **values}


def conversation_handler(
    envelope: Mapping[str, Any], context: Mapping[str, Any]
) -> Mapping[str, Any]:
    """Respond naturally and synthesize any prior operational lane results."""

    message = _message(envelope)
    prior = list(context.get("lane_results", []))
    useful = [result for result in prior if result.get("lane") != "conversation"]

    if useful:
        fragments = []
        sources = []
        for result in useful:
            if result.get("status") not in {"completed", "degraded"}:
                continue
            text = result.get("response") or result.get("answer") or result.get("summary")
            if text:
                fragments.append(str(text).strip())
            for source in result.get("sources", []) or []:
                if source not in sources:
                    sources.append(source)
        if fragments:
            return _completed(
                response="\n\n".join(fragments),
                synthesis=True,
                source_count=len(sources),
                sources=sources,
            )
        return _degraded(
            "NO_SYNTHESIZABLE_ENGINE_OUTPUT",
            response="The selected engines returned no user-facing content.",
            synthesis=True,
        )

    lowered = message.casefold()
    if re.fullmatch(r"(?:hi|hello|hey|hiya|howdy|greetings)[.!?\s]*", message, re.I):
        response = "Hello! How can I help you explore or work with the StegVerse ecosystem today?"
    elif re.fullmatch(r"good\s+morning[.!?\s]*", message, re.I):
        response = "Good morning! How can I help you explore or work with the StegVerse ecosystem today?"
    elif re.fullmatch(r"good\s+afternoon[.!?\s]*", message, re.I):
        response = "Good afternoon! How can I help you explore or work with the StegVerse ecosystem today?"
    elif re.fullmatch(r"good\s+evening[.!?\s]*", message, re.I):
        response = "Good evening! How can I help you explore or work with the StegVerse ecosystem today?"
    elif re.fullmatch(r"(?:thanks|thank\s+you|much\s+appreciated)[.!?\s]*", message, re.I):
        response = "You’re welcome. What would you like to work on next?"
    elif "what can you do" in lowered:
        response = (
            "I can hold a conversation and route ecosystem, external-information, "
            "and solver requests through the capabilities installed on this node."
        )
    else:
        response = (
            "I understand this as a conversational request, but this local handler "
            "does not yet have a general language model attached."
        )
        return _degraded("GENERAL_CONVERSATION_MODEL_NOT_ATTACHED", response=response)
    return _completed(response=response, synthesis=False)


@dataclass(frozen=True)
class EcosystemQueryHandler:
    retriever: EcosystemRetriever | None = None

    def __call__(self, envelope: Mapping[str, Any], context: Mapping[str, Any]) -> Mapping[str, Any]:
        query = _message(envelope)
        if self.retriever is None:
            return _unavailable(
                "ECOSYSTEM_RETRIEVER_NOT_CONFIGURED",
                response="Authoritative ecosystem retrieval is unavailable on this node.",
                sources=[],
            )
        records = list(self.retriever(query, context))
        if not records:
            return _degraded(
                "NO_AUTHORITATIVE_ECOSYSTEM_RECORDS",
                response="No authoritative ecosystem records matched the request.",
                sources=[],
            )
        snippets = []
        sources = []
        for record in records:
            text = record.get("text") or record.get("summary") or record.get("content")
            source = record.get("source") or record.get("uri") or record.get("repository")
            if text:
                snippets.append(str(text).strip())
            if source and source not in sources:
                sources.append(source)
        if not snippets:
            return _degraded(
                "RETRIEVAL_RECORDS_LACK_CONTENT",
                response="Authoritative records were found but contained no usable response content.",
                sources=sources,
            )
        return _completed(
            response="\n\n".join(snippets),
            sources=sources,
            evidence_count=len(records),
            retrieval_authoritative=True,
        )


@dataclass(frozen=True)
class ExternalLLMHandler:
    provider: ExternalLLMProvider | None = None

    def __call__(self, envelope: Mapping[str, Any], context: Mapping[str, Any]) -> Mapping[str, Any]:
        prompt = _message(envelope)
        if self.provider is None:
            return _unavailable(
                "EXTERNAL_LLM_PROVIDER_NOT_CONFIGURED",
                response="External LLM access is unavailable on this node.",
            )
        provider_result = dict(self.provider(prompt, context))
        output = provider_result.get("response") or provider_result.get("output") or provider_result.get("text")
        if not output:
            return _degraded(
                "EXTERNAL_LLM_EMPTY_RESPONSE",
                response="The external provider returned no usable response.",
                provider=provider_result.get("provider"),
                model=provider_result.get("model"),
            )
        return _completed(
            response=str(output),
            provider=provider_result.get("provider"),
            model=provider_result.get("model"),
            usage=provider_result.get("usage"),
            provider_receipt=provider_result.get("receipt_id"),
        )


_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_ALLOWED_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval_numeric(node: ast.AST) -> float | int:
    if isinstance(node, ast.Expression):
        return _eval_numeric(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left = _eval_numeric(node.left)
        right = _eval_numeric(node.right)
        if isinstance(node.op, ast.Pow) and abs(float(right)) > 12:
            raise ValueError("exponent outside bounded solver range")
        return _ALLOWED_BINOPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_eval_numeric(node.operand))
    raise ValueError("unsupported expression")


def solver_handler(envelope: Mapping[str, Any], context: Mapping[str, Any]) -> Mapping[str, Any]:
    """Evaluate bounded arithmetic only; symbolic work requires a separate engine."""

    message = _message(envelope)
    candidate = re.sub(r"^(?:solve|calculate)\s+", "", message.strip(), flags=re.I)
    candidate = candidate.rstrip(" ?")
    if len(candidate) > 120:
        return _degraded("SOLVER_EXPRESSION_TOO_LONG", response="The expression exceeds the local solver limit.")
    try:
        tree = ast.parse(candidate, mode="eval")
        value = _eval_numeric(tree)
    except Exception:
        return _degraded(
            "SYMBOLIC_OR_UNSUPPORTED_SOLVER_REQUEST",
            response="This node’s local solver currently supports bounded arithmetic expressions only.",
        )
    return _completed(
        response=f"{candidate} = {value}",
        expression=candidate,
        result=value,
        checked_locally=True,
    )


def build_default_handler_registry(
    *,
    ecosystem_retriever: EcosystemRetriever | None = None,
    external_llm_provider: ExternalLLMProvider | None = None,
) -> Dict[str, Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]]:
    """Build the standard non-authorizing handler registry for a node."""

    return {
        "conversation": conversation_handler,
        "ecosystem_query": EcosystemQueryHandler(ecosystem_retriever),
        "external_llm": ExternalLLMHandler(external_llm_provider),
        "solver": solver_handler,
    }
