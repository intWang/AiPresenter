# RingCentral Safety Presenter Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add and wire a RingCentral-specific presenter safety skill into all RingCentral profiles so OpenAI and Codex CLI narration receive concrete RingCentral privacy and side-effect boundaries.

**Architecture:** This is a prompt-context slice. Profiles keep the existing `skillPaths` mechanism; `load_presenter_context()` and provider prompt builders should continue working without production-code changes.

**Tech Stack:** YAML profiles, Markdown presenter skills, pytest, ruff, mypy.

---

### Task 1: Lock Profile Loading Expectations

**Files:**
- Modify: `tests/unit/test_config_loader.py`
- Modify: `tests/unit/test_presenter_context.py`
- Create: `tests/unit/test_presenter_skill_packaging.py`

- [ ] **Step 1: Write failing config loader assertion**

Update `test_load_ringcentral_bind_speaker_profile` so `profile.narration.skill_paths` expects:

```python
[
    Path("presenter/skills/app-director.md").resolve(),
    Path("presenter/skills/live-explainer.md").resolve(),
    Path("presenter/skills/ringcentral-safety.md").resolve(),
]
```

- [ ] **Step 2: Write failing presenter context assertion**

Update `test_load_presenter_context_reads_configured_soul_and_memory` so it expects:

```python
assert [skill.name for skill in context.skills] == [
    "app-director",
    "live-explainer",
    "ringcentral-safety",
]
assert "ringcentral video safety guardian" in context.skills[2].content.lower()
assert "recording and leave/end stay explain-only" in context.skills[2].content.lower()
```

- [ ] **Step 3: Add all-profile and packaged-profile assertions**

Add a parametrized config-loader test:

```python
@pytest.mark.parametrize(
    "profile_path",
    [
        Path("profiles/ringcentral-video.yaml"),
        Path("profiles/ringcentral-video-bind-speaker.yaml"),
        Path("profiles/ringcentral-video-codex-cli-speaker.yaml"),
        Path("profiles/ringcentral-video-openai.example.yaml"),
        Path("profiles/ringcentral-video-piper-speaker.yaml"),
    ],
)
def test_all_ringcentral_profiles_include_ringcentral_safety_skill(
    profile_path: Path,
) -> None:
    profile = load_profile(profile_path)

    assert [path.stem for path in profile.narration.skill_paths] == [
        "app-director",
        "live-explainer",
        "ringcentral-safety",
    ]
```

Add a packaged-profile test:

```python
def test_packaged_ringcentral_profile_resolves_packaged_safety_skill() -> None:
    profile = load_profile(Path("src/ai_presenter/profiles/ringcentral-video.yaml"))

    assert profile.narration.skill_paths[-1] == Path(
        "src/ai_presenter/presenter/skills/ringcentral-safety.md"
    ).resolve()
```

- [ ] **Step 4: Add root/packaged skill copy sync test**

Create `tests/unit/test_presenter_skill_packaging.py` with a test that compares root and packaged skill filenames and content:

```python
def test_packaged_presenter_skill_copies_match_repo_skills() -> None:
    repo_skill_dir = Path("presenter/skills")
    packaged_skill_dir = Path("src/ai_presenter/presenter/skills")
    repo_skills = sorted(path.name for path in repo_skill_dir.glob("*.md"))
    packaged_skills = sorted(path.name for path in packaged_skill_dir.glob("*.md"))

    assert packaged_skills == repo_skills
    for name in repo_skills:
        assert (packaged_skill_dir / name).read_text(encoding="utf-8") == (
            repo_skill_dir / name
        ).read_text(encoding="utf-8")
```

- [ ] **Step 5: Run RED tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_config_loader.py::test_load_ringcentral_bind_speaker_profile tests\unit\test_presenter_context.py::test_load_presenter_context_reads_configured_soul_and_memory
```

Expected: the new and updated tests fail because `ringcentral-safety.md` is not configured and the packaged copy does not exist.

### Task 2: Lock Provider Prompt Inclusion

**Files:**
- Modify: `tests/unit/test_openai_provider.py`
- Modify: `tests/unit/test_codex_cli_provider.py`

- [ ] **Step 1: Add RingCentral safety marker to OpenAI prompt test**

In `test_narration_instructions_include_presenter_soul_and_memory`, add a second skill fixture:

```python
PresenterSkill(
    name="ringcentral-safety",
    content="Skill marker: recording and leave/end stay explain-only.",
),
```

Assert:

```python
assert "Presenter skill - ringcentral-safety:" in instructions
assert "Skill marker: recording and leave/end stay explain-only." in instructions
```

- [ ] **Step 2: Add RingCentral safety marker to Codex CLI prompt test**

In `test_codex_cli_prompt_includes_presenter_soul_and_memory`, add:

```python
PresenterSkill(
    name="ringcentral-safety",
    content="Skill marker: never read chat or participant names by default.",
),
```

Assert:

```python
assert "Presenter skill - ringcentral-safety:" in calls[0]["input"]
assert "Skill marker: never read chat or participant names by default." in calls[0]["input"]
```

- [ ] **Step 3: Run RED provider tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_openai_provider.py::test_narration_instructions_include_presenter_soul_and_memory tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_presenter_soul_and_memory
```

