# v1.8 build notes

## Flags carried from the metadata research
- Sturridge: Wikipedia never states a retirement, so yearsActive end year 2022 is inferred from
  his last club. Treat as unconfirmed.
- Kante: caps/goals will keep rising while he is active. Figure is as of Oct 2026.
- Honours year style: content.json uses a single year, "Champions League (Real Madrid, 2014)",
  not a season span. Research came back in both formats; normalise to single year.
- Wilshere: Arsenal also won Community Shields in 2015 and 2017 while he was contracted, but
  Wikipedia credits him only with 2014. Using the Wikipedia line.

## Still to produce
- story paragraphs x86 (voice matched to Delap/Bramble/Bullard: 90-150 words, no em dashes)
- youtube link x86, verified via the oEmbed endpoint so dead links and wrong-person matches fail loudly
- aliases x86 (derivable: full name lowercased, plus surname, plus accented variant)
- numbers x86 (derivable: "N goals in M caps for Country")
- kickoff x86 (derivable: "I was born on the Nth of Month YYYY. I played M times for my country, scoring N goals.")

## More research flags
- Pires: the Wikipedia lead says three FA Cups, the honours list says two (2003, 2005). He was
  injured for the 2002 final. Using two, which matches the honours list.
- Britton: yearsActive is ambiguous. He retired from the professional game in 2018 but then made
  11 appearances for Llanelli and Ammanford in the Welsh pyramid up to 2021. Using 1999-2018.
  His FAW Premier Cup wins are dropped as a regional cup, not a major honour.
- Delph: City also won League Cups and an FA Cup while he was registered 2015-19, but Wikipedia
  credits him with only the two league titles and his involvement could not be verified. Using
  the two, which matches his picked clue "I won the Premier League twice".

## Two contradictions worth recording
- Jagielka honours array is genuinely EMPTY. That is correct and matches his picked clue
  "I played six hundred and fifty nine league games and never won a single trophy."
- Jagielka going in goal against Arsenal in Dec 2006 and saving from van Persie: an earlier
  fact-check CONFIRMED this, a later agent says it is not in the article and may be invention.
  It does NOT appear in his five picked clues, so nothing ships on it. Do not reinstate without
  a primary source.
- Valencia: the South American appearance record could not be found in his article by one agent,
  but another independently confirmed Willian overtook him 326 to 325 in May 2025, which implies
  the record was real. His picked clue already says "I held" rather than "I hold".
- Valencia position: infobox lists right winger first, then right-back. Using Winger. Right-back
  is equally defensible for his later United years.
