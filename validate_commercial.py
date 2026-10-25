"""Offline commercial record checks, never execution authority or perceptual QA."""
import json
import sys
from pathlib import Path
from validate_continuity import dated, recorded, shape

SCHEMA = Path(__file__).parent / 'schemas/commercial.schema.json'


def validate(data):
    errors = shape(data, json.loads(SCHEMA.read_text(encoding='utf-8')))
    if errors:
        return errors

    def require(ok, message):
        if not ok:
            errors.append(message)

    sources = data['sources']
    require(len({s['id'] for s in sources}) == len(sources), 'duplicate source ID')
    for source in sources:
        require(source['duration_seconds'] <= data['source_cap_seconds'],
                'source duration exceeds configured ceiling')
    social = data['social']
    if social['phone_first']:
        require(social['composition'] == 'native_9_16', 'phone-first requires native 9:16 composition, not landscape cropping')
        require(all(social[k] for k in ('mobile_readability_planned', 'immediate_visual_hook_planned',
                                       'motivated_cuts_planned', 'muted_comprehension_planned')),
                'phone-first composition, hook, motivated cuts and muted comprehension must be planned')
    ready = data['status'] in ('submission_ready', 'accepted')
    if data['owner_verdict'] == 'rejected':
        require(data['status'] == 'rejected', 'owner rejection cannot become ready or accepted')
    research = data['research']
    entries = research['sources']
    by_id = {s['id']: s for s in entries}
    require(len(by_id) == len(entries), 'duplicate research source ID')
    require(not research['third_party_material_copied'], 'research does not authorize copying third-party creative material')
    for source in entries:
        if source['access'] != 'read':
            require(not source['read_sections'] and not source['creative_viewed'] and not source['creative_heard'],
                    'unread/unavailable source cannot claim reading or creative review')
            require(source['metric_kind'] == 'not_reported' and source['conclusion'] == 'unknown',
                    'unread/unavailable source cannot assert outcome conclusions; attribute claims to reviewed evidence')
        if source['conclusion'] == 'business_outcome_reported':
            require(source['metric_kind'] == 'business_outcome', 'popularity is not conversion/business-outcome evidence')
        if source['conclusion'] == 'popularity_only':
            require(source['metric_kind'] == 'popularity', 'popularity conclusion requires popularity evidence')
    if ready:
        require(research['status'] == 'reviewed' and recorded(research['access_review']),
                'focused campaign and academic access/research review required before readiness')
        for source in entries:
            require(all(recorded(source[k]) for k in ('id', 'title', 'author', 'link', 'limits', 'lawful_use'))
                    and dated(source['checked_at']), 'exact dated research source, limits and lawful use required')
            if source['access'] == 'read':
                require(bool(source['read_sections']) and all(recorded(v) for v in source['read_sections']),
                        'record exact sections/pages actually read')
                require(recorded(source['creative_coverage']), 'record actual creative viewing/hearing coverage')
                if source['metric_kind'] != 'not_reported':
                    require(recorded(source['metric_evidence']) and recorded(source['metric_scope']),
                            'reported metrics require supporting evidence and measurement scope')
            if source['access'] == 'unavailable':
                require(recorded(source['access_limitation']) and bool(source['alternative_source_ids']),
                        'unavailable research needs limitation and lawful public alternative')
                for ref in source['alternative_source_ids']:
                    alternate = by_id.get(ref)
                    require(alternate is not None and alternate['access'] == 'read'
                            and alternate['access_route'] == 'public', 'fallback must identify a reviewed public source')
        for kind in ('campaign', 'academic'):
            require(any(s['kind'] == kind and s['access'] in ('read', 'unavailable') for s in entries),
                    kind + ' research or documented access limitation required')
        dimensions = [a['dimension'] for a in research['applications']]
        require(set(dimensions) == {'hook', 'physical_action', 'cuts', 'pacing', 'sound', 'payoff'}
                and len(dimensions) == 6, 'research application must address six craft dimensions once')
        for application in research['applications']:
            require(recorded(application['change']) and recorded(application['verification_plan']),
                    'application needs concrete change/retention decision and verification plan')
            require(bool(application['source_ids']) and all(ref in by_id and by_id[ref]['access'] == 'read'
                    for ref in application['source_ids']), 'application must cite actually reviewed sources')
        require(all(recorded(s['id']) for s in sources), 'source IDs must be resolved')
        require(data['owner_verdict'] == 'approved', 'owner decision remains unresolved')
        require(data['prompt_approved'] and data['design_approved'] and data['rights_approved'],
                'prompt, design and rights approval declarations required')
        references = data['references']
        require(bool(references), 'actual references required')
        require(len({r['role'] for r in references}) == len(references), 'duplicate reference role')
        require(all(recorded(r[k]) for r in references for k in ('role', 'artifact_id', 'provider_id')),
                'reference IDs and roles must be resolved')
        require(all(r['approved'] for r in references), 'reference approval unresolved')
        require(bool(data['required_reference_roles']) and
                set(data['required_reference_roles']) == {r['role'] for r in references},
                'all required reference roles must be bound')
        require(len(set(data['required_reference_roles'])) == len(data['required_reference_roles']),
                'duplicate required reference role')
        quote, budget = data['quote'], data['budget']
        require(data['request_validated'] and quote['kind'] == 'final_payload',
                'price-only quote cannot validate a final request')
        require(quote['payload_sha256'] == data['payload_sha256'], 'quote does not match exact payload')
        require(dated(quote['checked_at']) and recorded(quote['evidence']), 'dated quote evidence required')
        require(budget['authorized'] and recorded(budget['evidence']),
                'quote cannot supply spending authorization')
        require(budget['payload_sha256'] == data['payload_sha256'], 'budget does not match exact payload')
        require(recorded(quote['unit']) and recorded(budget['unit']), 'quote/budget units must be resolved')
        require(quote['unit'] == budget['unit'], 'quote/budget units differ')
        require(quote['total'] <= budget['maximum'], 'quote exceeds authorized maximum')
        require(not budget['requires_hard_cap'] or budget['hard_cap_verified'],
                'requested hard cap is not verified')
    if data['status'] == 'accepted':
        if social['phone_first']:
            social_fields = ('destination', 'safe_guide_source', 'safe_guide_checked_at',
                             'safe_regions_verified', 'mobile_faces_hands_product_readable',
                             'hook_and_cuts_reviewed', 'caption_brand_overlays_clear',
                             'muted_comprehension_reviewed', 'sound_cleared', 'clean_export_reviewed')
            absent = [key for key in social_fields if key not in social]
            if absent:
                return errors + ['phone-first acceptance requires actual social review: ' + ', '.join(absent)]
            require(recorded(social['destination']) and recorded(social['safe_guide_source'])
                    and dated(social['safe_guide_checked_at']), 'dated destination-specific safe guide required')
            require(all(social[k] for k in social_fields[3:]), 'all phone-first actual export checks must pass')
        missing = [key for key in ('output', 'review', 'owner_heard_and_watched',
                                   'owner_review_evidence', 'owner_review_artifact') if key not in data]
        if missing:
            return errors + ['acceptance requires actual evidence: ' + ', '.join(missing)]
        review = data['review']
        require(review['artifact'] == data['output'], 'review must match exact output identity/version/hash')
        require(all(recorded(v) for v in data['output'].values()), 'output identity must be resolved')
        require(recorded(review['reviewer']) and dated(review['reviewed_at']) and review['independent'],
                'dated independent reviewer required')
        require(review['picture_method'] == 'normal_speed_viewing' and review['picture_complete'],
                'full normal-speed picture review required; frames alone are insufficient')
        require(review['audio_method'] == 'direct_listening' and review['audio_complete'],
                'complete direct-audio review required; waveforms/transcripts are insufficient')
        require(all(review['checks'].values()), 'all declared review checks must pass')
        require(data['owner_heard_and_watched'] and recorded(data['owner_review_evidence']) and
                data['owner_review_artifact'] == data['output'],
                'owner acceptance must refer to watched/heard exact output')
    return errors


def main():
    if len(sys.argv) != 2:
        print('Usage: python validate_commercial.py PACKET.json')
        return 2
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
        errors = validate(data)
    except (OSError, ValueError) as exc:
        print('Invalid commercial packet: ' + str(exc))
        return 1
    if errors:
        print('\n'.join(errors))
        return 1
    print('Commercial declarations consistent (' + data['evidence_kind'] +
          '); no approval authentication, generation, viewing or listening performed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
