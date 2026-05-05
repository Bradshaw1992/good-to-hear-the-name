-- Reject display names containing common slurs/profanity.
-- Strips non-letters first (so "f u c k" or "fuck.123" are still caught).
-- Run this in the SQL Editor of the gthn project.

alter table public.scores
  drop constraint if exists scores_clean_name;

alter table public.scores
  add constraint scores_clean_name check (
    lower(regexp_replace(display_name, '[^a-zA-Z]', '', 'g'))
    !~ '(fuck|shit|cunt|wank|bollock|bastard|prick|cock|twat|arse|slut|whore|bitch|nigger|nigga|faggot|retard|spastic|paki|chink|gook|tranny|nazi|hitler|rape|pedo|paedo)'
  );
