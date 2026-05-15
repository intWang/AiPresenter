# Native Chinese Narration Design

## Goal

Make the RingCentral Video Chinese demo feel authored in Chinese instead of translated from the English script. The controller should use native Chinese narration text when the spoken language is Chinese, and local TTS should expose the small set of tone controls that Windows SAPI can reliably support.

## Current Problem

The material package stores one English narration string per step. `render_presenter_text()` currently performs a small replacement pass for Chinese, so the Chinese output keeps English sequencing, sentence shape, and presenter rhythm. The TTS provider can speak Chinese through Windows SAPI Huihui, but SAPI only supports practical controls such as voice, rate, and volume.

## Design

Add optional localized narration text to package narration blocks:

```yaml
narration:
  text: English source script.
  localizedText:
    zh: 原生中文讲稿。
```

Runtime narration selection will choose `localizedText[language]` when present, then apply the selected tone. English keeps the existing source text. Chinese native scripts will not receive the old English-word replacement pass.

For the first pass, add Chinese scripts to the `meeting-control-map-demo` flow, because it is the main controller demo flow the user is exercising. Keep the same safe UI operation order, but rewrite each spoken step in a natural Chinese product-demo style: short clauses, clear transitions, and explicit safety boundaries for risky controls.

Windows SAPI tone handling remains intentionally modest:

- Professional: default Huihui rate.
- Conversational: slightly slower and warmer pacing.
- Concise: slightly faster, with the first sentence selected where possible.

Higher expressive control should be handled later by a neural TTS profile, such as OpenAI `gpt-4o-mini-tts`, because that model supports promptable tone, speed, intonation, and emotional range.

## Testing

- Package model accepts `localizedText`.
- Chinese rendering uses localized text rather than English replacement.
- Concise Chinese rendering picks the first Chinese sentence.
- RingCentral `meeting-control-map-demo` has Chinese localized text for every step.
- Windows SAPI provider uses tone-specific rate through the speech provider factory path.
