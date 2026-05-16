# Cycle 055 Technical Scan

## Implementation Surface

- `packages/ringcentral-video.yaml`: add one `qa` item without `relatedEntrypointIds`.
- `src/ai_presenter/runtime/questions.py`: protect explicit entrypoint-title location questions from Q&A fragment matching.
- Unit tests cover behavior in `tests/unit/test_questions.py`, count assertions in package, diagnostics, and CLI tests.

## Prompt Set

- Primary: `Can AiPresenter send a reaction or raise my hand safely?`
- English alternates: thumbs-up reaction, raise hand for me, use reactions safely, handle raise hand.
- Chinese: `可以帮我发表情或举手吗`, `怎么安全使用举手和表情`.
- Japanese: `リアクションを送ったり手を上げたりできますか`.

## Count Deltas

- Q&A items: `11 -> 12`.
- Q&A prompt candidates: `63 -> 71`.
- Chinese Q&A coverage: `12/12`.
- Japanese Q&A coverage: `12/12`.
- Package-owned aliases remain `53`.

## Runtime Guard

The new safety item initially shadowed `Where is Raise hand?`. A guard now returns `None` from Q&A fragment matching when the user starts with `where is` or `where are` and names an entrypoint title, so entrypoint lookup can answer location questions.
