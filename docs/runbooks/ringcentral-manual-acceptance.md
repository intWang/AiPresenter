# RingCentral Manual Acceptance

## Preconditions

- `RingCentralDevelop` is installed, open, and already logged in.
- The profile `profiles/ringcentral-video.yaml` loads successfully.
- A virtual audio device such as VB-CABLE or VoiceMeeter is installed when testing virtual microphone output.
- In the RingCentralVideo executable directory, `config.ini` has `DisableAffinityMask=true` so meeting child
  windows can be captured reliably.

## Smoke Checklist

This uses the default fake providers. It verifies desktop automation, window binding, state detection, event filtering, and logging. It does not prove audible speech or OpenAI behavior.

- Before live route validation, open `docs/knowledge/ringcentral-video/validation-checklist-index.md` and choose the smallest target route group. Record any pass/fail evidence in `acceptance-runs.md`; runbook checkboxes are not acceptance evidence.
- To prepare a manual evidence draft without touching RingCentral, run `.venv\Scripts\ai-presenter acceptance-draft --package ringcentral-video --entrypoint ringcentral.video.main.add-coworkers`; complete the draft only after the actual manual run.

- [ ] Run `.venv\Scripts\ai-presenter run --profile ringcentral-video --dry-run` from the repo root.
- [ ] Run `.venv\Scripts\ai-presenter flows --package ringcentral-video` and confirm the scripted demo flow id before launch.
- [ ] Run `.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo`; if RingCentralVideo is not running, pass `--ringcentral-config "<RingCentralVideo>\config.ini"`.
- [ ] Run `.venv\Scripts\ai-presenter controller --profile ringcentral-video-bind-speaker --package ringcentral-video --flow missing-flow --dry-run`; verify the error says `Unknown demo flow: missing-flow` and lists available flows.
- [ ] Run `.venv\Scripts\ai-presenter voices` and confirm language and tone aliases are listed.
- [ ] Run `.venv\Scripts\ai-presenter voices --profile ringcentral-video-bind-speaker` and confirm English and Chinese routes are supported.
- [ ] Run `.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly` and confirm `[OK] voice: Chinese / Friendly supported via speech=windows-sapi-zh`.
- [ ] Run `.venv\Scripts\ai-presenter doctor --profile ringcentral-video-bind-speaker --language zh-CN --tone friendly` before a local Chinese-voice demo; when the Huihui SAPI voice is installed, confirm both `[OK] voice:` and `[OK] voice assets:`.
- [ ] Run `.venv\Scripts\ai-presenter demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language zh-CN --tone friendly --dry-run`; verify `Loaded voice: Chinese / Friendly`.
- [ ] Run `.venv\Scripts\ai-presenter controller --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language English --tone coach --dry-run`; verify `Loaded voice: English / Coach`.
- [ ] Verify regional language aliases such as `zh-CN` normalize to English/Chinese output families, and tone aliases such as `warm` or `mentor` normalize to the loaded voice label.
- [ ] Confirm voice preflight passes for a supported Chinese route: `.venv\Scripts\ai-presenter demo --profile ringcentral-video-bind-speaker --package ringcentral-video --flow meeting-control-map-demo --language zh-CN --dry-run`.
- [ ] Confirm voice preflight fails before launch for the fake speech profile: `.venv\Scripts\ai-presenter demo --profile ringcentral-video --package ringcentral-video --flow meeting-controls-tour --language zh-CN --dry-run`; verify the error names `speech provider fake` and `Chinese / Professional`.
- [ ] From another directory, run `<repo>\.venv\Scripts\ai-presenter run --profile ringcentral-video --dry-run`.
- [ ] Confirm the profile loads without validation errors.
- [ ] Open `RingCentralDevelop` and confirm the user is logged in.
- [ ] Run `.venv\Scripts\ai-presenter run --profile ringcentral-video --iterations 1`.
- [ ] Confirm the Video tab is selected.
- [ ] Confirm Start is clicked.
- [ ] Confirm `RingCentralVideo` starts.
- [ ] Confirm the runner binds a window with class `RingCentralVideoClass`.
- [ ] Confirm meeting joined state is detected only after in-meeting controls are visible.
- [ ] Toggle microphone and confirm one narration event.
- [ ] Toggle camera and confirm one narration event.
- [ ] Change participant count and confirm one narration event.
- [ ] Review logs for profile load, launch steps, binding, observations, events, narration generation, and media output status.

## Real Audio And OpenAI Checklist

This uses `profiles/ringcentral-video-openai.example.yaml`, which switches narration and speech to OpenAI while keeping RingCentral state recognition deterministic through the adapter.

- [ ] Set `OPENAI_API_KEY`.
- [ ] Set `AI_PRESENTER_OPENAI_NARRATION_MODEL`.
- [ ] Optionally set `AI_PRESENTER_OPENAI_TTS_MODEL`; when omitted, speech uses the built-in TTS model default.
- [ ] Confirm `profiles/ringcentral-video-openai.example.yaml` points `virtualMicDevice` to the installed virtual audio device.
- [ ] From the repo root, run `.venv\Scripts\ai-presenter run --profile profiles\ringcentral-video-openai.example.yaml --dry-run`.
- [ ] From the repo root, run `.venv\Scripts\ai-presenter run --profile profiles\ringcentral-video-openai.example.yaml --iterations 1`.
- [ ] Confirm local speaker playback contains audible presenter speech.
- [ ] Confirm RingCentral receives audio from the configured virtual microphone device.

## Controller Acceptance Checklist

This verifies the controller shell, target selection, text questions, voice controls, and quick scanning for apps that do not yet have a curated material package.

- [ ] Open controller and verify the Target section shows Material package mode.
- [ ] Verify the operator summary shows source, target, flow, voice, scan state, and question outcome.
- [ ] Open the controller with a local voice profile and confirm the operator summary includes
  `Voice assets: OK` before pressing Start. If assets are missing, confirm Start stays disabled
  and the summary names the missing SAPI or Piper requirement.
- [ ] Start `meeting-control-map-demo`, Pause, Resume, and End.
- [ ] While running, verify Start is disabled.
- [ ] While running, verify Refresh and Scan are disabled.
- [ ] Verify Pause and End enablement matches the running and ending states.
- [ ] Ask `What does Invite do?` and verify the answer area updates.
- [ ] Switch language to Chinese and ask `chat`; verify Chinese answer text.
- [ ] While `meeting-control-map-demo` is running, ask `chat`; verify the controller reports a queued safe demo and the original flow continues after Chat.
- [ ] Switch language to Chinese and ask `聊天在哪里`; verify the answer maps to Chat.
- [ ] Ask `怎么离开会议`; verify the controller answers only and does not click Leave.
- [ ] Switch tone to Conversational and verify the answer is warmer but still accurate.
- [ ] Switch to Running desktop app mode, refresh windows, select a harmless app, and scan.
- [ ] Before scanning a running app, verify question submit is disabled or blocked.
- [ ] Verify generated package status reports entrypoints.
- [ ] Ask about a safe visible control and verify answer plus safe action.
- [ ] Ask about a risky visible control and verify no click happens.
