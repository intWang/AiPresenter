# Cycle 125 Demand Analysis: Spanish Alias Readiness Before Runtime Promotion

Date: 2026-05-17
Cycle: 125
Scope: demand analysis only. This handoff is the only file this subagent should edit. Do not modify package YAML, runtime code, tests, durable knowledge, generated artifacts, or prior handoffs in this analysis slice.

## 1) ç”¨æˆ·ä»·å€¼åˆ¤æ–­

Cycle 124 å·²æŠŠ `ringcentral-video` åŒ…å†…è¥¿è¯­ demo narration è¡¥é½åˆ° `51/51`ï¼Œè¥¿è¯­ Q&A ä¹Ÿä¿æŒ `12/12` questions å’Œ `12/12` answersã€‚å½“å‰æœ€é‡è¦çš„äº‹å®žæ˜¯ï¼šè¥¿è¯­å·²ç»æ˜¯ package-local å†…å®¹å®Œæ•´ï¼Œä½†è¿˜ä¸æ˜¯ runtime presenter è¯­è¨€ã€‚

å®žæµ‹ä¿¡å·ï¼š

- `localization-report --package ringcentral-video --language es` é€šè¿‡ï¼Œå¹¶æŠ¥å‘Šå››ä¸ª demo flow å…¨éƒ¨å®Œæˆã€‚
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` åŒæ—¶æŠ¥å‘Š `[OK] localization` å’Œ `[FAIL] runtime language support`ã€‚
- `questionAliases.es` ä»åªæœ‰ `1/27` entrypointsã€`3` aliasesã€‚
- `doctor` å·²ç»ä¼šæ£€æŸ¥ alias duplicateã€Q&A duplicateã€Q&A alias overlap å’Œ substring riskï¼›å½“å‰åŒ…å…±æœ‰ `90` package-owned aliasesã€`84` Q&A promptsï¼Œå¹¶æœ‰ä¸€ä¸ª INFO çº§ substring risk æ‘˜è¦ã€‚

å› æ­¤ï¼Œä¸‹ä¸€è½®æœ€é«˜ç”¨æˆ·ä»·å€¼ä¸æ˜¯ç«‹åˆ»å¯ç”¨ `--language es`ï¼Œè€Œæ˜¯å…ˆè¡¥é½è¥¿è¯­é—®é¢˜å…¥å£åˆ«åã€‚åŽŸå› ï¼š

- AI Presenter çš„æ ¸å¿ƒä»·å€¼ä¸æ˜¯åªä¼šæ’­æ”¾è„šæœ¬ï¼Œè€Œæ˜¯åœ¨æ¼”ç¤ºä¸­å›žç­”ç”¨æˆ·é—®é¢˜å¹¶æŠŠç”¨æˆ·å¸¦åˆ°æ­£ç¡®æŽ§ä»¶ã€‚è¥¿è¯­æ–‡æœ¬å·²å®Œæ•´ï¼Œä½†è‡ªç„¶è¥¿è¯­é—®é¢˜ä»å‡ ä¹Žæ— æ³•é€šè¿‡ package-owned aliases å‘½ä¸­ RingCentral Video æŽ§ä»¶ã€‚
- è¿è¡Œæ—¶å¯ç”¨ `es` çš„ blast radius æ˜Žæ˜¾æ›´å¤§ï¼šéœ€è¦ presenter language normalizationã€voice/provider routingã€`voices` catalogã€profile asset readinessã€controller language choicesã€doctor/CLI docsã€setup/runbook å’Œ live/manual acceptanceã€‚çŽ°åœ¨ alias è¦†ç›–åªæœ‰ `1/27`ï¼Œå…ˆå¯ç”¨ runtime ä¼šé€ æˆâ€œèƒ½é€‰æ‹©è¥¿è¯­ï¼Œä½†è¥¿è¯­æé—®è·¯ç”±å¾ˆè–„â€çš„ä½“éªŒå€ºã€‚
- alias æ‰©å±•æ˜¯ package-localï¼Œå¯æµ‹è¯•ã€å¯å›žæ»šã€å¯é€šè¿‡ doctor é£Žé™©æ£€æŸ¥å®ˆä½å®‰å…¨è¾¹ç•Œï¼›å®ƒæ˜¯ runtime promotion å‰æ›´å°ã€æ›´ç¨³çš„ä¸€å—åœ°åŸºã€‚
- RingCentral Video èµ„æ–™åŒ…æ²‰æ·€ä¹Ÿä¼šä»Ž alias æ‰©å±•ä¸­å—ç›Šï¼šæ¯ä¸ª entrypoint çš„å¯å‘çŽ°æ€§ä¼šæ›´æ˜Žç¡®ï¼ŒåŽç»­ runtime è¥¿è¯­ã€controller é—®ç­”ã€acceptance run éƒ½èƒ½å¤ç”¨è¿™äº›åŒ…å†…äº‹å®žã€‚

ç»“è®ºï¼šCycle 125 å»ºè®®åšâ€œSpanish questionAliases package-local expansionâ€ï¼Œå…ˆè¡¥è¥¿è¯­æŽ§ä»¶å®šä½/å‘çŽ°ç±» aliasesï¼Œä¸å¯ç”¨ runtime `es`ã€‚

## 2) å»ºè®®æœ¬è½®ç›®æ ‡

åœ¨ `packages/ringcentral-video.yaml` ä¸­æ‰©å±• `questionAliases.es`ï¼Œç›®æ ‡æ˜¯è®©è¥¿è¯­ç”¨æˆ·çš„æŽ§ä»¶å®šä½ç±»é—®é¢˜èƒ½å‘½ä¸­ RingCentral Video çš„å¸¸ç”¨å®‰å…¨å…¥å£ï¼ŒåŒæ—¶ä¿æŒ `demo --language es` ä¸æ”¯æŒã€‚

æŽ¨èèŒƒå›´ï¼š

- ä»¥æ—¥è¯­ alias çš„ä½Žé£Žé™©è¦†ç›–é¢ä¸ºæ¨¡æ¿ï¼Œå†ä¿ç•™çŽ°æœ‰è¥¿è¯­ background aliasesã€‚
- æ–°å¢žè¥¿è¯­ aliases åˆ°å®‰å…¨çš„ location/discovery entrypointsï¼Œä¾‹å¦‚ï¼š
  - `ringcentral.video.overview`
  - `ringcentral.video.top.meeting-info`
  - `ringcentral.video.top.network-quality`
  - `ringcentral.video.top.views`
  - `ringcentral.video.toolbar.audio`
  - `ringcentral.video.toolbar.audio-menu`
  - `ringcentral.video.toolbar.video-menu`
  - `ringcentral.video.toolbar.participants`
  - `ringcentral.video.toolbar.chat`
  - `ringcentral.video.toolbar.react`
  - `ringcentral.video.toolbar.raise-hand`
  - `ringcentral.video.more.recording`
  - `ringcentral.video.more.notes`
- ä¿ç•™çŽ°æœ‰ `ringcentral.video.settings.background` çš„ `es` aliasesï¼š`configuraciÃ³n de fondo`ã€`fondo virtual`ã€`desenfocar fondo`ã€‚

å»ºè®®å†™æ³•åŽŸåˆ™ï¼š

- aliases åªè¡¨è¾¾æŽ§ä»¶åã€ä½ç½®ã€å…¥å£ã€é¢æ¿ã€èœå•ã€çŠ¶æ€æŸ¥çœ‹ç­‰æ„å›¾ã€‚
- ä¸æŠŠâ€œè¯»å–å†…å®¹ã€å¤åˆ¶é“¾æŽ¥ã€å‘é€é‚€è¯·ã€å¼€å§‹å½•åˆ¶ã€ç¦»å¼€ä¼šè®®ã€å‘é€ reactionã€ä¸¾æ‰‹ã€åˆ‡æ¢éº¦å…‹é£Ž/æ‘„åƒå¤´ã€ä¿®æ”¹è®¾ç½®â€ç­‰åŠ¨ä½œåž‹è¯·æ±‚æ”¾è¿› aliasesã€‚
- å¯¹æ•æ„Ÿ entrypoints åªåŠ  location aliasesã€‚Recordingã€Meeting informationã€Notes/Transcript ä»åº”ä¾èµ– `questionPolicy: answerOnly` æˆ–æ—  `openSteps` æ¥é˜»æ­¢è‡ªåŠ¨æ“ä½œã€‚
- ä¿ç•™è‹±æ–‡ RingCentral UI label ä½œä¸ºè§†è§‰é”šç‚¹æ—¶å¯æ··å†™ï¼Œä¾‹å¦‚ `Meeting information`, `Network quality`, `Participants`, `Chat`, `Raise hand`, `Notes`ã€‚

å»ºè®®é¢„æœŸç»“æžœï¼š

- `questionAliases.es` ä»Ž `1/27` æå‡åˆ°ä¸€ä¸ªæ˜Žç¡®çš„å°åž‹å®‰å…¨è¦†ç›–é›†ï¼Œå»ºè®®ç›®æ ‡ä¸º `14/27` entrypointsï¼šä¸Šé¢ 13 ä¸ªæ–°å¢ž entrypoints åŠ çŽ°æœ‰ background entrypointã€‚
- alias æ€»æ•°ç”±å®žçŽ° subagent åœ¨é€‰å®šè¯è¡¨åŽå›ºå®šï¼Œå¹¶åœ¨æµ‹è¯•ä¸­ç²¾ç¡®æ–­è¨€ã€‚ä¸è¦åªå†™â€œå¤§äºŽæŸæ•°â€çš„æ¾æ•£æµ‹è¯•ã€‚
- è¥¿è¯­ demo/Q&A coverage ä¿æŒ `51/51`ã€`12/12`ã€`12/12`ã€‚
- è¥¿è¯­ runtime ä¿æŒ unsupportedã€‚

## 3) æ˜Žç¡®éžç›®æ ‡

æœ¬è½®ä¸è¦å¯ç”¨ `--language es`ï¼Œä¸è¦æŠŠ Spanish åŠ å…¥ presenter runtime language normalizationã€labelsã€controller language menuã€`voices` catalog æˆ– provider routingã€‚

æœ¬è½®ä¸è¦æ–°å¢žè¥¿è¯­ voice assetã€OpenAI/Windows SAPI/Piper è·¯ç”±ã€profile æ”¯æŒå£°æ˜Žã€README è¿è¡Œæ”¯æŒå£°æ˜Žã€live-ready å£°æ˜Žæˆ– acceptance è¯æ®ã€‚

æœ¬è½®ä¸è¦æ‰©å±•è¥¿è¯­ demo narration æˆ– Q&A æ­£æ–‡ï¼›è¿™äº›åœ¨ Cycle 124 å·²å®Œæˆåˆ° package-local completeã€‚

æœ¬è½®ä¸è¦æ–°å¢ž action/content aliasesï¼Œä¾‹å¦‚â€œlee el chatâ€, â€œcopia el enlaceâ€, â€œempieza a grabarâ€, â€œsal de la reuniÃ³nâ€, â€œenvÃ­a una reacciÃ³nâ€, â€œlevanta la manoâ€, â€œcomparte pantallaâ€ã€‚è¿™ç±»æ„å›¾åº”ç”± Q&A safety/routing å¤„ç†ï¼Œè€Œä¸æ˜¯ä½œä¸º entrypoint aliasã€‚

æœ¬è½®ä¸è¦æ”¹å˜ question matching é¡ºåºã€`questionPolicy` è¯­ä¹‰ã€`_can_operate(...)`ã€legacy aliasesã€openStepsã€locatorsã€cleanupã€demo flow é¡ºåºæˆ– action offsetsã€‚

æœ¬è½®ä¸è¦åš RingCentral live/manual acceptanceã€‚P0 live validation ä»æœ‰ä»·å€¼ï¼Œå°¤å…¶æ˜¯ controller queued Chat question å’Œ Add coworkers cleanupï¼Œä½†å®ƒæ˜¯å¦ä¸€æ¡éªŒè¯å·¥ä½œæµï¼Œä¸åº”å’Œè¥¿è¯­ alias æ‰©å±•æ··åœ¨ä¸€èµ·ã€‚

æœ¬è½®ä¸è¦é¡ºæ‰‹å¤§æ¸…ç† durable docsã€‚å¯ä»¥åœ¨å®žçŽ° handoff è®°å½•å‘çŽ°ï¼š`docs/knowledge/language-lifecycle.md` çš„ â€œCurrent Spanish Stateâ€ ä»æè¿° Cycle 123 partial stateï¼Œ`runtime-safety-routing.md` çš„ alias/Q&A counts ä¹Ÿå¯èƒ½éš Cycle 124 åŽå˜æ—§ã€‚é™¤éžä¸»ä¼šè¯æ˜Žç¡®è¦æ±‚ï¼Œå¦åˆ™ä¸è¦åœ¨ alias å®žçŽ°åˆ‡ç‰‡é‡Œæ”¹è¿™äº› evergreen docsã€‚

æœ¬è½®ä¸è¦ stage æˆ–æäº¤ `.coverage`ã€‚

## 4) éªŒæ”¶æ ‡å‡†

Package/localization éªŒæ”¶ï¼š

- `packages/ringcentral-video.yaml` åªå¢žåŠ  `questionAliases.es`ï¼Œä¸æ”¹å˜ demo narrationã€Q&A æ­£æ–‡ã€openStepsã€locatorsã€cleanupã€flowsã€profiles æˆ– runtime codeã€‚
- `localization-report --package ringcentral-video --language es` ä»æŠ¥å‘Šï¼š
  - `51/51` demo steps
  - `12/12` Q&A questions
  - `12/12` Q&A answers
  - æ›´æ–°åŽçš„ `questionAliases.es present on ...` ç²¾ç¡®è®¡æ•°
- `localization-report --package ringcentral-video --language es --require-complete` ä»é€šè¿‡ã€‚
- Chinese/Japanese strict reports ä»é€šè¿‡ï¼Œä¸”æ—¢æœ‰ `zh`ã€`ja` alias counts ä¸å› è¥¿è¯­å˜æ›´è€Œæ¼‚ç§»ã€‚

Runtime/lifecycle éªŒæ”¶ï¼š

- `demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run` ä»å¤±è´¥ï¼Œå¹¶åŒ…å« `Unsupported presenter language: es`ã€‚
- `doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es` ä» exit nonzeroï¼š`localization` ä¸º OKï¼Œ`runtime language support` ä¸º FAILã€‚
- ä¸å‡ºçŽ°ä»»ä½•æ–‡æ¡£æˆ– CLI è¾“å‡ºæš—ç¤º Spanish å·² runnableã€voice-readyã€controller-readyã€accepted æˆ– live-readyã€‚

Question routing/safety éªŒæ”¶ï¼š

- ä¸ºæ–°å¢žçš„è¥¿è¯­ aliases å¢žåŠ  focused testsï¼Œæ–­è¨€å…¸åž‹è¥¿è¯­ location/discovery é—®é¢˜èƒ½å‘½ä¸­å¯¹åº” entrypointã€‚
- å¯¹ Meeting informationã€Recordingã€Notes/Transcriptã€Leaveã€Shareã€Inviteã€Chatã€Participants ç­‰æ•æ„Ÿé¢ï¼Œæ–°å¢žæˆ–ä¿ç•™æµ‹è¯•è¯æ˜Žï¼š
  - location aliases å¯ä»¥åŒ¹é…æ­£ç¡® entrypointï¼›
  - action/content prompts ä¸ä¼šå› ä¸º alias æ‰©å±•å˜æˆå¯æ“ä½œä¸­æ–­ï¼›
  - `answerOnly` æˆ–æ—  `openSteps` çš„è¾¹ç•Œä»ç”Ÿæ•ˆã€‚
- `doctor` alias duplicateã€Q&A duplicateã€Q&A alias overlap ä¸æ–°å¢ž WARN/FAILã€‚è‹¥ INFO çº§ substring risk æ•°é‡å› é¢„æœŸ aliases å¢žåŠ è€Œå˜åŒ–ï¼Œæµ‹è¯•å¿…é¡»ç²¾ç¡®æ›´æ–°å¹¶è§£é‡ŠåŽŸå› ã€‚

è´¨é‡é—¨ï¼š

- è¿è¡Œ focused package/question/CLI/diagnostics testsã€‚
- è¿è¡Œ `git diff --check`ã€‚
- æ£€æŸ¥ `git status --short`ï¼Œç¡®è®¤åªæœ‰æœ¬è½®æŽˆæƒæ–‡ä»¶å’Œå®žçŽ°æ–‡ä»¶å˜åŒ–ï¼Œ`.coverage` æœª stagedã€‚

## 5) ç»™æŠ€æœ¯ subagent/ä¸»ä¼šè¯çš„äº¤æŽ¥æç¤º

ä½ æ˜¯ Cycle 125 æŠ€æœ¯/å®žçŽ° subagentã€‚è¯·æŠŠæœ¬è½®å½“æˆ package-local Spanish alias readinessï¼Œä¸è¦åš runtime Spanish promotionã€‚

å…ˆè¯»å–ï¼š

- `packages/ringcentral-video.yaml`
- `src/ai_presenter/runtime/questions.py`
- `src/ai_presenter/runtime/diagnostics.py`
- `src/ai_presenter/packages/localization_status.py`
- `tests/unit/test_material_packages.py`
- `tests/unit/test_questions.py`
- `tests/unit/test_cli.py`
- `tests/unit/test_diagnostics.py`
- `docs/knowledge/language-lifecycle.md`
- `docs/knowledge/ringcentral-video/runtime-safety-routing.md`
- `docs/knowledge/ai-presenter-maintenance.md`

å®žçŽ°æ–¹å‘ï¼š

- TDD-firstï¼šå…ˆæŠŠ Spanish alias report countã€å…¸åž‹ Spanish location promptsã€æ•æ„Ÿ prompt safety parity å†™æˆå¤±è´¥æµ‹è¯•ã€‚
- å†åœ¨ `packages/ringcentral-video.yaml` æ·»åŠ è¥¿è¯­ aliasesã€‚
- ä»¥æ—¥è¯­ alias è¦†ç›–é¢ä¸ºå®‰å…¨æ¨¡æ¿ï¼Œä½†ä¿ç•™çŽ°æœ‰è¥¿è¯­ background aliasesã€‚ç›®æ ‡å»ºè®®ä¸º `questionAliases.es` è¦†ç›– `14/27` entrypointsï¼Œæœ€ç»ˆ alias æ€»æ•°ç”±æµ‹è¯•ç²¾ç¡®é”å®šã€‚
- åªæ·»åŠ  location/discovery/control-name aliasesã€‚åŠ¨ä½œã€å†…å®¹è¯»å–ã€å¤åˆ¶ã€å‘é€ã€å¼€å§‹/åœæ­¢ã€ç¦»å¼€ã€çŠ¶æ€æ”¹å˜ç±»è¥¿è¯­è¡¨è¾¾ä¸è¦è¿› aliasesã€‚
- ä¸ä¿®æ”¹ runtime supported languagesï¼›`PresenterVoiceSettings(language="es")` ä»åº”æŠ›å‡º `Unsupported presenter language: es`ã€‚

æŽ¨èéªŒè¯å‘½ä»¤ï¼š

```powershell
.\.venv\Scripts\python -m pytest --override-ini addopts= -p no:cacheprovider -q tests\unit\test_material_packages.py tests\unit\test_questions.py tests\unit\test_cli.py::test_localization_report_outputs_complete_spanish_package tests\unit\test_cli.py::test_localization_report_require_complete_passes_for_spanish_package tests\unit\test_cli.py::test_demo_rejects_unknown_language_before_runtime tests\unit\test_cli.py::test_doctor_require_localization_accepts_package_only_spanish_language tests\unit\test_diagnostics.py
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language es --require-complete
.\.venv\Scripts\ai-presenter.exe doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --require-localization --localization-language es
.\.venv\Scripts\ai-presenter.exe demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language es --dry-run
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language zh --require-complete
.\.venv\Scripts\ai-presenter.exe localization-report --package ringcentral-video --language ja --require-complete
git diff --check
git status --short
```

ä¸»ä¼šè¯å†³ç­–å»ºè®®ï¼š

- è‹¥ç›®æ ‡æ˜¯ç»§ç»­è¯­è¨€æ‰©å±•ï¼šæ‰¹å‡† Spanish alias readinessã€‚
- è‹¥ç›®æ ‡æ˜¯æå‡ RingCentral live confidenceï¼šå¦å¼€ live/manual acceptance sliceï¼Œä¼˜å…ˆ controller queued Chat question æˆ– Add coworkers cleanupã€‚
- è‹¥ç›®æ ‡æ˜¯ repo knowledge hygieneï¼šå¦å¼€ docs-only slice æ›´æ–° language lifecycle/current counts/source indexã€‚ä¸è¦æŠŠå®ƒå¡žè¿› alias å®žçŽ°é‡Œã€‚
