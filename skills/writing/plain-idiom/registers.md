# Registers and swaps

Grouped by source register. Swaps are suggestions, not mandates — often the better fix is to
delete the clause entirely, because the metaphor was doing the work of a missing thought.

---

## 1. American ball sports

The largest and least portable group. Baseball, American football and basketball. Assume no
comprehension outside North America.

**Baseball**

| Instead of | Try |
| --- | --- |
| ballpark figure / in the ballpark | rough estimate / roughly right |
| step up to the plate | take it on |
| touch base | check in, have a quick chat |
| out of left field | unexpected, from nowhere |
| home run / knocked it out of the park | big win, went very well |
| swing for the fences | go for the ambitious version |
| curveball | surprise, complication |
| strike out / three strikes | fail, third failure |
| bottom of the ninth / ninth inning | very late, nearly out of time |
| covering all the bases | covering everything |
| right off the bat | straight away |
| a whole new ball game | a different problem entirely |
| pinch hit | stand in, cover for |
| rain check | put it off, come back to it |

**American football**

| Instead of | Try |
| --- | --- |
| handoff | handover (UK usage is fine and clearer) |
| punt on it / punt to next sprint | defer it, push it back |
| Hail Mary | long shot, last resort |
| move the goalposts | change the requirements |
| game plan / playbook | plan, approach, runbook |
| quarterback (verb) | lead, coordinate |
| fumble / drop the ball | mishandle, miss |
| end run around | bypass, go around |
| down to the wire | right up to the deadline |
| blitz | concentrated push |
| in the red zone | close to done |
| Monday-morning quarterbacking | hindsight, second-guessing |

**Basketball and other**

| Instead of | Try |
| --- | --- |
| slam dunk | certain, obviously right |
| full-court press | all-out effort, sustained pressure |
| jump ball | too close to call |
| par for the course (golf) | typical, expected |
| below par / up to par (golf) | below standard / good enough |
| the ball's in their court (tennis) | it's with them now, waiting on them |
| down to the last lap (motorsport) | nearly finished |
| level playing field | fair, same rules for everyone |
| ahead of the curve | early, ahead of others |

## 2. British sport — do not substitute into this

Listed so you recognise them, not so you use them. Equally opaque internationally.

Cricket: *sticky wicket, knocked for six, on the back foot / front foot, played a straight
bat, stumped, bowled over, hit for six, good innings, off one's own bat, close of play,
batting above your average.*
Boxing: *below the belt, throw in the towel, on the ropes, saved by the bell, punch above
your weight, roll with the punches.*
Horse racing: *front runner, home straight, also-ran, neck and neck, across the board, down
to the wire, hands down, run its course.*
Snooker/darts/rugby: *behind the eight ball, snookered, double top, into touch, kicked into
the long grass.*

## 3. War, battle and violence

Two problems: comprehension is usually fine, but the *framing* isn't. Adversarial, urgent,
zero-sum, heroic. Worth rewriting the thought rather than swapping the word.

| Instead of | Try |
| --- | --- |
| war room | incident channel, ops room, situation review |
| battle-tested / battle-hardened | proven in production, well exercised |
| in the trenches | doing the day-to-day work |
| on the front line | customer-facing, first response |
| silver bullet | single fix, easy answer |
| death march | sustained overtime, unrealistic schedule |
| fire drill | urgent unplanned work, scramble |
| take no prisoners | uncompromising |
| bite the bullet | accept the cost, get on with it |
| scorched earth | complete rewrite, start again |
| pick your battles | choose what's worth pushing on |
| under fire / taking flak | under criticism |
| rally the troops | get everyone behind it |
| land grab / turf war | overlapping ownership, boundary dispute |
| nuke it / nuke from orbit | delete and rebuild |
| shoot down (an idea) | reject, argue against |
| bulletproof | reliable, hard to break |
| we killed that feature | we removed / retired that feature |
| hang (of a UI) | stops responding |
| hit (a button) | select, click, choose |
| a post-mortem | a review, a retro, an incident review |

### Violence-adjacent terms that are fine

These are technical terms of art with no accurate synonym. Leave them:

`kill` / `kill -9` / `SIGKILL`, `abort()`, `terminate` (an instance), `execute` (a query,
a process), `attack surface`, `threat model`, `blast radius`, `smoke test`, `crash`,
`deadlock`, `starvation`, `fail-fast`, `circuit breaker`, `chaos engineering`, `dead letter
queue`, `killer feature` is *not* on this list — that one's figurative.

Rule: if a reader would look for it in a man page, keep it. If it only appears in prose,
swap it.

### Terms with an established replacement

`whitelist` / `blacklist` → `allowlist` / `denylist` or rewrite ("allow requests from…").
`master` / `slave` → `primary`/`replica`, `controller`/`node`, `main` (git).
`sanity check` → `check`, `quick check`, `confidence check`.
`dummy value` → `placeholder`.
`grandfathered` → `exempt`, `pre-existing`.
When the term is a real API name or keyword, mention it once in code font, then use the plain
term in prose.

## 4. Hunting, shooting, fishing, farming

Less charged, still culture-bound and often unnecessary.

