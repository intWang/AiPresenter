# Localized Q&A And Alias Content Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the first slice of multilingual Q&A and entrypoint aliases into package data while preserving deterministic safety behavior.

**Architecture:** Extend Pydantic package models with optional localized Q&A and `questionAliases`. Update `runtime.questions` to use package-owned aliases and localized answers before legacy built-in aliases. Update RingCentral YAML with a small, tested Chinese slice.

**Tech Stack:** Python, Pydantic, pytest, YAML material package.

---

### Task 1: Package-Owned Localized Q&A And Aliases

**Files:**
- Modify: `src/ai_presenter/packages/models.py`
- Modify: `src/ai_presenter/runtime/questions.py`
- Modify: `packages/ringcentral-video.yaml`
- Modify: `tests/unit/test_questions.py`
- Modify: `tests/unit/test_material_packages.py`
- Modify: `docs/knowledge/ringcentral-video/source-index.md`
- Create: `docs/agent-handoffs/cycle-006-implementation.md`

- [ ] **Step 1: Write failing package-model tests**

In `tests/unit/test_material_packages.py`, add:

```python
def test_question_answers_support_localized_questions_and_answers() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    item = next(qa for qa in package.qa if qa.question == "How do I protect my real background?")

    assert "zh" in item.localized_questions
    assert "怎么保护我的真实背景" in item.localized_questions["zh"]
    assert item.localized_answers["zh"].startswith("打开 Settings")


def test_operation_entrypoints_support_package_owned_question_aliases() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))
    chat = package.entrypoint_by_id("ringcentral.video.toolbar.chat")

    assert "zh" in chat.question_aliases
    assert "聊天在哪里" in chat.question_aliases["zh"]
```

- [ ] **Step 2: Write failing question tests**

In `tests/unit/test_questions.py`, add:

```python
from ai_presenter.packages.models import MaterialPackage


def test_package_owned_alias_matches_without_legacy_alias_table() -> None:
    package = MaterialPackage.model_validate(
        {
            "appId": "demo",
            "appName": "Demo",
            "version": 1,
            "profileIds": ["demo-profile"],
            "operationEntrypoints": [
                {
                    "id": "demo.panel",
                    "title": "Panel",
                    "area": "Main",
                    "purpose": "Open the demo panel.",
                    "questionAliases": {"zh": ["自定义面板"]},
                    "openSteps": [
                        {
                            "action": "clickWindowControl",
                            "target": "Panel",
                            "match": {"controlType": "button"},
                        }
                    ],
                }
            ],
            "demoFlows": [],
            "manualControls": [],
        }
    )

    response = answer_question(
        package=package,
        question="自定义面板在哪里",
        voice=PresenterVoiceSettings(language="zh"),
    )

    assert response.entrypoint_id == "demo.panel"
    assert response.can_operate is True


def test_localized_qa_question_returns_localized_answer() -> None:
    package = load_material_package(Path("packages/ringcentral-video.yaml"))

    response = answer_question(
        package=package,
        question="怎么保护我的真实背景",
        voice=PresenterVoiceSettings(language="zh", tone="professional"),
    )

    assert response.entrypoint_id == "ringcentral.video.settings.background"
    assert response.answer_text.startswith("打开 Settings")
    assert "Blur" in response.answer_text
```

- [ ] **Step 3: Run focused tests and verify RED**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py::test_question_answers_support_localized_questions_and_answers tests\unit\test_material_packages.py::test_operation_entrypoints_support_package_owned_question_aliases tests\unit\test_questions.py::test_package_owned_alias_matches_without_legacy_alias_table tests\unit\test_questions.py::test_localized_qa_question_returns_localized_answer
```

Expected: failures because model fields and matching support are not implemented yet.

- [ ] **Step 4: Extend package models**

In `src/ai_presenter/packages/models.py`:

```python
class OperationEntrypoint(CamelModel):
    id: str
    title: str
    area: str
    purpose: str
    open_steps: list[PackageOpenStep] = Field(default_factory=list, alias="openSteps")
    presenter_notes: list[str] = Field(default_factory=list, alias="presenterNotes")
    question_aliases: dict[str, list[str]] = Field(default_factory=dict, alias="questionAliases")
```

and:

```python
class QuestionAnswer(CamelModel):
    question: str
    answer: str
    localized_questions: dict[str, list[str]] = Field(
        default_factory=dict,
        alias="localizedQuestions",
    )
    localized_answers: dict[str, str] = Field(default_factory=dict, alias="localizedAnswers")
    related_entrypoint_ids: list[str] = Field(default_factory=list, alias="relatedEntrypointIds")
```

- [ ] **Step 5: Update question matching**

In `src/ai_presenter/runtime/questions.py`:

- Pass `voice.language` into `_match_qa`.
- Match Q&A against `item.question` and all strings in `item.localized_questions.values()`.
- Render `item.localized_answers[voice.language]` when present.
- Add package-owned alias matching before legacy `_ENTRYPOINT_ALIASES`.
- Keep longest-alias wins across package-owned aliases.

Suggested helper shapes:

```python
def _qa_questions(item: QuestionAnswer) -> list[str]:
    questions = [item.question]
    for localized in item.localized_questions.values():
        questions.extend(localized)
    return questions


def _qa_answer_text(item: QuestionAnswer, voice: PresenterVoiceSettings) -> str:
    return item.localized_answers.get(voice.language, item.answer)
```

and update `_match_entrypoint_alias` to scan `entrypoint.question_aliases`.

- [ ] **Step 6: Update RingCentral YAML**

Add Chinese localized Q&A for background privacy:

```yaml
- question: How do I protect my real background?
  localizedQuestions:
    zh:
    - 怎么保护我的真实背景
    - 怎么模糊背景
  answer: Open Settings, choose Background, and select Blur or a virtual background. Blur is the safest default
    for privacy because it hides room detail while keeping the person visible.
  localizedAnswers:
    zh: 打开 Settings，选择 Background，然后选择 Blur 或虚拟背景。Blur 是最稳妥的隐私默认项，因为它会隐藏房间细节，同时保留人物可见。
  relatedEntrypointIds:
  - ringcentral.video.settings.background
  - ringcentral.video.settings.background.blur
```

Add `questionAliases.zh` to these entrypoints:

- `ringcentral.video.toolbar.chat`: `聊天`, `聊天室`, `消息`, `聊天在哪里`
- `ringcentral.video.toolbar.invite`: `邀请`, `邀请别人`, `拉人`, `加人`
- `ringcentral.video.toolbar.share`: `共享屏幕`, `分享屏幕`, `屏幕共享`, `共享`
- `ringcentral.video.settings.background`: `背景`, `虚拟背景`, `模糊背景`, `设置背景`
- `ringcentral.video.toolbar.leave`: `离开会议`, `退出会议`, `结束会议`

- [ ] **Step 7: Run focused tests and verify GREEN**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py
```

Expected: focused tests pass, including mojibake negative regression and risky aliases.

- [ ] **Step 8: Update knowledge docs**

In `docs/knowledge/ringcentral-video/source-index.md`, update the question-matching row to say Cycle 006 adds package-owned localized Q&A and `questionAliases`, while legacy Python aliases remain as fallback.

- [ ] **Step 9: Write implementation handoff**

Create `docs/agent-handoffs/cycle-006-implementation.md` with actual RED/GREEN commands, files changed, and remaining risks.

- [ ] **Step 10: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
```

Expected: full test suite passes with only the known `pywinauto` STA COM threading warning.
