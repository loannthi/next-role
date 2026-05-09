"""Define the career agent."""

import deepagents.graph as _graph_mod
import deepagents.middleware.filesystem as _fs_mw
import deepagents.middleware.memory as _mem_mw
import deepagents.middleware.skills as _skills_mw
import deepagents.middleware.subagents as _sub_mw
import langchain.agents.middleware.todo as _todo_mw
from backend.app.career_agent import prompts as _prompts
from backend.app.career_agent.middleware import UtcDatetimeMiddleware
from backend.app.career_agent.tools import (
    CAREER_AGENT_DIR,
    make_extract_jd,
    make_list_files,
    make_overwrite_file,
    make_parse_document,
)
from backend.app.career_agent.utils import load_subagents
from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StoreBackend


def _apply_prompt_overrides() -> None:
    """Replace the prompts that deepagents/langchain inject into the system message.

    Most middlewares read their constant by bare name at call time, so patching
    the module attribute is enough. `TodoListMiddleware` and `SubAgentMiddleware`
    are different — they capture the constant as a keyword-only default arg,
    which Python freezes into `__init__.__kwdefaults__` at class-definition
    time. Reassigning the module attribute after that does nothing; we must
    patch `__kwdefaults__` directly.

    `BASE_AGENT_PROMPT` is patched here (rather than via
    `HarnessProfile.base_system_prompt`) because the harness-profile overlay
    also replaces declarative subagents' authored `system_prompt`, wiping out
    the prompts defined in `subagents.yaml`. Patching the module constant
    affects only the main agent's base, not subagent specs.

    Must run before `create_deep_agent()`. Process-global side effect — any
    other deep agent instantiated in the same Python process after this runs
    will also see these prompts.
    """
    # `setattr` (rather than direct assignment) sidesteps ty's literal-type
    # narrowing on the module-level `BASE_AGENT_PROMPT` constant.
    setattr(_graph_mod, "BASE_AGENT_PROMPT", _prompts.BASE)  # noqa: B010

    _skills_mw.SKILLS_SYSTEM_PROMPT = _prompts.SKILLS
    _fs_mw._FILESYSTEM_SYSTEM_PROMPT_TEMPLATE = _prompts.FILESYSTEM  # noqa: SLF001
    _fs_mw.FILESYSTEM_SYSTEM_PROMPT = _prompts.FILESYSTEM.format(
        large_tool_results_prefix="/large_tool_results",
    )
    _fs_mw.EXECUTION_SYSTEM_PROMPT = _prompts.EXECUTION
    _mem_mw.MEMORY_SYSTEM_PROMPT = _prompts.MEMORY

    _todo_mw.WRITE_TODOS_SYSTEM_PROMPT = _prompts.TODO
    _sub_mw.TASK_SYSTEM_PROMPT = _prompts.TASK

    _todo_mw.TodoListMiddleware.__init__.__kwdefaults__["system_prompt"] = _prompts.TODO  # type: ignore # noqa: PGH003
    _sub_mw.SubAgentMiddleware.__init__.__kwdefaults__["system_prompt"] = _prompts.TASK  # type: ignore # noqa: PGH003


_apply_prompt_overrides()


_MODEL = "bedrock_converse:global.anthropic.claude-sonnet-4-6"


_backend = CompositeBackend(
    default=FilesystemBackend(root_dir=CAREER_AGENT_DIR, virtual_mode=True),
    routes={
        "/memory/": StoreBackend(
            namespace=lambda _: ("career_agent", "memory"),
        ),
        "/processed": StoreBackend(
            namespace=lambda _: ("career_agent", "processed"),
        ),
        "/research/": StoreBackend(
            namespace=lambda _: ("career_agent", "research"),
        ),
        "/interview_coach/": StoreBackend(
            namespace=lambda _: ("career_agent", "interview_coach"),
        ),
        "/large_tool_results/": StoreBackend(
            namespace=lambda _: ("career_agent", "large_tool_results"),
        ),
        "/workspace/": StoreBackend(
            namespace=lambda _: ("career_agent", "workspace"),
        ),
    },
)

career_agent = create_deep_agent(
    system_prompt=_prompts.SYSTEM_PROMPT,
    model=_MODEL,
    memory=["AGENTS.md"],
    skills=["skills/"],
    tools=[
        make_list_files(_backend),
        make_parse_document(_backend),
        make_extract_jd(_backend),
        make_overwrite_file(_backend),
    ],
    subagents=load_subagents(CAREER_AGENT_DIR / "subagents.yaml"),
    backend=_backend,
    middleware=[UtcDatetimeMiddleware()],
)
