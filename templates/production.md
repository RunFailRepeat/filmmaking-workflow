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

## Shot card

Complete a private continuity JSON packet using the bundled schema. The basic Markdown checker does not validate the voice/camera/finishing fields below; use validate_continuity.py as well. A metadata pass is not an actual media review or authenticated approval.

shot_id: TBD
source_duration_seconds: TBD
usable_range: TBD
start_state: TBD
action: TBD
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

## Character voice lock and actual payload

Per speaking character: provider / voice ID / type:
Exact user-heard approved take ID / immutable source version:
Current-film audition and owner approval evidence:
Accent / pronunciation / delivery:
Line IDs / exact dialogue / playback order:
Actual shot or reshoot payload version:
Supported ordered voice/audio bindings inspected:
If unsupported, approved direct-edit plan (takes, lines, ranges, sync, ambience):
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
Direct listening coverage for EVERY line: UNVERIFIED
Per line: approved take/version; heard voice AND accent; exact words/pronunciation/delivery; unclipped timing; sync; other speakers; ambience:
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
