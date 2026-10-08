# Production packet

Use a private copy. Replace TBD fields and record approvals only when actually granted.

project_id: TBD
objective: TBD
obstacle: TBD
ending: TBD
edit_duration_seconds: TBD
delivery_format: TBD
reference_ids: TBD
rights_review: PENDING
story_approval: PENDING
prompt_approval: PENDING
execution_approval: PENDING

User-defined duration minimum / target / maximum:
Beat windows in export seconds:
Per clip: source ID/version/duration, source in/out (including head trim), export start/end:
Per seam: export window and separately mapped outgoing/incoming source windows:
Approved dialogue IDs / exact speakers / text / order and cross-cut segment mapping:
Silent shots: no dialogue; preserve state, geography, effects and ambience:
Evidence stage: PLANNING ONLY until actual media review is separately recorded
Selected workflow sources, repository version/tests/readback and unresolved in-scope issues: see [work-cycle record](work-cycle.md); plugin checks only when authorized

Reference readiness: approved/versioned recurring wardrobe, location, complex prop and background-ensemble references; record missing designs and supported binding roles.
Production-ready / owner-authorized exploratory test (scope and unresolved references): UNRESOLVED
Estimate reference-transfer side effects / authority / reused confirmed bindings: see [media transfers](../MEDIA_TRANSFERS.md)

## Character-sheet output contract (when applicable)

Current user brief/version and approval:
Requested view types and count of each:
Total output panels (reconcile with the view counts):
Identity — preserve / permitted changes:
Wardrobe — preserve / permitted changes:
Style — preserve / permitted changes:
Composition — preserve / permitted changes:
Exact final prompt/payload checked against current brief: NOT VERIFIED

Do not inherit the input reference's composition over explicit output instructions. Add no extra portrait, panel, percentage or geometric layout detail unless needed and specified. Record the project's approved layout here rather than assuming a universal panel count. This checklist requires human review; existing validators do not verify character-sheet layout.

## Shot card

For speaking material, complete a private packet using the [dialogue continuity schema](../schemas/continuity.schema.json) and validate_continuity.py. For silent shots, use the [planning contract](../PLANNING.md) with no dialogue segments on silent clips (empty ledgers for an entirely silent plan) and retain the visual/action seam and actual sound-review records below; do not invent speech or voice approvals. In a mixed edit, silent clips remain part of whole-export visual/sound review. Mark speech-only fields not applicable with a reason, including exact_dialogue: NONE (silent shot). The basic Markdown checker only checks fields and approval markers; neither it nor a planning pass establishes visual references, performance, actual media review or authenticated approval. Silent-export acceptance is human review, not a dialogue-schema release pass.

shot_id: TBD
source_duration_seconds: TBD
usable_range: TBD
start_state: TBD
action: TBD
director_intent_performance_reaction_and_opening_motion_phase: TBD
coverage_purpose: TBD
mechanical_review_details_separate_from_performance_prompt: TBD
end_state: TBD
screen_direction: TBD
exact_dialogue: TBD
ordered_reference_ids: TBD
model_and_mode: TBD
settings_version: TBD
acceptance_checks: TBD
lens_focal_length_look: TBD (visual intent, not physical optics guarantee)
framing: TBD
focus_depth_of_field: TBD
camera_movement: TBD
reshoot_continuity_and_approved_exceptions: TBD
outgoing_endpoint_state: TBD (characters, poses, ongoing action, props, environment)
incoming_angle_size: TBD (intentional new angle or meaningful shot-size change)
cut_plan: TBD (screen direction, eyelines, 180-degree axis, timing)
match_action_edit_handles: TBD (optional; no duplicated action/frozen overlap)
reference_for_state_or_fixed_start_frame: TBD
fixed_frame_supported_alternative_or_verified_trim_handles: TBD
explicit_continuous_shot_exception: NOT GRANTED
actual_seam_normal_speed_pose_action_voice_sound_review: UNVERIFIED
actual_seam_angle_size_axis_direction_eyelines_props_environment_checks: UNVERIFIED
actual_seam_sound_effects_preservation: UNVERIFIED
story_action_sequential: TBD
has_edited_seam_including_simultaneous_coverage: TBD
seam_reviewer_and_timezone_timestamp: UNVERIFIED
seam_export_asset_version_range_and_cut_seconds: UNVERIFIED
outgoing_and_incoming_source_assets_versions_durations_reviewed_ranges: UNVERIFIED

## Character voice lock and actual payload

Per speaking character: provider / voice ID / type:
Exact user-heard approved take ID / immutable source version:
Current-film audition and owner approval evidence:
Accent / pronunciation / delivery:
Line IDs / exact dialogue / playback order:
Actual shot or reshoot payload version:
Supported ordered voice/audio bindings inspected:
If unsupported, approved direct-edit plan (takes, lines, ranges, sync, ambience):
Complete actual timing and instructions; placeholder markers do not pass preflight.
Audio state (unchanged / removed / changed / replaced):
Replacement installed and approved: NOT VERIFIED

Do not assume a converted preset matches a generated voice, or a reference image preserves voice. New films audition voices; no automatic previous-film voice reuse. Removed/changed audio remains unresolved until replaced and approved.

## Review evidence

Evidence coverage:
Decision: NOT REVIEWED
Accepted source ranges:
Defects and smallest repair:
Publication approval: NOT GRANTED

Actual final export version:
Actual final export asset ID and duration (seconds):
Actual listener ID and timezone-qualified listening date/time: UNVERIFIED
Exact listened source asset ID (must match final export):
Listened export-relative time ranges (full export, including effects/ambience):
Per-line export-relative start/end ranges:
Keep declared line starts in playback order; overlapping/equal starts are allowed.
Direct listening coverage for EVERY line: UNVERIFIED
Per line: approved take/version; heard voice AND accent; exact words/pronunciation/delivery; unclipped timing; sync; other speakers; ambience:
Per-line sound-effect preservation (separate from ambience): UNVERIFIED
Owner listening review gate: OPEN
ASR/transcript evidence is not listening. If unable to listen, retain UNVERIFIED status and owner review gate.

## Enhancement after approved picture/edit

Approved picture/edit source version:
Grading / sharpening / upscale settings (or explicit none):
Exact operation approval: NOT GRANTED
Fresh quote and spending approval if paid: NOT GRANTED
Actual enhanced output version:
Actual source-versus-enhanced comparison (identity/faces, artifacts/detail, crop, continuity, timing, audio): UNVERIFIED
Enhanced export listened to again: UNVERIFIED
Original and editable project retained: NOT VERIFIED