*Take a stab at, take a shot at, a long shot, magic bullet, shotgun approach, red herring,
fishing expedition, cast a wide net, a shot across the bows, low-hanging fruit, herding cats,
cash cow, sacred cow, beat a dead horse, flogging a dead horse, pets vs cattle* (Google
specifically calls this last one out), *put out to pasture, bell the cat.*

Swaps: *try, attempt, unlikely, broad search, distraction, easy wins, difficult to
coordinate, high-margin product, untouchable assumption, keep arguing a settled point.*

## 5. Management-speak — dead metaphors

Mostly metaphors that have decayed into vagueness. The [GOV.UK words-to-avoid
list](https://www.gov.uk/guidance/style-guide/a-to-z-of-gov-uk-style#words-to-avoid) is the
authority here; it bans these outright on the basis that they're too general to mean
anything.

| Instead of | Try |
| --- | --- |
| drive (adoption, change) | increase, cause, encourage |
| unlock (value, potential) | make possible, enable — or say what actually happens |
| deliver | make, build, provide, send |
| leverage | use |
| deep dive | detailed look, investigation |
| robust | say what it actually withstands |
| ring-fence | protect, set aside |
| landscape / ecosystem | the set of tools, the market, the systems |
| going forward | from now on — or delete |
| key (learnings, stakeholders) | important — or delete |
| double-click on that | look at it in more detail |
| circle back | come back to it |
| align on | agree |
| socialise (an idea) | share, discuss |
| bandwidth | time, capacity |
| north star | goal |
| move the needle | make a measurable difference |
| boil the ocean | try to do everything at once |
| eat the elephant / one bite at a time | break it into pieces |
| table stakes | the minimum, a basic requirement |
| skin in the game | a stake in the outcome |
| take it offline | discuss it separately |

## 6. Ableist figures of speech

Cheap to fix, and Google's guidance groups them with the rest.

*crazy / insane* (outliers, numbers) → *baffling, surprising, unusually large*
*blind to / turn a blind eye* → *ignoring, not accounting for*
*cripples, crippling* → *severely slows, degrades*
*dumb (terminal excepted), lame* → *simple, basic, weak*
*tone deaf* → *misjudged*
*paralysed* → *stalled, blocked*
*OCD about* → *particular about, meticulous*

## 7. Other US defaults worth catching

- **Dates** — `07/04/2026` is ambiguous. Use `4 July 2026` or ISO `2026-07-04`.
- **Units** — miles, feet, °F, US gallons, US billions in older text. Prefer SI or state both.
- **Currency and tax** — 401(k), IRS, ZIP code, "the holidays", Thanksgiving, "Q4 push
  before the holidays". Say *end of year* if that's what you mean.
- **"Football"** — ambiguous by hemisphere. Name the code or avoid.
- **Spelling** — organise/organize, licence/license, -ise vs -ize. Note that Oxford English
  uses -ize; the GOV.UK house style uses -ise. Pick one and be consistent; don't change
  spellings inside code, API names, or CSS (`color`, `serialize`, `Authorization`).
- **Legalisms** — "First Amendment", "due process", "at-will" assume US law.

---

## Sources and further reading

- [Google developer documentation style guide — Write inclusive documentation](https://developers.google.com/style/inclusive-documentation) — the figurative-language and violent-language sections, and the "term of art vs metaphorical extension" rule.
- [Google — Write for a global audience](https://developers.google.com/style/translation) — "avoid being too culturally specific to the US… sports, and figures of speech".
- [Google — Word list](https://developers.google.com/style/word-list) — per-term rulings.
- [Microsoft Writing Style Guide — Global communications, writing tips](https://learn.microsoft.com/en-us/style-guide/global-communications/writing-tips) — "avoid idioms, colloquial expressions, and culture-specific references".
- [GOV.UK A to Z style guide](https://guidance.publishing.service.gov.uk/writing-to-gov-uk-standards/style-guides/a-to-z-style-guide/) and [words to avoid](https://civilservice.blog.gov.uk/2022/08/16/a-simple-guide-on-words-to-avoid-in-government/) — the management-speak list, British.
- [Inside GOV.UK — avoiding words to avoid](https://insidegovuk.blog.gov.uk/2014/04/11/avoiding-words-to-avoid/) — the reasoning behind it.
- [Home Office — designing for limited English](https://design.homeoffice.gov.uk/design-and-content/content/designing-for-limited-english).
- Flusberg, Matlock & Thibodeau (2018), ["War metaphors in public discourse"](https://www.stephenflusberg.com/uploads/2/6/9/4/26942597/2018_flusberg_matlock_thibodeau_-_war_metaphors.pdf), *Metaphor and Symbol* — evidence that war framing changes which solutions people favour.
- Edmond Weiss, *The Elements of International English Style* (2005) — book-length treatment of writing English for non-native readers.
- John Kohl, *The Global English Style Guide* (SAS, 2008) — controlled-English rules, translation-oriented.
- [Foothold America — US business jargon glossary](https://www.footholdamerica.com/blog/us-business-jargon-glossary/) — useful as a raw source list of US-specific business idiom.
