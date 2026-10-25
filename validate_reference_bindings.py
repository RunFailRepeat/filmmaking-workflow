"""Offline checks of declared reference assignments; reuses existing ordinal checks.

No provider calls, image inspection, semantic classification or spending authority.
Approved requirements and current pins must come from separately reviewed sources.
"""
import json
import re
import sys
from pathlib import Path
from jev_audit import validate_state, digest, keys, require, sha, text
from validate_continuity import dated, recorded

REVIEW_CHECKS = {'correct_subjects', 'specific_prop_roles', 'no_redundant_appearance_override',
                 'approved_characters_reused', 'voice_performance_and_audio_bindings'}


def validate(packet):
    try:
        keys(packet, {'state', 'current', 'requirements', 'requirements_sha256',
                      'provider_notation', 'semantic_review', 'consumption'})
        state, current, requirements = (packet[k] for k in ('state', 'current', 'requirements'))
        # Keep the established ordered-media, image-ordinal, exact-token and pin checks.
        validate_state(state, current)
        sha(packet['requirements_sha256'])
        require(digest(requirements) == packet['requirements_sha256'], 'approved requirement pin mismatch')
        require(isinstance(requirements, list) and bool(requirements), 'required character/prop manifest missing')
        require(all(r['role'] == 'image' for r in state['references']),
                'this adapter requires image-only media roles; mixed media needs separate review')
        refs = {r['subject']: r for r in state['references']}
        require(len(refs) == len(state['references']), 'one declared reference per entity required by this adapter')
        entities, assets = set(), set()
        for item in requirements:
            keys(item, {'entity_id', 'kind', 'approved_media_id', 'source_sha256', 'reference_roles'})
            for k in ('entity_id', 'approved_media_id'):
                text(item[k]); require(recorded(item[k]), 'unresolved approved entity/media ID')
            require(item['kind'] in ('character', 'prop', 'environment'), 'unknown reference entity kind')
            sha(item['source_sha256'])
            require(isinstance(item['reference_roles'], list) and bool(item['reference_roles']), 'missing intended reference roles')
            for role in item['reference_roles']: text(role)
            require(len(set(item['reference_roles'])) == len(item['reference_roles']), 'duplicate intended reference role')
            if item['kind'] == 'prop':
                require('prop' in item['reference_roles'], 'specific prop requires its own prop role')
            if item['kind'] == 'character':
                require('identity' in item['reference_roles'], 'character requires identity role')
            require(item['entity_id'] not in entities, 'duplicate required entity')
            require(item['approved_media_id'] not in assets, 'each specific entity requires a distinct binding in this adapter')
            entities.add(item['entity_id']); assets.add(item['approved_media_id'])
            ref = refs.get(item['entity_id'])
            require(ref is not None, 'required character/prop reference missing')
            require(ref['uuid'] == item['approved_media_id'] and ref['source_sha256'] == item['source_sha256'],
                    'intended entity does not match approved reference identity/hash')
        require(entities == set(refs), 'unexpected reference entity outside approved requirements')

        notation = packet['provider_notation']
        keys(notation, {'provider', 'model', 'mode', 'source', 'checked_at', 'verified', 'tokens'})
        for k in ('provider', 'model', 'mode', 'source'):
            text(notation[k]); require(recorded(notation[k]), 'unresolved provider notation evidence')
        require(notation['verified'] is True and dated(notation['checked_at']), 'verified dated provider notation evidence required')
        require(all(notation[k] == state['payload']['settings'].get(k) for k in ('provider', 'model', 'mode')),
                'notation evidence must match actual provider/model/mode')
        expected_tokens = [r['notation'] for r in state['references']]
        require(notation['tokens'] == expected_tokens, 'provider-supported tokens must match ordered reference tokens')
        # Additional check for common numbered @ aliases, not a universal provider grammar.
        found = re.findall(r'(?<![\w@])@[A-Za-z]+ ?\d+(?!\w)', state['payload']['prompt'])
        require(set(found) == set(expected_tokens), 'unknown/missing numbered model-visible token')

        review = packet['semantic_review']
        keys(review, {'state_sha256', 'requirements_sha256', 'notation_sha256', 'reviewer', 'reviewed_at', 'checks', 'evidence'})
        require(review['state_sha256'] == digest(state) and review['requirements_sha256'] == packet['requirements_sha256']
                and review['notation_sha256'] == digest(notation), 'semantic review is stale for current bindings/prompt')
        for k in ('reviewer', 'evidence'):
            text(review[k]); require(recorded(review[k]), 'semantic reviewer and evidence required')
        require(dated(review['reviewed_at']), 'dated semantic review required')
        keys(review['checks'], REVIEW_CHECKS)
        require(all(v == 'pass' for v in review['checks'].values()), 'semantic reference/appearance/audio review unresolved')

        consumption = packet['consumption']
        keys(consumption, {'repo_commit', 'rules_version', 'rules_sha256', 'owner_corrections_version',
                           'owner_corrections_sha256', 'payload_sha256', 'reviewer', 'consumed_at'})
        require(consumption['repo_commit'] == state['repo_commit'], 'consumed repository version mismatch')
        for field in ('rules', 'owner_corrections'):
            require(consumption[field + '_version'] == state[field]['version'] and
                    consumption[field + '_sha256'] == state[field]['sha256'], 'consumed rules/corrections version mismatch')
        require(consumption['payload_sha256'] == digest(state['payload']), 'consumption not bound to actual payload')
        text(consumption['reviewer'])
        require(recorded(consumption['reviewer']) and dated(consumption['consumed_at']), 'dated consumption reviewer required')
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        return [str(exc) or 'malformed reference packet']
    return []


def main():
    if len(sys.argv) != 2:
        print('Usage: python validate_reference_bindings.py PACKET.json')
        return 2
    try:
        packet = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
        errors = validate(packet)
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    if errors:
        print('\n'.join(errors)); return 1
    print('Declared reference assignments consistent; no visual/semantic proof, provider verification or execution authority.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
