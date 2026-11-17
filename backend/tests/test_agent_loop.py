from types import SimpleNamespace
from typing import Any

import pytest

from app.agent.loop import MAX_STEPS, AgentRunner
from app.agent.skill_gap import compute_skill_gap
from app.agent.writing import CoverLetter, InterviewPrep, InterviewQuestion

GAP = compute_skill_gap(["Python"], {"Python": True, "Go": True}, 1, 2)
LETTER = CoverLetter(motivation="a", competency="b", projects="c", aspiration="d")
PREP = InterviewPrep(
    questions=[InterviewQuestion(category="technical", question="q", answer_direction="a")] * 10
)


class FakeToolbox:
    def __init__(self, fail_letter_times: int = 0) -> None:
        self.gap: Any = None
        self.cover_letter: Any = None
        self.interview: Any = None
        self.calls: list[str] = []
        self.tones: list[str | None] = []
        self.fail_letter_times = fail_letter_times

    async def get_resume(self) -> dict[str, Any]:
        self.calls.append("get_resume")
        return {"skills": ["Python"]}

    async def get_job(self) -> dict[str, Any]:
        self.calls.append("get_job")
        return {"skills": {"Python": "required"}}

    async def compute_skill_gap(self) -> dict[str, Any]:
        self.calls.append("compute_skill_gap")
        self.gap = GAP
        return GAP.model_dump()

    async def draft_cover_letter(self, tone: str | None = None) -> dict[str, Any]:
        self.calls.append("draft_cover_letter")
        self.tones.append(tone)
        if self.fail_letter_times:
            self.fail_letter_times -= 1
            raise RuntimeError("model hiccup")
        self.cover_letter = LETTER
        return {"motivation": 1}

    async def generate_interview_questions(self) -> dict[str, Any]:
        self.calls.append("generate_interview_questions")
        self.interview = PREP
        return {"questions": ["q"] * 10}


def call(name: str, **args: Any) -> SimpleNamespace:
    return SimpleNamespace(name=name, args=args, id=f"id-{name}")


def turn(*calls: SimpleNamespace, text: str = "") -> SimpleNamespace:
    content = SimpleNamespace(role="model", parts=[])
    return SimpleNamespace(
        function_calls=list(calls), text=text, candidates=[SimpleNamespace(content=content)]
    )


class ScriptedModels:
    def __init__(self, turns: list[SimpleNamespace], error: Exception | None = None) -> None:
        self.turns = turns
        self.error = error
        self.requests: list[Any] = []

    async def generate_content(self, *, model: str, contents: list[Any], config: Any) -> Any:
        self.requests.append(list(contents))
        if self.error:
            raise self.error
        return self.turns.pop(0) if self.turns else turn(text="done")


def runner(
    models: ScriptedModels, box: FakeToolbox, events: list[Any] | None = None
) -> AgentRunner:
    async def emit(step: dict[str, Any]) -> None:
        if events is not None:
            events.append(step)

    client = SimpleNamespace(aio=SimpleNamespace(models=models))
    return AgentRunner(client, "m", box, emit)


async def test_full_run_follows_model_and_streams_steps() -> None:
    models = ScriptedModels(
        [
            turn(call("get_resume"), call("get_job")),
            turn(call("compute_skill_gap")),
            turn(call("draft_cover_letter", tone="열정적인")),
            turn(call("generate_interview_questions")),
            turn(text="Moslik 50%. Go o'rganing."),
        ]
    )
    box, events = FakeToolbox(), list[Any]()
    result = await runner(models, box, events).run("uz")
    assert box.calls == [
        "get_resume",
        "get_job",
        "compute_skill_gap",
        "draft_cover_letter",
        "generate_interview_questions",
    ]
    assert box.tones == ["열정적인"]
    assert result.summary == "Moslik 50%. Go o'rganing."
    assert result.gap.match_percent == 50
    assert [e["tool"] for e in events] == box.calls
    assert all(step["ok"] and not step["fallback"] for step in result.steps)
    tool_reply = models.requests[1][-1]
    assert tool_reply.role == "user"
    assert tool_reply.parts[0].function_response.id == "id-get_resume"


async def test_tool_error_is_returned_to_model_which_retries() -> None:
    models = ScriptedModels(
        [
            turn(call("draft_cover_letter", resume_id="someone-else")),
            turn(call("draft_cover_letter")),
            turn(call("generate_interview_questions")),
        ]
    )
    box = FakeToolbox(fail_letter_times=1)
    result = await runner(models, box).run("en")
    first_reply = models.requests[1][-1].parts[0].function_response.response
    assert "Unexpected arguments" in first_reply["error"]
    assert [s["ok"] for s in result.steps][:2] == [False, False]
    assert result.steps[1]["summary"] == "error: RuntimeError"
    assert result.cover_letter == LETTER


async def test_early_stop_triggers_fallback() -> None:
    box = FakeToolbox()
    result = await runner(ScriptedModels([turn(call("get_job")), turn(text="ok")]), box).run("en")
    fallback = [s["tool"] for s in result.steps if s["fallback"]]
    assert fallback == ["compute_skill_gap", "draft_cover_letter", "generate_interview_questions"]
    assert result.summary == "ok"


async def test_model_failure_still_produces_result() -> None:
    box = FakeToolbox()
    result = await runner(ScriptedModels([], error=RuntimeError("api down")), box).run("en")
    assert result.summary == ""
    assert all(s["fallback"] for s in result.steps)


async def test_step_limit_is_enforced() -> None:
    models = ScriptedModels([turn(call("get_job")) for _ in range(MAX_STEPS + 5)])
    box = FakeToolbox()
    await runner(models, box).run("en")
    assert len(models.requests) == MAX_STEPS
    assert box.calls.count("get_job") == MAX_STEPS


async def test_unrecoverable_failure_raises() -> None:
    box = FakeToolbox(fail_letter_times=99)
    with pytest.raises(RuntimeError, match="could not finish"):
        await runner(ScriptedModels([turn(text="stop")]), box).run("en")
