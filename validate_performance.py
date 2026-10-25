"""Offline declaration checks. Does not listen, authenticate approvals or authorize jobs."""
import json
import math
import re
import sys
from pathlib import Path

from validate_continuity import dated, recorded, shape

SCHEMA = Path(__file__).parent / 'schemas/performance.schema.json'
V4_MODELS = {'elevenlabs_v4', 'eleven_v4', 'eleven_v4_turbo'}
V4_PARAMETERS = {'stability', 'similarity_boost'}


def same(a, b):
    return math.isclose(a, b, rel_tol=0, abs_tol=1e-7)


def validate(d, stage='planning'):
    """Check metadata; acceptance additionally requires declared direct hearing evidence.

    A production_record label is a declaration, never proof of authenticity.
    Synthetic fixtures can exercise every gate but remain synthetic.
    Bounded format: one character, one continuous stem, prefix cues only;
    changing approved intent needs a separate review record, not a rewritten source.
    Source hashes are declared bindings; this tool does not fetch or hash media.
    """
    if stage not in ('planning', 'acceptance'):
        return ['unknown stage']
    errors = shape(d, json.loads(SCHEMA.read_text(encoding='utf-8')))
    if errors:
        return errors

    def require(ok, message):
        if not ok:
            errors.append(message)

    accepted = stage == 'acceptance' or d['status'] == 'accepted' or d['dependent_visuals_ready']
    approved, candidate, contract, bridge = (d[k] for k in
        ('approved_performance', 'candidate', 'provider_contract', 'audio_bridge'))
    require(approved['reference_start'] < approved['reference_end'],
            'positive approved performance reference range required')
    canonical = d['canonical_lines']
    ids = [line['id'] for line in canonical]
    require(len(set(ids)) == len(ids), 'duplicate canonical line ID')
    require(all(line['character_id'] == d['character_id'] for line in canonical),
            'one character per continuous performance record')
    require([{k: line[k] for k in ('id', 'character_id', 'spoken_text')}
             for line in candidate['lines']] == canonical,
            'candidate must preserve exact canonical words, character and order')
    for line in candidate['lines']:
        require(line['control_cues'] == approved['control_cues'],
                'approved expressive cues missing or changed; preserve historical approval and review changed intent separately')
        require(line['provider_text'] == ' '.join([*line['control_cues'], line['spoken_text']]),
                'provider text must render exact control cues separately from spoken words')
        require(all(cue not in line['spoken_text'] for cue in line['control_cues']),
                'control cue leaked into spoken dialogue')
    for key in ('provider', 'model', 'voice_id', 'voice_type'):
        require(candidate[key] == approved[key], 'approved performance ' + key + ' mismatch')
    for key in ('provider', 'model'):
        require(contract[key] == candidate[key], 'provider contract ' + key + ' mismatch')
    require(candidate['parameters'] == approved['parameters'],
            'approved performance parameters changed; separate review of changed intent required')
    names = [p['name'] for p in contract['parameters']]
    submitted_names = [p['name'] for p in candidate['parameters']]
    require(len(names) == len(set(names)) and len(submitted_names) == len(set(submitted_names)),
            'duplicate parameter name')
    approved_names = [p['name'] for p in approved['parameters']]
    require(len(approved_names) == len(set(approved_names)), 'duplicate approved parameter name')
    supported = [{k: p[k] for k in ('name', 'value')} for p in contract['parameters'] if p['supported']]
    has_ssml_break = any(re.search(r'<\s*break\b', line['provider_text'], re.IGNORECASE)
                         for line in candidate['lines'])
    require(not has_ssml_break or contract['ssml_breaks_supported'],
            'SSML breaks require explicit provider support')
    if candidate['model'] in V4_MODELS:
        require(not contract['ssml_breaks_supported'] and not has_ssml_break,
                'Eleven v4 does not support SSML breaks')
        for parameter in [*approved['parameters'], *candidate['parameters'],
                          *[p for p in contract['parameters'] if p['supported']]]:
            require(parameter['name'] in V4_PARAMETERS,
                    'Eleven v4 parameter unsupported: ' + parameter['name'])
            try:
                value = float(parameter['value'])
                valid = math.isfinite(value) and 0 <= value <= 1
            except ValueError:
                valid = False
            require(valid, 'Eleven v4 supported parameter values must be numeric strings in [0, 1]')
    require(candidate['parameters'] == supported,
            'every submitted parameter/value requires exact provider support evidence')
    require(not approved['control_cues'] or contract['control_cues_supported'],
            'expressive cues require provider support evidence')
    require(dated(contract['checked_at']) and recorded(contract['source']),
            'dated provider contract source required')

    require(bridge['source'] == candidate['source'], 'audio bridge must bind exact candidate source/version')
    require(bridge['source_start'] < bridge['source_end'] and bridge['export_start'] < bridge['export_end'],
            'positive continuous audio range required')
    require(same(bridge['source_end'] - bridge['source_start'], bridge['export_end'] - bridge['export_start']),
            'normal-speed continuous audio only; retiming requires another reviewed mapping')
    require([r['line_id'] for r in bridge['line_ranges']] == ids,
            'continuous audio must cover every canonical line once in order')
    previous = bridge['source_start']
    for span in bridge['line_ranges']:
        require(previous <= span['source_start'] < span['source_end'] <= bridge['source_end'],
                'audio line ranges overlap, reorder or exceed continuous source')
        require(span['export_start'] < span['export_end'], 'positive export line range required')
        for endpoint in ('start', 'end'):
            require(same(span['export_' + endpoint], bridge['export_start'] +
                         span['source_' + endpoint] - bridge['source_start']),
                    'line range must preserve continuous source-to-export mapping')
        previous = span['source_end']
    cuts = bridge['picture_cuts']
    require(cuts == sorted(set(cuts)), 'picture cuts must be unique and chronological')
    require(all(bridge['export_start'] < cut < bridge['export_end'] for cut in cuts),
            'picture cut outside continuous audio coverage')

    if accepted:
        for label, record, reference in (('approved', approved, approved['source']),
                                         ('candidate', candidate, approved['source'])):
            review = record['review']
            require(all(recorded(v) for v in record['source'].values()), label + ' exact source identity required')
            require(review['source'] == record['source'], label + ' review source/version mismatch')
            require(review['comparison_source'] == reference, label + ' review comparison source/version mismatch')
            require(review['method'] == 'direct_listening' and review['status'] == 'approved'
                    and review['owner_approved'] and review['owner_heard'],
                    label + ' requires heard owner-approved performance')
            require(recorded(review['owner_identity']) and recorded(review['owner_review_evidence']),
                    label + ' separate owner identity and source-bound hearing evidence required')
            require(recorded(review['listener']) and dated(review['reviewed_at']),
                    label + ' named listener and dated review required')
            require(review['start'] < review['end'] and all(review['checks'].values()),
                    label + ' listening coverage and all performance checks required')
        reference_review = approved['review']
        require(reference_review['start'] <= approved['reference_start']
                and reference_review['end'] >= approved['reference_end'],
                'approved listening must cover the entire declared reference range')
        review = candidate['review']
        require(review['start'] <= bridge['source_start'] and review['end'] >= bridge['source_end'],
                'candidate listening must cover the entire retained continuous audio')
    return errors


def main():
    if len(sys.argv) not in (2, 3):
        print('Usage: python validate_performance.py PACKET.json [planning|acceptance]')
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
        errors = validate(data, sys.argv[2] if len(sys.argv) == 3 else 'planning')
    except (OSError, ValueError) as exc:
        print('Invalid performance packet: ' + str(exc))
        return 1
    if errors:
        print('\n'.join(errors))
        return 1
    print('Recorded-evidence checks passed (' + data['evidence_kind'] +
          '); no listening, approval authentication, generation or media-quality verdict performed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
