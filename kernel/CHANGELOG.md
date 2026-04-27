# Kernel Changelog

Versioned history of the episteme kernel. The kernel is a contract;
changes to it are load-bearing for every adapter and every operator
profile downstream. This file is the audit trail.

Format: `[version] — date — change`. Versions follow semantic intent:
- **major** — a principle added, removed, or reframed.
- **minor** — a new artifact or schema field.
- **patch** — clarifications, attribution, boundary statements.

---

## [1.1.0-rc1](https://github.com/junjslee/episteme/compare/episteme-v1.0.0-rc1...episteme-v1.1.0-rc1) (2026-04-27)


### Features

* **0.10.0-alpha/1:** stateful interception — write-then-execute bypass closed ([73a66ab](https://github.com/junjslee/episteme/commit/73a66ab1205e40fce36f0d363f1637cf802b9f51))
* **0.10.0-alpha/2:** replace ASCII control-plane diagram with SVG ([b5ff678](https://github.com/junjslee/episteme/commit/b5ff67820507fbcb592974eecc677ea8bae63556))
* **0.10.0-alpha/3:** episteme evolve friction — heuristic telemetry analyzer ([0e0725b](https://github.com/junjslee/episteme/commit/0e0725ba0188f90fea40dd7ebbf71b024b967a32))
* **0.10.0-alpha/4:** last_elicited freshness gate + neutrality sweep + version reconcile ([abf5453](https://github.com/junjslee/episteme/commit/abf54539e4e887b246ad49982364ab5848b98545))
* **0.11-coherence:** demo_posture.sh — cinematic differential (75s) ([7a7be91](https://github.com/junjslee/episteme/commit/7a7be91fd991caf27c9afb6753aa499de9cdcc11))
* **0.11-phase-12:** checkpoint 1 — profile-audit scaffolding ([38374c0](https://github.com/junjslee/episteme/commit/38374c0df5aed245c8eda5fe2baaff3574220f08))
* **0.11-phase-12:** checkpoint 3 — Axis A dominant_lens (failure-first) ([83f28c3](https://github.com/junjslee/episteme/commit/83f28c3f4769dbfa476a9a5bc6579447e5904ba8))
* **0.11-phase-12:** checkpoint 4 — Axis D asymmetry_posture (loss-averse) ([7a0e38d](https://github.com/junjslee/episteme/commit/7a0e38d9fa505b5f179fc974b49b4b62fc8db3a1))
* **0.11-phase-12:** checkpoint 5 — Axis B noise_signature (status-pressure) ([7d9ef1f](https://github.com/junjslee/episteme/commit/7d9ef1f8e2899ce06172121c91fda4e47f1dfc78))
* **0.11.0-entry:** profile v2 axis sharpening + architecture svg render fix ([ff28dfb](https://github.com/junjslee/episteme/commit/ff28dfb889f82dd72a19e85bc4e8173bb698a9d0))
* **0.11.0:** phase 11 — semantic-tier promotion job ([a73ec05](https://github.com/junjslee/episteme/commit/a73ec056bc145b811cba604436de2a1a965e5a49))
* **0.11.0:** phase 9+10 landed — profile becomes control signal, memory becomes storage ([22b53db](https://github.com/junjslee/episteme/commit/22b53db148c696ed3fc5f0a85c45b05ddd613668))
* 0.5.0 — posture framing, marketplace install, differential demo, capture CLI ([62ea264](https://github.com/junjslee/episteme/commit/62ea264cca94ddd414c0312dc35b8ca18c56f61c))
* **0.8.1:** strict-by-default enforcement + semantic validator + bypass-resistant matching ([919cf34](https://github.com/junjslee/episteme/commit/919cf34ed789881f3d6ce5e0e9dfc7540edbba3a))
* **0.9.0-entry:** privacy scrub + calibration telemetry + visual demo + bypass hardening ([c4a87a7](https://github.com/junjslee/episteme/commit/c4a87a73f10529418bf81a459116e293f1640477))
* add deterministic workflow+cognitive profiling with infer/hybrid and tests ([423b3d8](https://github.com/junjslee/episteme/commit/423b3d8105ba7b32624fd20c1f70ab88bb58766f))
* add guided setup command for profile+cognition onboarding ([2338a2f](https://github.com/junjslee/episteme/commit/2338a2fe401e1432194b2da98466161693b89a81))
* add ontological agent roles and sharpen operating-system positioning ([65a7408](https://github.com/junjslee/episteme/commit/65a74089862ed4e060e672c837c296a8fb67491c))
* align philosophy contract across docs, adapters, and agents ([211e58c](https://github.com/junjslee/episteme/commit/211e58cb506e0a86be41e7ba8e515f40ff366e99))
* **brand:** integrate dragon mark — companion approach across READMEs + plugin manifests + favicon (Event 69) ([b13fffe](https://github.com/junjslee/episteme/commit/b13fffecc8768c50a03b3779fd0f09d9fbd4ccfb))
* **brand:** ship sage+dragonling pixel mark + SVG favicon ([e403f5f](https://github.com/junjslee/episteme/commit/e403f5f0b844fd1a36a963a847904709fcf6e161))
* broaden platform support to OMO/OMX and update animated visuals ([12fd908](https://github.com/junjslee/episteme/commit/12fd908ed6122a190b3cb9097317af07407c3864))
* constitution, opencode adapter, dynamic adapter registry, gap-survey protocol, and deep philosophy integration ([12a9ce3](https://github.com/junjslee/episteme/commit/12a9ce3bb6094f34ac6ac361922d4f96a49cb44f))
* **demo:** three-act v0.10.0 demo — posture, kernel remembers, kernel learns ([9cd1df3](https://github.com/junjslee/episteme/commit/9cd1df379e5881e03c3b397664418801ce4db13c))
* extract kernel/ as canonical markdown spec, lead README with kernel ([8fb56a5](https://github.com/junjslee/episteme/commit/8fb56a50324f45e2213a78d1643af9b87b8b7439))
* harness system — auto-provision project operating environments ([29d02bf](https://github.com/junjslee/episteme/commit/29d02bfdcd7d988df898c63e8e39224ea00f4ad3))
* **hooks,tools:** Path Y mid-soak fixes — CP-TEL-01 + CP-DEDUP-01 applied (Event 49) ([c7fdef0](https://github.com/junjslee/episteme/commit/c7fdef0085f26211a1a33c41977448eb00f66dc1))
* **hooks,tools:** Path Y mid-soak fixes (Event 49) ([8e894d9](https://github.com/junjslee/episteme/commit/8e894d9d274ec692ebc63694d12adf5ddc754ea7))
* **hooks:** Frame-stage advisory footer for preferred_lens_order + explanation_form ([e66abe9](https://github.com/junjslee/episteme/commit/e66abe95f8e32243a123670b366645f39ee499c7))
* **hooks:** SessionStart surfaces noise_watch_set derived knob ([a8d83d6](https://github.com/junjslee/episteme/commit/a8d83d637397bb28a5ecbabd312aaf7c19bc04c3))
* improve setup wizard defaults and split profile/cognition answer files ([1c6defd](https://github.com/junjslee/episteme/commit/1c6defdc7cf3fc35b809abb5ca949781936b5e32))
* **logo:** pixel-art dragon mark candidates — 6 SVG variants + conversion script (Event 68 commit 2/2) ([9bd1f13](https://github.com/junjslee/episteme/commit/9bd1f13d4415ff539a8662258826fb12e464300b))
* **memory:** append rule-shape rule to agent_feedback.md ([d326126](https://github.com/junjslee/episteme/commit/d32612680da3747439204ea0f83f92357f6132e3))
* **memory:** promote agent-learned feedback to global via agent_feedback.md ([b995be0](https://github.com/junjslee/episteme/commit/b995be055e4f7a046d2b2dcbba36951ff43283ca))
* publish clean contract names and remove product audit artifact ([9b65026](https://github.com/junjslee/episteme/commit/9b650265e8437af7c13e33c0d4c5a166cb234d3b))
* publish personal profiles, reorganize examples, update init path ([a0e5e73](https://github.com/junjslee/episteme/commit/a0e5e7366a7f575ebccd48c3711c17603c505d56))
* publish-ready structure with harness, Hermes sync, and init command ([7fd8178](https://github.com/junjslee/episteme/commit/7fd81783711d05529cbebc871b8bdec3ad6cd258))
* **readme:** add clone-count badge backed by MShawon gist action ([e15f92f](https://github.com/junjslee/episteme/commit/e15f92f26f2f01e658689bac46d558c2b95e8148))
* repositioning and bridge implementation ([1fb472f](https://github.com/junjslee/episteme/commit/1fb472f90bbdff4e7a9004b57c6be0f6f3a641df))
* **setup+docs:** synthesize soul-aware onboarding with deterministic clarity ([9e18b2a](https://github.com/junjslee/episteme/commit/9e18b2afe25cb3a691143641e385e4473089d676))
* **v1.0-rc:** complete implementation arc · kernel update · demo assets sync ([f7c7e6c](https://github.com/junjslee/episteme/commit/f7c7e6cf496f1b13cb15b6d5b2e62b32b6999978))
* **v1.0-rc:** CP10 Blueprint D (Architectural Cascade & Escalation) scaffolding + cascade detector + kernel-state exemption from live dogfood ([fb37044](https://github.com/junjslee/episteme/commit/fb37044733f426b1f0ba39408ea15f46d54dc71c))
* **v1.0-rc:** CP3 Layer 2 classifier in the hot path, blueprint-aware ([101d3cd](https://github.com/junjslee/episteme/commit/101d3cdba57f1a3a6f61b22d3af19388866ea29b))
* **v1.0-rc:** CP4 Layer 3 contextual grounding, blueprint-aware ([2558c67](https://github.com/junjslee/episteme/commit/2558c67d8e6dd191fed404ed3bd1013ce2c69cee))
* **v1.0-rc:** CP5 Blueprint B (Fence Reconstruction) end-to-end + first Pillar 3 synthesis output ([117fa69](https://github.com/junjslee/episteme/commit/117fa6907440981bd25e949e92e893279f3ff474))
* **v1.0-rc:** CP6 Layer 4 verification_trace schema + close fluent-vacuous gap ([fb09b0a](https://github.com/junjslee/episteme/commit/fb09b0a4bb3d161c08111405fbb3fab5a7dce7ed))
* **v1.0-rc:** CP7 Pillar 2 hash chain + Pillar 3 substrate + retroactive CP5 upgrade ([086c10a](https://github.com/junjslee/episteme/commit/086c10ab895e637b8fb73a5eb4005a24bfd0269a))
* **v1.0-rc:** CP8 Layer 8 spot-check sampling + episteme review CLI + SessionStart digest ([a1156c2](https://github.com/junjslee/episteme/commit/a1156c2be4560fede5a17da22073a6a879d3308c))
* **v1.0-rc:** CP9 Pillar 3 active guidance surface + episteme guide CLI + SessionStart framework digest ([78c271f](https://github.com/junjslee/episteme/commit/78c271fbc24cda04250d439f1363444a98dbb303))
* **web,readme,ci:** Events 34+35 — Korean README + release-please automation + v1.0.1 Chain Hygiene CP update (Path-A prep batch) ([27653df](https://github.com/junjslee/episteme/commit/27653dfc9e1be1fba7bf7adcd1ab86651e768c34))
* **web,readme:** Korean storytelling rewrite + Spanish + Chinese READMEs + /readme/{es,zh} routes (Event 40) ([de76b42](https://github.com/junjslee/episteme/commit/de76b423771c227c530734def76b953d37e20cb3))
* **web,readme:** soften top-of-page tone — broaden high-impact scope + acknowledge agent-validates-request ([0405495](https://github.com/junjslee/episteme/commit/0405495edb176d5e52ff5a1727cc490ad37a7c46))
* **web,readme:** wire epistemekernel.com as canonical domain ([4c59d87](https://github.com/junjslee/episteme/commit/4c59d8782bbcad4fc964dd31166f5c205479f1cb))
* **web:** auto-render docs/COMMANDS.md at /commands ([fe5088e](https://github.com/junjslee/episteme/commit/fe5088e955bed698ce67a13b5c8b79b254d93e5a))
* **web:** Header anchor-tab visual distinction + close NEXT_STEPS items 8 + 9 ([cdd548c](https://github.com/junjslee/episteme/commit/cdd548c244c11ab276429bffcc671ccc95c7c7bf))


### Bug Fixes

* **1.0-rc:** pytest config, telemetry redaction, Windows fcntl fallback ([d3cf98f](https://github.com/junjslee/episteme/commit/d3cf98fd2e3428a5aca1ac876c8c1725ca4c3016))
* **1.0-rc:** RC-cycle items 7, 8, 11 — episode id, top-n clamp, malformed-surface signal ([9a7cd1b](https://github.com/junjslee/episteme/commit/9a7cd1b883671f3576284a51f8e69a490305c3cb))
* **adapter:** register 4 PostToolUse Bash hooks in build_settings() — opens fresh soak (Path-A Event 38) ([2ec8151](https://github.com/junjslee/episteme/commit/2ec81514aec9c9f2561a56905721b160fa94d262))
* **ci/hooks:** release-please PR permissions and root-path canonicalization (Event 42) ([6f3968e](https://github.com/junjslee/episteme/commit/6f3968e71968e0cecdc4ce8fd58933eeb2135f93))
* close the harness loop — agents now read HARNESS.md at runtime ([7dd9b44](https://github.com/junjslee/episteme/commit/7dd9b4451a8f8686715b9ff086cb5626d3a18c6d))
* declare swing-mortem in vendor_skills manifest ([16c0221](https://github.com/junjslee/episteme/commit/16c022149e03c651efcc4f09a37a0ff5074fabb4))
* **hooks:** CP-FENCE-02 correlation-id dual-write + fallback (Event 50) ([301dc8d](https://github.com/junjslee/episteme/commit/301dc8d5e337e50e8c64bfb630e40440cdea0008))
* **hooks:** CP-FENCE-02 correlation-id dual-write + fallback (Event 50) ([dec257e](https://github.com/junjslee/episteme/commit/dec257e00bbb23275cdde58555ca250f184de974))
* **hooks:** loud-failure-mode logging for PostToolUse async hooks (Path-A Event 36) ([a92fce1](https://github.com/junjslee/episteme/commit/a92fce168ff6070a09e2eea5aa1c00272fc23166))
* **hooks:** loud-failure-mode logging on state_tracker + calibration_telemetry (Event 39 — Event 36 follow-up) ([96a2d88](https://github.com/junjslee/episteme/commit/96a2d88722924a6be43055338dc8dcc481bc01cf))
* install pytest in CI environment ([c453cbe](https://github.com/junjslee/episteme/commit/c453cbe32d8ceb8c67c9db7309b1152885b853e1))
* **marketplace:** align manifest shape with strict `claude plugin validate` ([d8ea852](https://github.com/junjslee/episteme/commit/d8ea8524646f42f993a058f26d85e5916c6c12da))
* **plugin:** correct agents field shape + reconcile version to v1.0.0-rc1 (fixes [#1](https://github.com/junjslee/episteme/issues/1)) ([0c27d9c](https://github.com/junjslee/episteme/commit/0c27d9ce4150cbd025cd3ed30ddf0a3304c16e4b))
* **plugin:** remove hooks field — resolves duplicate-load on /plugin install ([b0c166c](https://github.com/junjslee/episteme/commit/b0c166cc8dd31c23ad504ec157dde78bcbbad1fb))
* posture_demo ([f11bd27](https://github.com/junjslee/episteme/commit/f11bd27366e7a2747edf739e6749dcf23e9d2e58))
* resolve CI failures, update Node actions, and fix broken imports ([0616c4d](https://github.com/junjslee/episteme/commit/0616c4d6a83f4cfc2d7f17e348e4945e387a9337))
* **v1.0-rc:** pytest pythonpath includes repo root for core.hooks ([2a2ed68](https://github.com/junjslee/episteme/commit/2a2ed68d44494e2ab234a90881a479beebe5a751))


### Documentation

* **0.11-coherence:** align PROGRESS / PLAN / NEXT_STEPS ([9598d6a](https://github.com/junjslee/episteme/commit/9598d6ad5dfba66150980cc09bb51929216a2b40))
* **0.11-coherence:** design spec for visual + narrative coherence pass ([47d147a](https://github.com/junjslee/episteme/commit/47d147a6360f413e23f12f5ea4466c738378995d))
* **0.11-coherence:** Figure 1 — system-overview.svg in arxiv style ([ca10718](https://github.com/junjslee/episteme/commit/ca10718a6b0cd9f264ebe4047dca1e2408bf930b))
* **0.11-coherence:** Figure 2 — architecture_v2.svg in arxiv style ([ccd0caf](https://github.com/junjslee/episteme/commit/ccd0caf312127c5a40b4b91cc03426c253cf0b9f))
* **0.11-coherence:** NARRATIVE.md — doxa/episteme/praxis spine + 결 (gyeol) ([c89cec8](https://github.com/junjslee/episteme/commit/c89cec8371c77f0895745428fb3560ae4bb7d027))
* **0.11-coherence:** README — lead with posture-as-thinking ([665c215](https://github.com/junjslee/episteme/commit/665c2151e43ce9694255b65fc8b77d47e829ddf2))
* **0.11-coherence:** record posture_demo.gif ([ddbf762](https://github.com/junjslee/episteme/commit/ddbf76253a952ed51a60a12646e397103362e626))
* **0.11-phase-12:** approved design spec for profile-audit loop ([9c26201](https://github.com/junjslee/episteme/commit/9c2620128f55a097216934878075dd3d9937793a))
* **1.0-rc:** reframe lede — thinking framework is the product, blocker is enforcement ([b008b3e](https://github.com/junjslee/episteme/commit/b008b3ed859896d4753a52969a2d7529df9e66ac))
* add command cheat sheet and improve doctor troubleshooting tips ([f9ddb11](https://github.com/junjslee/episteme/commit/f9ddb1179eda92415079a887014dbf33ba990591))
* add front-page system diagram for architecture at a glance ([b658407](https://github.com/junjslee/episteme/commit/b658407e6536decb8c08f7302106ab454be5e7bf))
* add setup demo gif and clarify canonical-memory value ([c61f1b5](https://github.com/junjslee/episteme/commit/c61f1b59bfc035913318a6692029d0cf08c778e1))
* add strict mode block demo gif ([c4111c5](https://github.com/junjslee/episteme/commit/c4111c594449262892f600e59110d4d8c6e2f080))
* consolidate cognitive setup, fix duplicate bloat, audited by hermes ([e413065](https://github.com/junjslee/episteme/commit/e41306569103dc8fd89d6bc44e0100fe2d589d9f))
* expand front-page diagram to full cognitive-os workflow and file map ([20c1f84](https://github.com/junjslee/episteme/commit/20c1f84e7db00831dd2bf87fc9339bbf47db2115))
* extend epistemic-trust vocabulary to English README + cite paper in REFERENCES.md (Event 44) ([fa7a055](https://github.com/junjslee/episteme/commit/fa7a0553fb9bd933cb2c2e258823eb1d1f4afb83))
* extend epistemic-trust vocabulary to English README + cite paper in REFERENCES.md (Event 44) ([19e3b59](https://github.com/junjslee/episteme/commit/19e3b59c67b465854bf94043c7cd866cc4847380))
* fix Mermaid parse error and switch overview image to GIF ([da19ca4](https://github.com/junjslee/episteme/commit/da19ca485c7bb2a462e77c87554fa0f930ecbdb0))
* fix README integrity, add system visual, and update tool guidance ([8299a60](https://github.com/junjslee/episteme/commit/8299a60de48c2666c0192d66a33fb9094faf111a))
* **governance:** always-clean-master Git workflow protocol (Event 57) ([d67e407](https://github.com/junjslee/episteme/commit/d67e40720a161b750007001a8aa1d24a66d4810f))
* **governance:** always-clean-master Git workflow protocol (Event 57) + Event 56 approval rescue ([5d9f0c8](https://github.com/junjslee/episteme/commit/5d9f0c8a43415ae3e62cfdc4a21bbe46232db479))
* **governance:** protocol refinement · sync-order + Path B caveat + branch-deletion footgun (Event 61) ([ac98c0b](https://github.com/junjslee/episteme/commit/ac98c0b56a2480f84057cde75d23379e73240c51))
* **governance:** protocol refinement · sync-order + Path B caveat + branch-deletion footgun (Event 61) ([8a2b048](https://github.com/junjslee/episteme/commit/8a2b04865dd2417ccaeee993da61a9a73afb58b7))
* **handoff:** refresh NEXT_STEPS Resume-here date + So-What-Now line ([611a6b6](https://github.com/junjslee/episteme/commit/611a6b64ad046bf86926f967f637a836ac030236))
* **handoff:** refresh NEXT_STEPS Resume-here for clean mid-soak cold-start ([a5b1a74](https://github.com/junjslee/episteme/commit/a5b1a74288f0cbb3148566fecde3014ad8669696))
* INSTALL.md §4 first-run + docs/ consolidation (Event 54) ([00881a3](https://github.com/junjslee/episteme/commit/00881a3ccbe3403a3c9a7137ba470506e4d040cb))
* INSTALL.md §4 first-run + docs/ consolidation (Event 54) ([2539359](https://github.com/junjslee/episteme/commit/25393599d9a4862421f1415fc5b9ea73a34821df))
* **kernel:** Pearl honest translation note in REFERENCES.md ([b603685](https://github.com/junjslee/episteme/commit/b60368529847665d5da06904b1c2e27ce95c46d3))
* **kernel:** SUMMARY Blueprint D mention + log Hybrid-C decision in NEXT_STEPS ([e55705f](https://github.com/junjslee/episteme/commit/e55705f5e64e010ab6b4d60d63e037e95a2a5e4c))
* **kernel:** Two-vocabulary distinction section resolves Gate 27 (Path-A Event 37) ([eca946f](https://github.com/junjslee/episteme/commit/eca946f45de8f14f4403f229198174f16b20b002))
* Langfuse v3.170.0 adjacent-ecosystem appendix (Event 52) ([9edb1dc](https://github.com/junjslee/episteme/commit/9edb1dcc46617ad24922077181e488cc8fa37cab))
* Langfuse v3.170.0 adjacent-ecosystem appendix (Event 52) ([5b5a32e](https://github.com/junjslee/episteme/commit/5b5a32eb639e4ca454eb799535960ac38b4b7ea1))
* log 0.8.0 episteme migration in PROGRESS + NEXT_STEPS ([6398258](https://github.com/junjslee/episteme/commit/6398258258093f6ad816ee2925489b625087c030))
* **next-steps:** align with Phase A completion + stage Phase B/C ([a61bbc8](https://github.com/junjslee/episteme/commit/a61bbc8287dc82a7178590672ece353c2ac22829))
* **next:** queue v1.0.1 CP — deferred-discovery chain hygiene ([27af7a0](https://github.com/junjslee/episteme/commit/27af7a075ee3c5cce4942ed50120e4661b880308))
* **policy:** add Doc classification policy to AGENTS.md (Event 66 follow-up) ([6ff26b2](https://github.com/junjslee/episteme/commit/6ff26b2dbb9a44e472da7da754a2bc58aa8444d9))
* post-soak triage rubric (Event 46) ([f247095](https://github.com/junjslee/episteme/commit/f24709550054fc588eaad55f3babda4ff8c4693f))
* post-soak triage rubric (Event 46) ([a21fe97](https://github.com/junjslee/episteme/commit/a21fe97081574bef464034262ee8b650019dc2d2))
* post-v1.0 branched roadmap (Event 51) ([917bb45](https://github.com/junjslee/episteme/commit/917bb458bce054fb7848142618caeb4832f1fe3f))
* post-v1.0 branched roadmap + Hermes lessons (Event 51) ([a854a0c](https://github.com/junjslee/episteme/commit/a854a0cd6473fe885c4b39a689411eedf5f1f99c))
* **privatize:** move v1.1+ strategic docs to private staging (Event 65 commit 1/2) ([2798918](https://github.com/junjslee/episteme/commit/2798918d4ef2978cce092d7fd08d57f3f0cad027))
* **privatize:** Tier 1 + Tier 2 doc privatization + governance rewrites (Event 66) ([445b85f](https://github.com/junjslee/episteme/commit/445b85ff89ae67584ca4a8a893efc9e5f92fe6bf))
* **profile:** re-elicit asymmetry_posture with Events 65-67 evidence (Event 68 commit 1/2) ([e413df3](https://github.com/junjslee/episteme/commit/e413df3bb5eb675ec150e27f5d118279955dbfd2))
* **progress:** Event 25 — v1.0.0-rc1 tagged · Vercel deploy · RC soak opens ([eccae8b](https://github.com/junjslee/episteme/commit/eccae8b30905e64a7151e273601a392cd4c9dcbf))
* rasterize arxiv figures to PNG for deterministic README rendering ([1757ae6](https://github.com/junjslee/episteme/commit/1757ae683433e0348db1a0292c856887712de5da))
* **readme:** add ABCD architecture section above the fold ([b52c42e](https://github.com/junjslee/episteme/commit/b52c42e104c0ef010434fa9472254732e00eb9ce))
* rebalance system visual aspect and switch Mermaid to horizontal layout ([9c59b46](https://github.com/junjslee/episteme/commit/9c59b46a9e3513ba4a4a91d1887c4e74fc2e30a7))
* reconcile kernel CHANGELOG + PLAN + NEXT_STEPS with 0.8.0 reality ([a54fe1b](https://github.com/junjslee/episteme/commit/a54fe1bc4ba2ba2ecdda15d63f29a14f2bc1ffa1))
* record environment-side migration (pip, shell, settings.json) ([4783e41](https://github.com/junjslee/episteme/commit/4783e41358adc82a4f5d926c67d2c1d943776b1c))
* redesign front system map, update repo links, and clean demo GIF chrome ([945293d](https://github.com/junjslee/episteme/commit/945293d6ae22fcd43a8011d9a57041b49dfae260))
* refresh system overview visual and revamp setup demo GIF ([006427e](https://github.com/junjslee/episteme/commit/006427e26154f14ceb1fcddd3feeb41e9aaa0703))
* regenerate SVG with proper multi-platform layout and no text overflow ([91266be](https://github.com/junjslee/episteme/commit/91266becd51bc86af4f12a4c0adbf6a1e5aa615e))
* replace old gifs with animated svgs mirroring terminal design ([b4d6ae2](https://github.com/junjslee/episteme/commit/b4d6ae2fb7bfbc5da5ecaf428c126c2a63d48d18))
* restore repo URLs back to cognitive-os ([56c6952](https://github.com/junjslee/episteme/commit/56c69523637e839818a8387c187428a3aca6d4d2))
* rewrite README to center on the Thinking Framework and Protocol Synthesis ([23abc0a](https://github.com/junjslee/episteme/commit/23abc0ac66c8d761f3b042030082bca255c2d2cf))
* roadmap audit — remove LLM-as-judge + web-dashboard (Event 53) ([b751def](https://github.com/junjslee/episteme/commit/b751defaf12a8029192ed38913dfe0df52f54a01))
* roadmap audit — remove LLM-as-judge + web-dashboard (Event 53) ([70fbd3a](https://github.com/junjslee/episteme/commit/70fbd3a8c15c1e58b9ebcbd4ff4f57fd9a95af45))
* session handoff — log 2026-04-20 work, point resume at Phase 12 CP2 ([dfb83ce](https://github.com/junjslee/episteme/commit/dfb83ce5276cf0f03c2a5d0c8ab3ef6206b7b35d))
* **strategy:** §8 adjacent-ecosystem scan 3 · alex-core-invariants + system_prompts_leaks + tolaria (Event 62) ([6933fcc](https://github.com/junjslee/episteme/commit/6933fcc08355fb07f14ff981d132f4031b9107b3))
* **strategy:** §8 adjacent-ecosystem scan 3 · alex-core-invariants + system_prompts_leaks + tolaria (Event 62) ([e178dc3](https://github.com/junjslee/episteme/commit/e178dc325b279609f5c1b2870474fc582199db74))
* **strategy:** CP-EPISODIC-OUTCOME-01 added to Theme 1 (Event 63) ([e494340](https://github.com/junjslee/episteme/commit/e49434027b279cb68dbfff99dc26c4440b05a4fc))
* **strategy:** CP-EPISODIC-OUTCOME-01 added to Theme 1 (Event 63) ([b1e5c07](https://github.com/junjslee/episteme/commit/b1e5c075c62cedb8912b7169f101c13cbede5fdb))
* **strategy:** post-soak migration plan + product protection strateg… ([d372137](https://github.com/junjslee/episteme/commit/d3721375d4b54b7dcd2d8e5aca4d4a95866d8f8d))
* **strategy:** post-soak migration plan + product protection strategy (Event 58) ([25715b7](https://github.com/junjslee/episteme/commit/25715b7ab8992a91542badcda468a2173c94bff7))
* **strategy:** Section K reference anchor expansion · Peirce/Engelbart/Bender/Heidegger (Event 60) ([190556f](https://github.com/junjslee/episteme/commit/190556f6e595467e90a193f4ff30c55eee5b1985))
* **strategy:** Section K reference anchor expansion · Peirce/Engelbart/Bender/Heidegger (Event 60) ([e0a5c21](https://github.com/junjslee/episteme/commit/e0a5c21bba5886ff0a676c6b2d33c0c567da1cc6))
* **strategy:** stage AGPL-3.0 LICENSE + migration §J + commercial footer (Event 59) ([ae149bc](https://github.com/junjslee/episteme/commit/ae149bc35b4ecb758ad67310bd86d0165a9d5ed0))
* **strategy:** stage AGPL-3.0 LICENSE + migration §J + commercial footer (Event 59) ([78aa26d](https://github.com/junjslee/episteme/commit/78aa26d2b1e9515411a708c6f819c9f33c41b7aa))
* unify top-level value proposition into one concise statement ([8530668](https://github.com/junjslee/episteme/commit/853066829d7a9249d046b5c79da827f667f917b3))
* **v1.0-rc:** sync PLAN/PROGRESS/NEXT_STEPS for CP4 + fold rebase-SHA + dedupe cleanups ([b9bb1ee](https://github.com/junjslee/episteme/commit/b9bb1eecb0568cb290564eb763912e25990e871a))
* **v1.0-rc:** sync PLAN/PROGRESS/NEXT_STEPS for CP5 — Fence Reconstruction end-to-end ([91c9965](https://github.com/junjslee/episteme/commit/91c99653aca8e59c48114f7b0f81742fa5aaf5e5))
* **v1.0-rc:** sync PLAN/PROGRESS/NEXT_STEPS for Event 10 GTM README realignment ([636ad53](https://github.com/junjslee/episteme/commit/636ad53efdda794e642cb2ee482d8ec51e552a38))
* **v1.0:** approve semantic-governance spec — eight-layer spiderweb for the Reasoning Surface Guard ([7492894](https://github.com/junjslee/episteme/commit/7492894d7a193cbb1481e6718a310f20ff66ef29))
* **vision:** operator approved v1.1 spec with 3 Cognitive Arms and D11 fatigue guard ([ac7bf7d](https://github.com/junjslee/episteme/commit/ac7bf7d5910035969cc7ee31541075a379c7a3af))
* **vision:** v1.1+ roadmap — Protocol Decay, Causal Clustering, and … ([f5b145d](https://github.com/junjslee/episteme/commit/f5b145d82c1f64b26b93c36a7c29ee18cfe4d46a))
* **vision:** v1.1+ roadmap — Protocol Decay, Causal Clustering, and the Proactive Reasoning Engine ([d62f374](https://github.com/junjslee/episteme/commit/d62f374baf44ea483f063153d0e5cd17452c6fbc))

## [Unreleased] — v1.0.0 RC cycle open (2026-04-21)

v0.11.0 has been tagged and shipped. The v1.0 RC cycle is open. The approved spec is `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md` — *Design — Causal-Consequence Scaffolding & Protocol Synthesis — v1.0 RC*, status `approved (reframed, third pass)`. Three reframes on 2026-04-21 took the spec from v0.11.0's retrospective audit loop to a forward-looking architecture grafting four jobs onto the LLM substrate: per-action causal-consequence decomposition, per-case context-fit protocol synthesis, active operator guidance at future decisions, and continuous architectural self-maintenance.

- **Pillar 1 · Cognitive Blueprints** — scenario-polymorphic Reasoning Surface schemas. Four named blueprints (Axiomatic Judgment, Fence Reconstruction, Consequence Chain, Architectural Cascade & Escalation) + generic maximum-rigor fallback for unclassified high-impact ops. Blueprint D is the self-maintenance engine — fires when the agent discovers a flaw, vulnerability, stale artifact, config gap, or core-logic drift; forces patch-vs-refactor evaluation, symmetric cascade synchronization across the full blast radius (CLI / config / schemas / visualizations / docs / tests / generated artifacts / external surfaces), and continuous digging & logging of adjacent discoveries.
- **Pillar 2 · Append-Only Hash Chain** — tamper-evident SHA-256 chain across episodic, pending-contracts, and framework (protocols + deferred-discoveries) streams. Closes the memory-poisoning doxa class.
- **Pillar 3 · Framework Synthesis & Active Guidance** — context-indexed protocols synthesized by Pillar-3-capable blueprints, hash-chained, surfaced as advisory operator guidance at future matching decisions. Advisory, never blocking — collapsing into enforcement would produce a feedback loop where the kernel enforces its own synthesis against the operator.
- **BYOS** — bring-your-own-skill stance enshrined. No tool-specific validation paths; no prescriptive tool-usage in blueprints. The ecosystem provides the skills; the kernel provides the episteme.
- **Two new failure modes** registered: #10 framework-as-Doxa (synthesized protocols re-introducing the averaging the scaffold was built to resist); #11 cascade-theater (Blueprint D's `blast_radius_map[]` padded with `not-applicable` entries). Countermeasures landed in `KERNEL_LIMITS.md` (limits 9–11) and `FAILURE_MODES.md` (modes 10–11).
- **10 CPs** to land: CP1 extracts `_specificity.py`; CP2–CP4 add the scenario detector, blueprint registry, and Layers 2+3 hot-path integration; CP5 ships Blueprint B (Fence Reconstruction) end-to-end including first framework synthesis output; CP6 adds Layer 4 `verification_trace` schema; CP7 lands Pillar 2 hash chain + Pillar 3 substrate; CP8 adds spot-check sampling; CP9 wires the active-guidance query; CP10 scaffolds Blueprint D (cascade detector + structural validation + hash-chained deferred-discovery writes).
- **CP1 — in progress (this session).** `_classify_disconfirmation` + three pattern tuples + `DisconfirmationClass` type alias moved from `src/episteme/_profile_audit.py` to new `core/hooks/_specificity.py`. Phase 12 re-imports via `sys.path` injection (behavior unchanged). Test suite 304/304 green.
- **Blueprint-D self-dogfood** — this session is the kernel satisfying Blueprint D on itself. CP1 + a symmetric cascade sync across eight named documentation surfaces (NARRATIVE, POSTURE, REASONING_SURFACE, MEMORY_ARCHITECTURE, kernel/README, KERNEL_LIMITS, ARCHITECTURE, COGNITIVE_OS_ARCHITECTURE → EPISTEME_ARCHITECTURE rename) plus adjacent drift (FAILURE_MODES, this changelog, top-level README, AGENTS, llms.txt). The Gate-28-equivalent dogfood criterion: editing episteme-while-editing-episteme must satisfy Blueprint D.

No version bump yet — v1.0.0-rc1 tag follows CP1-CP10 completion + RC soak.

---

## [0.11.0] — 2026-04-21 — The Calibration Loop: profile becomes control signal, episodic tier writes, semantic promotion, profile-audit closes the circuit

This release closes the loop the kernel has been building toward since
0.8.0: an operator's declared cognitive profile is no longer
documentation — it is a *control signal* that modulates hook behavior
(phase 9), is checked against the *lived record* of high-impact
decisions (phase 10), is *clustered into proposals* for promotion
(phase 11), and is *audited for drift* against praxis (phase 12). The
profile-audit loop counters measure-as-target drift (failure mode 8)
by surfacing where the operator's claim and the operator's behavior
have diverged — not as a verdict, but as a re-elicitation prompt.

- **Phase 9 — profile becomes control signal.** New `core/hooks/_derived_knobs.py`
  derives 7 behavior knobs from the operator profile axes and writes
  them to `~/.episteme/derived_knobs.json`. `reasoning_surface_guard.py`
  replaces module-level `MIN_DISCONFIRMATION_LEN` /
  `MIN_UNKNOWN_LEN` constants with lookups against the derived knob,
  fallback 15. For the maintainer's v2 profile the minimum raises 15
  → 27. First end-to-end proof the v2 profile modulates hook
  behavior. 17 new tests.
- **Phase 10 — episodic-tier writer.** New PostToolUse hook
  `core/hooks/episodic_writer.py` fires on high-impact Bash pattern
  match; assembles a record per the `memory-contract-v1` schema;
  appends to `~/.episteme/memory/episodic/YYYY-MM-DD.jsonl`.
  Reasoning-Surface snapshot attached when present (snapshot now
  includes `knowns` per phase-12 requirement; previously omitted);
  secrets redacted before write; provenance confidence reflects
  available signal. Wired into `hooks/hooks.json` PostToolUse/Bash
  alongside `state_tracker` and `calibration_telemetry`, all async.
  19 new tests.
- **Phase 11 — semantic-tier promotion job.** New `src/episteme/_memory_promote.py`
  + CLI subcommand `episteme memory promote`. Reads episodic tier,
  clusters by `(domain_marker, primary high-impact pattern)`,
  computes per-cluster success rate + disconfirmation fire rate,
  emits deterministic proposals to
  `~/.episteme/memory/reflective/semantic_proposals.jsonl`. Proposal
  ids are stable hashes of the signature + sorted evidence refs, so
  re-running on identical input produces byte-identical output.
  Never touches the semantic tier; promotion is explicit. 19 new tests.
- **Phase 11.5 — coherence pass (docs-only).** Specced in
  `docs/DESIGN_V0_11_COHERENCE_PASS.md`. Both arxiv-style figures
  rasterized to PNG; native Mermaid `graph TD` flowchart added in
  `docs/ARCHITECTURE.md` mapping doxa / episteme / praxis / 결 to
  exact file-level implementations. README leads thinking-first.
- **Phase 12 — profile-audit loop (4 worked axes).** New
  `src/episteme/_profile_audit.py` library + `episteme profile audit`
  CLI surface. On-demand comparison of each declared cognitive
  axis against the episodic record, emitted to
  `~/.episteme/memory/reflective/profile_audit.jsonl`. SessionStart
  surfaces unacknowledged drift via `core/hooks/session_context.py`.
  Four axes operationalized in 0.11.0; 11 axes ship as explicit
  per-axis stubs pointing to the spec sketch table for 0.11.1:
    - **Axis C · `fence_discipline` (CP2).** Constraint-removal
      records must carry reconstruction (S1) and review-trace (S2).
      Single-signature catastrophic exception per spec §Axis C —
      either signature failing flags drift, because constraint
      removal is high-consequence. Drift thresholds are
      claim-relative: `_FENCE_BANDS_BY_CLAIM` maps 0-5 to
      `[drift_floor, ideal_ceiling]` per signature. Claim 4
      reproduces the spec's 0.70 / 0.50 thresholds; claim 0 has
      floor 0.0 and cannot drift by under-performing.
    - **Axis A · `dominant_lens: failure-first` (CP3).** Two
      signatures: failure-frame ratio over unknowns +
      disconfirmation (S1, against `failure_frame` /
      `success_frame` lexicons in `kernel/PHASE_12_LEXICON.md`),
      and fire-condition rate from a per-record syntactic
      classifier on disconfirmation (S2). D1 strict — both must
      miss to flag drift. CP3 implements only `failure-first` at
      position 0; other lens values follow Template A.
    - **Axis D · `asymmetry_posture: loss-averse` (CP4).** Two
      signatures: stop-condition rate from a syntactic classifier
      on disconfirmation (S1), and rollback-mention rate against
      the `rollback_adjacent` lexicon over knowns + assumptions
      (S2). D1 strict. Success-verb vocabulary is deliberately
      tight — words like `deploy`, `promote`, `ship`, `merge`
      are excluded because they're routinely the noun-objects
      of stop verbs.
    - **Axis B · `noise_signature: status-pressure` (CP5).** Two
      signatures: buzzword density per record (S1, against the
      `buzzword` lexicon) and specificity-collapse under inferred
      cadence (S2). DRIFT DIRECTION INVERTED for S1 — high
      buzzword density against a counter-screen claim is what
      drift looks like. Catastrophic single-signature exception
      at S1 > 0.30 (decorative-language density at that level is
      itself the signal). Highest evidence floor (N ≥ 40) of all
      four axes.
- **Schema additions.** New `core/schemas/profile-audit/profile_audit_v1.json`
  governs the audit record shape. New `kernel/PHASE_12_LEXICON.md`
  ships five default lexicons (`failure_frame`, `success_frame`,
  `buzzword`, `causal_connective`, `rollback_adjacent`); operator
  override path at `core/memory/global/phase_12_lexicon.md`. Each
  audit record carries a `lexicon_fingerprint` so lexicon drift is
  visible in the record stream, never silent.
- **Operator profile v2 filled.** `core/memory/global/operator_profile.md`
  migrated from 0-3 to 0-5 process axes; all 9 cognitive-style
  axes populated. 5 axes remain `inferred` pending phase-12 audit
  signal — that the audit currently returns insufficient_evidence
  on the maintainer's small tier is correct cold-start behavior
  per spec §Cold-start, not a phase-12 bug.
- **D-countermeasures intact across CP2-CP5.** D1 multi-signature
  convergence (with the two named single-signature exceptions for
  Axis C and Axis B's catastrophic threshold), D2 retrospective-
  only, D3 re-elicitation never auto-correction, D4 named limits
  cited in every axis reason string.
- **Demo + README narrative re-centered.** `scripts/demo_posture.sh`
  gains a 2.2-second Beat 0 title card naming the Reasoning
  Surface fields, the Beat 3 BLOCK rendered in dim red (matching
  the script narration that calls it "the shallowest thing the
  kernel does"), and the falsifiable PASS in bright green as the
  actual climax. README posture-demo bullet re-captioned to put
  the Reasoning Surface itself at the climax — the specificity
  ladder is now framed as the *test* of the surface, not the
  point of it. New `docs/DEMOS.md` houses the second demo
  (renamed "posture as enforcement of the surface") so the
  homepage no longer puts cognition and enforcement at parity.
- **Versions reconciled:** `pyproject.toml`,
  `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`
  all 0.10.0 → 0.11.0.
- **Tests:** 121 → 304 passing (+183 across phases 9, 10, 11, 12).
  Zero regressions.

**What 0.11.0 is honestly NOT:**
1. **Coverage on 11 of 15 axes.** The spec-sketch table lays out
   templates for them; CP2-CP5 ship the four worked axes that prove
   the patterns. Remaining 11 are explicit per-axis stubs deferred
   to 0.11.1 — chosen over a generic fallback so the audit log is
   readable rather than 11 identical "not yet implemented" lines.
2. **Cross-axis consistency checks.** Per spec open question 5,
   v0.11 does per-axis only. `fence_discipline` high +
   `risk_tolerance` low expected; `fence_discipline` low +
   `risk_tolerance` low internally inconsistent — both pass in
   v0.11. Cross-axis lands in a follow-on.
3. **A schema field for cadence.** Per spec open question 2,
   v0.11 infers cadence from timestamp clustering; the
   `cadence_marker` field is 0.11.1 work.
4. **Goodhart-resistance beyond layer 1.** Reasoning Surface Guard
   still does syntactic + length checks. A sufficiently-aware
   agent can still defeat the gate with fluent-vacuous content
   that passes both. Phase 12 catches this OVER TIME via the
   audit loop, but the hot-path validator remains syntactic.
   v1.0 RC scope work — see `docs/DESIGN_V1_0_SEMANTIC_GOVERNANCE.md`
   for the proposed defense-in-depth upgrade.

## [0.10.0] — 2026-04-20 — The Sovereign Kernel: stateful interception + heuristic friction analyzer + profile freshness gate

- **Added** `core/hooks/state_tracker.py` — PostToolUse recorder that persists every agent-written file path, sha256, and timestamp to `~/.episteme/state/session_context.json` (24 h TTL, atomic temp+rename, `fcntl.flock` serialization). Tracks `Write`/`Edit`/`MultiEdit` targets across a curated extension set (`.sh`, `.bash`, `.zsh`, `.ksh`, `.py`, `.pyw`, `.js`, `.mjs`, `.cjs`, `.ts`, `.rb`, `.pl`, `.php`, plus extension-less files) and `Bash` redirect targets (`>`, `>>`, `| tee [-a]`).
- **Extended** `core/hooks/reasoning_surface_guard.py` to consult the state store. Two new match modes: (1) literal path/basename reference in a Bash command → deep-scan that file's current content against the high-impact pattern set; (2) variable-indirection shape (`bash $F`, `python $F`, `./$X`, `source $X`) against any recent tracked write → deep-scan every recent entry. Closes the write-then-execute-across-calls bypass and the `F=run.sh; bash $F` indirection shape.
- **Added** `episteme evolve friction` heuristic telemetry analyzer. Pairs prediction↔outcome JSONL records by `correlation_id`, flags `exit_code ≠ 0` against positive predictions, ranks most-violated unknowns and friction-prone ops, and emits a Markdown Friction Report. Deterministic, no ML. Seed for future automated `CONSTITUTION.md` refinement — see `docs/NEXT_STEPS.md`.
- **Added** `Last elicited: YYYY-MM-DD` required metadata on the operator profile markdown (Gap B). `episteme sync` parses it and injects a visible "Stale Context Warning" block into the rendered CLAUDE.md when absent or older than 30 days. Mirror field `last_elicited` also written to `.generated/workstyle_profile.json` and `.generated/workstyle_scores.json`. Schema doc (`kernel/OPERATOR_PROFILE_SCHEMA.md`) updated to make the field required.
- **Replaced** the ASCII control-plane diagram in `README.md` with `docs/assets/architecture_v2.svg` — three-layer schematic (Agent Runtime / Episteme Control Plane / Hardware · OS) with the Stateful Interceptor loop and Calibration Telemetry feed visible.
- **Neutrality sweep.** Final pass on historical narrative in `docs/PLAN.md` and `docs/PROGRESS.md`: residual absolute-user-home string references in *descriptions of the prior scrub* replaced with generic `~/...` language. Public `junjslee` GitHub identity retained intentionally.
- **Versions reconciled:** `pyproject.toml`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` all 0.8.0 → 0.10.0.
- **Tests:** 86 → 121 passing (35 new: 12 stateful interception, 7 friction analyzer, 16 last_elicited). Zero regressions.

**Architectural gaps that remain open (honest):**
1. **Intra-call indirection.** A single `Bash` call that both writes and executes a script (`echo "git push" > s.sh && bash s.sh` as *one* tool call) is caught today only by the existing in-command scanner (normalized text contains `git push`). State tracking adds no new coverage for this case because the PostToolUse recorder fires *after* the call completes. The true fix — pausing execution between the write and the exec — requires a cross-runtime proxy daemon (the next-phase Sovereign Kernel, 0.11+). The "Sovereign Kernel" name in 0.10.0 is directional — a first cut, not a finished claim.
2. **Dynamic shell assembly.** `A=git; B=push; $A $B` still passes — same reasoning as 0.8.1.
3. **Heredocs with variable terminators.** The redirect parser is regex-based and will miss `cat <<"$EOF" > f`.
4. **Scripts > 256 KB (hash) / > 64 KB (scan).** Unchanged caps from 0.9.0.

Rationale: 0.9.0-entry proved that a file-on-disk telemetry feed is enough to pair prediction↔outcome for a single operator. 0.10.0 extends that same discipline — file-on-disk state — across the *execution boundary* between a Write and a Bash. The kernel still rides the hook runtime; it does not yet mediate every syscall. The claim of a "Sovereign Kernel" is directionally honest: the control plane now remembers what the agent just wrote, which is the smallest step that meaningfully closes write-then-execute while staying within the Claude Code hook contract. The cross-runtime proxy daemon is the version of this that deserves the name without qualification — it is deferred to 0.11+ and explicitly gated on real-world FN evidence from 0.10.0 telemetry.

## [0.9.0-entry] — 2026-04-20 — Privacy scrub + calibration telemetry + visual demo + bypass hardening

- **Repository neutralized.** Personal filesystem paths and operator identifiers stripped from `docs/PROGRESS.md`, `docs/NEXT_STEPS.md`, `docs/assets/setup-demo.svg`, and `demos/01_attribution-audit/reasoning-surface.json`. Public `junjslee` GitHub identity retained intentionally.
- **Calibration telemetry shipped (Gap A).** `reasoning_surface_guard.py` writes a `prediction` record (correlation_id, command_executed, epistemic_prediction) to `~/.episteme/telemetry/YYYY-MM-DD-audit.jsonl` on every allowed high-impact Bash. New `core/hooks/calibration_telemetry.py` (PostToolUse) writes the matching `outcome` record carrying `exit_code` and status. Local-only; never transmitted.
- **Backtick substitution closed.** Command normalization maps backticks to whitespace; `` `git push` `` now trips the same patterns as bare shell.
- **`eval $VAR` blocked.** New indirection pattern label `"eval with variable indirection"` blocks `eval "$CMD"` / `eval $CMD`. Literal `eval "echo hi"` still passes.
- **Shell-script execution scanned.** `_match_script_execution` resolves and scans up to 64 KB of `.sh` files referenced by `./x.sh`, `bash x.sh`, `sh x.sh`, `zsh x.sh`, `source x.sh`, `. x.sh`. Missing scripts pass through (FP-averse).
- **Visual demo harness.** `scripts/demo_strict_mode.sh` is reproducible and recording-ready; `docs/CONTRIBUTING.md` documents the `asciinema rec → agg` flow.
- **Test coverage** 17 → 86 cases covering guard, telemetry, profile cognition, managed file, kernel integrity, workflow guard, context guard.

## [0.8.1] — 2026-04-20 — Strict-by-default enforcement + semantic validator + bypass-resistant matching

- **Flipped** `core/hooks/reasoning_surface_guard.py` default from advisory to **strict (blocking)**. Missing / stale / incomplete / lazy surfaces now exit 2 and block the tool call. Opt-out per-project: `touch .episteme/advisory-surface` (legacy `.episteme/strict-surface` is now a no-op — strict is default).
- **Added** semantic validator to `_surface_missing_fields`: `disconfirmation` and each `unknowns` entry must be ≥ 15 chars and must not match the lazy-token blocklist (`none`, `n/a`, `tbd`, `nothing`, `null`, `unknown`, `해당 없음`, `해당없음`, `없음`, `모름`, `-`, `--`, `...`, etc.). Closes the Lazy Agent Problem — an agent writing `"disconfirmation": "None"` or `"해당 없음"` no longer passes the gate.
- **Added** command-text normalization before regex matching: quotes, commas, brackets, parens, and braces map to whitespace, so bypass shapes like `python -c "subprocess.run(['git','push'])"`, `os.system('git push')`, and `sh -c 'npm publish'` trip the same high-impact patterns as bare shell invocations. Closes a concrete bypass vector where the `\b...\s+...\b` patterns missed quoted/bracketed forms.
- **Updated** `episteme inject`: strict mode is now the default no-op (nothing to create); `--no-strict` writes `.episteme/advisory-surface` explicitly. Removes the old `strict-surface` marker creation — redundant under the new default.
- **Strengthened** block-mode stderr output: leads with `"Execution blocked by Episteme Strict Mode. Missing or invalid Reasoning Surface."` and includes a one-line advisory-mode opt-out pointer.
- **Expanded** test coverage in `tests/test_reasoning_surface_guard.py` to 17 cases covering: strict-by-default on every failure mode (missing/stale/incomplete/lockfile), advisory-marker downgrade, legacy-marker no-op behavior, lazy-token rejection for disconfirmation and unknowns, short-string rejection, and three bypass-vector tests (subprocess list form, os.system, sh -c wrapping).
- **Synchronized** `kernel/HOOKS_MAP.md` with the new default and validator contract.

Rationale: 0.8.0's claim of a "deterministic control plane" was architecturally true (the PreToolUse hook does intercept every high-impact op) but operationally hedged — the default was advisory, and the validator only checked for non-empty strings. 0.8.1 closes both gaps. The system now delivers what the README has been claiming since 0.6.0: a strict cognitive contract that blocks execution until Knowns / Unknowns / Assumptions / Disconfirmation are filled with concrete, measurable, non-placeholder content.

## [0.8.0] — 2026-04-19 — Core migration: cognitive-os → episteme (name alignment + version reconciliation)

- **Renamed** Python package `src/cognitive_os/` → `src/episteme/`; all imports and console script (`episteme = "episteme.cli:main"`) updated. `git mv` preserved history.
- **Renamed** runtime directory convention `.cognitive-os/` → `.episteme/`; schema identifier `cognitive-os/reasoning-surface@1` → `episteme/reasoning-surface@1`.
- **Renamed** GitHub repo `junjslee/cognitive-os` → `junjslee/episteme` (old URL 301-redirects); all in-repo references updated.
- **Renamed** env vars `COGNITIVE_OS_CONDA_ROOT` → `EPISTEME_CONDA_ROOT` (legacy var still honored).
- **Made dynamic** the Python runtime: `CONDA_ROOT` hardcoded path → `PYTHON_PREFIX` derived from `sys.prefix`. New vars `EPISTEME_PYTHON_PREFIX` / `EPISTEME_PYTHON` / `EPISTEME_REQUIRE_CONDA`. `episteme doctor` skips conda checks on non-conda runtimes unless explicitly required.
- **Reconciled** versions: `pyproject.toml` (0.2.0 → 0.8.0), `.claude-plugin/plugin.json` (0.6.0 → 0.8.0), `.claude-plugin/marketplace.json` plugin (0.6.0 → 0.8.0). Three surfaces now agree.
- **Added** `.gitignore` rules for `.episteme/` and legacy `.cognitive-os/` runtime dirs.
- **Verified** `v0.8.0` git tag pushed to `origin`; `/plugin marketplace add junjslee/episteme` resolves.

Rationale: the name `cognitive-os` implied a replacement OS-layer; the project is an epistemic *posture* that rides existing runtimes. `episteme` (ἐπιστήμη — "justified, audited knowledge") matches the kernel's actual claim: knowledge is provisional unless it can be traced to evidence and disconfirmation conditions. No kernel principle or schema field changed — this is a cosmetic/identity migration, hence minor-version bump despite touching every adapter surface.

## [0.7.0] — 2026-04-19 — Real enforcement: audit log, inject command, strict blocking

- **Added** `_write_audit()` to `core/hooks/reasoning_surface_guard.py` — every reasoning-surface check (passed / advisory / blocked) now writes a structured entry to `~/.episteme/audit.jsonl`. Audit failure is silenced so it can never itself block an operation.
- **Added** `episteme inject [path] [--no-strict]` CLI command — deploys cognitive enforcement to any repository in one command: creates `.episteme/strict-surface` (hard-block mode) and a blank reasoning-surface template. Default: strict. Closes onboarding friction gap.
- **Added** `episteme log [--limit N] [--blocked]` CLI command — reads `~/.episteme/audit.jsonl` and renders a formatted time-series audit table with 🟢/🟡/🔴 action indicators. Closes observability gap.
- **Bumped** `plugin.json` version to `0.6.0`.
- **Added** `?` / `help [subcommand]` CLI aliases — `episteme ?` and `episteme help sync` both resolve to the correct help output.

Rationale: 0.6.0 established the philosophical control plane. 0.7.0 makes it physically enforceable and observable. The hook now produces a real block (exit 2) when strict mode is active — not advisory text. The audit log turns governance from "trust the agent read the markdown" into "here is every check, timestamped." The inject command reduces onboarding from sync + setup + survey to one command for any repo that needs immediate coverage.

Architectural gap still open: enforcement scope is currently limited to Claude Code's PreToolUse hook surface. A cross-runtime MCP proxy daemon that intercepts tool calls regardless of LLM runtime is the next level.

## [0.6.0] — 2026-04-19 — Epistemic control plane, DbC framing, zero-trust positioning

- **Fixed** `.claude-plugin/marketplace.json` schema: `plugins[0].source` was `"."` (invalid relative path); corrected to `"https://github.com/junjslee/episteme"`. Plugin is now installable via `/plugin marketplace add junjslee/episteme`.
- **Removed** `src/episteme/viewer/index.html` — deprecated UI artifact; `episteme viewer` CLI command remains.
- **Reframed** `README.md` opening with explicit governance positioning: episteme as a *deterministic control plane* and *epistemic policy engine*, not just a workflow tool. Added feedforward-vs-feedback contrast, DbC contract framing (Preconditions / Postconditions / Invariants), and OPA analogy.
- **Added** "Zero-trust execution" section to `README.md`: maps OWASP Agentic AI Top 10 risks to Reasoning Surface counters (prompt injection → Core Question gate, overreach → constraint regime, hallucination → mandatory Unknowns, infinite loops → Disconfirmation).
- **Added** "Human prompt debugging" section to `README.md`: frames the Knowns/Unknowns mapping as a mechanism for exposing logical gaps in the *user's original intent* before execution proceeds.
- **Added** interoperability statement and control-plane architecture diagram placeholder to `README.md`.
- **Added** Cynefin problem-domain classification table to `KERNEL_LIMITS.md`: requires agents to classify Clear / Complicated / Complex / Chaotic before populating the Reasoning Surface. Closes the most common misuse pattern—running analysis loops on Complex domains.
- **Updated** `.github/ISSUE_TEMPLATE/feature.yml`: added "Epistemic alignment" field requiring proposers to address kernel-principle impact, failure-mode mapping, and layer placement (kernel vs. profile vs. adapter). Replaced generic acceptance-criteria placeholder with falsifiable, disconfirmation-aware template.

Rationale: 0.5.0 made the system installable and demonstrable. 0.6.0 makes it *legible to engineers and systems thinkers*—the governance positioning, DbC contract model, and zero-trust framing translate the epistemic depth into language that maps to existing infrastructure-safety intuitions. The Cynefin addition closes a real misuse gap: structured deliberation is only correct for Complicated domains; Complex domains need probes, not plans.

## [0.5.0] — 2026-04-19 — Posture framing, installability, differential proof

- **Reframed** the top-of-repo lede and delivery pitch around *epistemic posture*. Added [`docs/POSTURE.md`](../docs/POSTURE.md) as the canonical statement of what episteme installs (texture of thought / texture of action / rationale). README lede now reads "episteme installs an epistemic posture."
- **Published** [`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) and updated [`plugin.json`](../.claude-plugin/plugin.json) with explicit `agents`, `skills`, and `hooks` discovery paths. Added [`hooks/hooks.json`](../hooks/hooks.json) using `${CLAUDE_PLUGIN_ROOT}` so the plugin is portable. Repo is now `/plugin marketplace add junjslee/cognitive-os`-installable from any machine.
- **Added** [`INSTALL.md`](../INSTALL.md) — the three install paths (marketplace one-liner, full clone + CLI, dev `--plugin-dir`).
- **Added** [`demos/03_differential/`](../demos/03_differential/) — same prompt, posture off vs. on, with a [`DIFF.md`](../demos/03_differential/DIFF.md) analysis of what the posture changed. Scenario: a PM asks for a 2-sprint semantic-search scope; posture-off answers *how*, posture-on answers *whether*. Named failure modes caught: question substitution, WYSIATI, anchoring, planning fallacy, overconfidence.
- **Added** `episteme capture` CLI command ([`src/episteme/capture.py`](../src/episteme/capture.py)) — drafts a reasoning-surface.json skeleton from unstructured text (Slack thread, PR, ticket, email). Extracts Knowns / Unknowns / Assumptions via declared heuristics; leaves `disconfirmation[]` intentionally empty because the operator must declare it. Closes the "capture ergonomics" adoption-friction gap.

Rationale: the prior release (0.4.0) landed the substrate bridge, benchmark, plugin scaffolding, local viewer, and a second demo. This release makes the product *pitchable* (posture framing), *installable* (marketplace manifest + portable hooks), and *differentially provable* (the off-vs-on demo). The capture CLI is the first real ergonomics primitive — the Reasoning Surface stops being a blank JSON file and starts being a 5-minute edit.

## [0.4.0] — 2026-04-19 — Substrate bridge, benchmark, plugin scaffolding, viewer, demo 02

- **Added** pluggable substrate bridge ([`docs/SUBSTRATE_BRIDGE.md`](../docs/SUBSTRATE_BRIDGE.md), `src/episteme/bridges/substrate/`) with three reference adapters (`noop`, `mem0`, `memori`). Contract: `global` memory never routes, `skipped ≠ failed`, provenance sacred when supported.
- **Added** [`benchmarks/kernel_v1/`](../benchmarks/kernel_v1/) — 20-prompt deterministic scorer with pre-declared disconfirmation target and strict scoring mode. First run: 18/20 strict (0.9), two modes flagged below the 0.70 per-mode bar. Honest partial PASS with integrity caveats documented.
- **Added** [`.claude-plugin/plugin.json`](../.claude-plugin/plugin.json) and plugin README (marketplace scaffolding).
- **Added** `episteme viewer` — stdlib-only local dashboard over the repo on 127.0.0.1:37776.
- **Added** [`demos/02_debug_slow_endpoint/`](../demos/02_debug_slow_endpoint/) — posture applied to a realistic p95 regression (DROP INDEX hidden in a rename migration). The fluent-wrong "add a Redis cache" answer rejected at the Core Question gate.

## [0.3.0] — 2026-04-19 — Attribution, boundary, and summary

- **Added** `kernel/SUMMARY.md` — 30-line operational distillation loaded first by agents.
- **Added** `kernel/KERNEL_LIMITS.md` — six conditions under which the kernel is the wrong tool, plus four declared structural gaps (calibration telemetry, profile staleness, multi-operator mode, tacit/explicit trade-off).
- **Added** operational summaries to each kernel file (two-tier structure: 5–7 line agent-efficient summary above full essay).
- **Expanded** `kernel/REFERENCES.md` from 4 to 14 primary citations with concept→wording maps; 15+ secondary sources documented. Primary additions: Popper, Shannon, Argyris & Schön, Alexander, Polanyi, Graham/Taleb, Pearl, Simon, Deming, Meadows.
- **Added** inline attribution footers to `CONSTITUTION.md`, `REASONING_SURFACE.md`, `FAILURE_MODES.md`.
- **Linked** `KERNEL_LIMITS.md` from `CONSTITUTION.md`'s "what it is not" section.

Rationale: a kernel whose claims cannot be traced to primary sources is unfalsifiable at the source-of-ideas level. A kernel without a declared boundary is a creed. Both gaps closed in this version.

## [0.2.0] — 2026-03 — Kernel extraction

- **Separated** `kernel/` from runtime and adapter code. Pure markdown; vendor-neutral.
- **Added** `CONSTITUTION.md`, `REASONING_SURFACE.md`, `FAILURE_MODES.md`, `OPERATOR_PROFILE_SCHEMA.md`, `HOOKS_MAP.md`, `MANIFEST.sha256`.

## [0.1.0] — 2026-02 — First principles

- Initial four-principle statement and six-failure-mode taxonomy.
- Workflow loop: Frame → Decompose → Execute → Verify → Handoff.

---

## How to edit this file

- Propose kernel changes as a version entry here *before* editing the kernel files.
- Reference the Evolution Contract (`docs/EVOLUTION_CONTRACT.md`) for the propose → critique → gate → promote flow on load-bearing changes.
- The current version number is mirrored in `MANIFEST.sha256` generation.
