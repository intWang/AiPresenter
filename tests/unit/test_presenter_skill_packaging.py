from pathlib import Path


def test_packaged_presenter_skill_copies_match_repo_skills() -> None:
    repo_skill_dir = Path("presenter/skills")
    packaged_skill_dir = Path("src/ai_presenter/presenter/skills")

    repo_skills = sorted(path.name for path in repo_skill_dir.glob("*.md"))
    packaged_skills = sorted(path.name for path in packaged_skill_dir.glob("*.md"))

    assert "ringcentral-safety.md" in repo_skills
    assert packaged_skills == repo_skills
    for name in repo_skills:
        assert (packaged_skill_dir / name).read_text(encoding="utf-8") == (
            repo_skill_dir / name
        ).read_text(encoding="utf-8")
