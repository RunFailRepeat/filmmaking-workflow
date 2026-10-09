# Content analytics: definitions before conclusions

Reviewed **2026-10-07**. This is measurement guidance and an unexecuted exploratory proposal, not a change to video-generation, quality or production defaults. No private account data is included. Recheck definitions and available fields before comparing historical periods.

## Keep a reproducible observation record

Keep one row per post per snapshot in a private working log, preserving earlier snapshots. Record platform, exact surface/report (public counter, Studio or API), content ID/URL, published and captured timestamps with timezone, actual post age, reporting window and filters. Preserve each native metric label, value, unit, definition/source date and population/denominator where known. If metrics use different filters or populations, retain that distinction explicitly. Missing, unavailable and not-yet-reported are not zero.

Separate raw observations from inferred causes. Record distribution context, promotions, collaborations and known measurement changes. A difference between posts does not by itself establish why performance changed. There is no universal retention formula that can safely combine unlike platforms or surfaces.

## Platform-specific interpretation

**X public post views:** repeats and the author's own views can count; the count is not unique viewers or a measure of video watching. Embedded posts do not add to this counter. [X view-count definitions](https://help.x.com/en/using-x/view-counts)

**X Media Studio:** the documented video-view threshold is at least two seconds with at least half the **player** in view. Metrics aggregate the video across posts; the page specifies logged-in views and excludes logged-out and web-embed data. Record the date filter and organic/promoted population. Dividing aggregate video views by one post's public views is not a validated watch rate: the populations and aggregation differ. [Media Studio analytics](https://help.x.com/en/using-x/media-studio-analytics)

**YouTube Studio Shorts:** the reviewed Help page defines engaged views as watching beyond the opening seconds, excluding loops; stayed to watch is a percentage of occasions viewers continued beyond those opening seconds. Average percentage viewed is the average portion watched among those who stayed, using engaged views and their corresponding watch time. It is not the percentage of viewers who completed the Short. Preserve these distinct measures and denominators. [Studio content-performance definitions](https://support.google.com/youtube/answer/12220281?hl=en)

**YouTube API:** the reviewed `engagedViews` wording instead describes viewing beyond the first frame or clicking/tapping to play. Its `averageViewDuration` and `averageViewPercentage` descriptions exclude looping-clip traffic. Do not silently merge these API definitions with Studio labels, or generalize that API exclusion to all Shorts replay watch time. Record the actual surface/report and definition version; the documentation's wording difference is unresolved here. [YouTube Analytics API metrics](https://developers.google.com/youtube/analytics/metrics)

**Instagram:** the accessible 2023 announcement is historical evidence about watch-time metrics, not proof of today's labels or denominator. No readable current native-help definition was established in this review. Inspect the fields and definitions actually available in the account before calculating rates. Views divided by reach is not a measured rewatch rate. [Historical Reels announcement](https://about.fb.com/news/2023/04/instagram-reels-trending-audio-and-gifts-updates/)

**TikTok:** an official support search excerpt indicates feature availability can depend on region/criteria, but the canonical article body was not readable in this review. Treat fields as optional until verified in the actual Studio surface; record unavailable fields explicitly. Keep organic analytics separate from advertising or Creator Rewards-qualified metrics rather than assuming equivalent populations. [Creator tools and TikTok Studio help](https://support.tiktok.com/en/using-tiktok/creating-videos/creator-tools-on-tiktok)

## Proposed timing pilot — exploratory only

This is not a validated best practice or minimum sample size, and adding it does not authorize publishing, generation or spending.

1. Propose eight matched pairs of fresh shorts (16 posts), at one post per day, comparing two practical slots defined in the audience's timezone. Preassign randomized, balanced slot order and balance weekday where feasible; record unavoidable imbalances.
2. Match duration, characters, topic, hook, quality, caption and audio as closely as practical. Log promotions, collaborations and distribution confounders. Different creative material remains a confounder even after matching; do not degrade quality to fit the pilot.
3. Preselect one primary metric with its exact native surface/denominator. Capture snapshots near 24 hours and seven days, recording actual age and capture delays. Analyze each platform separately using comparable windows and filters.
4. Compare within-pair differences and consistency across pairs, not just the biggest hit. Report counts, missing observations and uncertainty. Tiny counts are inconclusive; repeat before proposing any default change. Do not change video quality or production method based on one post.

No production experiment has been executed by this document. Any later experiment or workflow change needs separate review and authorization.