Expected: if the assertions are added with fixture skills, these tests may already pass because provider formatting is generic. This is acceptable for this task; the RED coverage for the feature comes from profile-loading tests in Task 1.

### Task 3: Create The Skill Markdown

**Files:**
- Create: `presenter/skills/ringcentral-safety.md`
- Create: `src/ai_presenter/presenter/skills/ringcentral-safety.md`

- [ ] **Step 1: Add the root skill**

Create `presenter/skills/ringcentral-safety.md` with a concise presenter skill that starts:

```markdown
# RingCentral Safety Skill

Use this skill when presenting RingCentral Video, answering questions about RingCentral Video controls, or deciding whether a visible RingCentral Video surface should be explained, opened, or left untouched.

You are a RingCentral Video safety guardian. Your job is to keep the demo useful without exposing private meeting content or creating unapproved meeting side effects.
```

Include sections for default policy, private surfaces, high-impact controls, cleanup, evidence language, and safe recovery.

- [ ] **Step 2: Add the packaged copy**

Create `src/ai_presenter/presenter/skills/ringcentral-safety.md` with identical content.

- [ ] **Step 3: Compare copies**

Run:

```powershell
Compare-Object (Get-Content 'presenter\skills\ringcentral-safety.md') (Get-Content 'src\ai_presenter\presenter\skills\ringcentral-safety.md')
```

Expected: no output.

### Task 4: Wire All RingCentral Profiles

**Files:**
- Modify: `profiles/ringcentral-video.yaml`
- Modify: `profiles/ringcentral-video-bind-speaker.yaml`
- Modify: `profiles/ringcentral-video-codex-cli-speaker.yaml`
- Modify: `profiles/ringcentral-video-openai.example.yaml`
- Modify: `profiles/ringcentral-video-piper-speaker.yaml`
- Modify: `src/ai_presenter/profiles/ringcentral-video.yaml`

- [ ] **Step 1: Add the skill path after live explainer**

In every listed profile, make the `skillPaths` block:

```yaml
  skillPaths:
    - ../presenter/skills/app-director.md
    - ../presenter/skills/live-explainer.md
    - ../presenter/skills/ringcentral-safety.md
```

- [ ] **Step 2: Run focused profile/context tests**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_config_loader.py::test_load_ringcentral_bind_speaker_profile tests\unit\test_presenter_context.py::test_load_presenter_context_reads_configured_soul_and_memory
```

Expected: both tests pass.

### Task 5: Verify And Review

**Files:**
- All changed files from Tasks 1-4

- [ ] **Step 1: Run focused provider/profile suite**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py::test_narration_instructions_include_presenter_soul_and_memory tests\unit\test_codex_cli_provider.py::test_codex_cli_prompt_includes_presenter_soul_and_memory
```

Expected: all selected tests pass.

- [ ] **Step 2: Run static checks**

Run:

```powershell
.\.venv\Scripts\ruff check --no-cache tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py tests\unit\test_codex_cli_provider.py
.\.venv\Scripts\mypy --no-incremental src\ai_presenter\runtime\presenter_context.py src\ai_presenter\config tests\unit\test_config_loader.py tests\unit\test_presenter_context.py tests\unit\test_openai_provider.py tests\unit\test_codex_cli_provider.py
```

Expected: ruff and mypy pass.

- [ ] **Step 3: Run full verification**

Run:

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests
.\.venv\Scripts\ruff check --no-cache .
.\.venv\Scripts\mypy --no-incremental src tests
git diff --check
```

Expected: all tests, ruff, mypy, and diff whitespace checks pass. Existing pywinauto STA warning may remain.

- [ ] **Step 4: Request review**

Dispatch a review subagent with:

- summary of changed files;
- spec and plan paths;
- focused and full verification output;
- request to check for prompt bloat, profile-copy drift, and accidental route-policy changes.
