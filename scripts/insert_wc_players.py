#!/usr/bin/env python3
"""Insert 18 new WC-themed players into content.json (Days 54-71).

Replaces existing roster at indices 53-70 with the new picks:
Wood, Mascherano, Sneijder, Griezmann, Young, Morientes, Giroud, Gyan,
De Jong, Lucio, Krul, Anelka, Amrabat, Chiellini, Pepe, Mustafi, Koulibaly, Gattuso.

Day 72 (index 71, Ricardo Carvalho) is left in place pending user's pick for the
gap created by removing Pires.

Writes to both Android (app/src/main/assets/content.json) and iOS
(ios/GoodToHearTheName/GoodToHearTheName/Resources/content.json) mirrors.

Run: scripts/.venv/bin/python scripts/insert_wc_players.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANDROID = os.path.join(ROOT, "app/src/main/assets/content.json")
IOS = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/content.json")

START_INDEX = 53  # Day 54

NEW_PLAYERS = [
    # Day 54 — Chris Wood (NZ)
    {
        "id": "chris_wood",
        "name": "Chris Wood",
        "country": "New Zealand",
        "countryFlag": "🇳🇿",
        "years": "2008–",
        "aliases": ["chris wood", "wood"],
        "clues": [
            "I played at the 2010 World Cup, playing 3 games and scoring 0 goals for my country. I'm here again at the 2026 World Cup.",
            "It was at Leeds and later Burnley that I became a more prolific goalscorer.",
            "I have never lost a World Cup game (as of the 18th of June 2026).",
            "I was the Championship's Golden Boot winner in 2017, scoring 27 goals for a club that hadn't been in the Premier League since 2004.",
            "I scored a Premier League hat-trick on Boxing Day 2023 for Nottingham Forest against my old club Newcastle, aged 31, helping save Forest from relegation that season."
        ],
        "image": "chris_wood.jpg",
        "silhouette": "chris_wood.jpg",
        "position": "Striker",
        "yearsActive": "2008–",
        "story": "New Zealand's all-time top goalscorer and the rare All Whites hero who built a decade-long Premier League career out of nothing flashy: relentless work-rate, a neat first touch, and a knack for the deflected goal. His World Cup highlight was being part of the 2010 team that drew all three games and went home undefeated. After loan-merry-go-round years at West Brom and stops at Leicester (Championship promotion), Burnley, Newcastle and Forest, he's one of the longest-running PL strikers from outside the Big Five nations.",
        "youtube": "https://www.youtube.com/watch?v=gghp-RkSiRg",
        "clubs": ["West Brom (youth)", "Barnsley", "Brighton", "Birmingham", "Bristol City", "Millwall", "Leicester", "Ipswich", "Leeds", "Burnley", "Newcastle", "Nottingham Forest"],
        "honours": ["Championship Golden Boot (2017, Leeds)", "Football League Cup (2013, with West Brom on loan)", "All-time New Zealand top scorer"],
        "numbers": "41 goals in 75+ caps for New Zealand",
        "didYouKnow": [
            "He had seven loan spells before he turned 24, more than almost any modern PL striker.",
            "His Boxing Day 2023 Forest hat-trick vs Newcastle was against the club that sold him to Forest months earlier.",
            "Still actively scoring at 33, currently leading the line for Nottingham Forest."
        ]
    },
    # Day 55 — Javier Mascherano (Argentina)
    {
        "id": "mascherano",
        "name": "Javier Mascherano",
        "country": "Argentina",
        "countryFlag": "🇦🇷",
        "years": "2003–2020",
        "aliases": ["mascherano", "javier mascherano", "el jefecito"],
        "clues": [
            "I played in four World Cups (2006, 2010, 2014 and 2018), playing 19 games and scoring 0 goals.",
            "I won the Champions League twice for a Spanish club.",
            "I joined the Premier League in 2006, moving controversially to London, but played most of my PL football in the North West.",
            "I lost the 2014 World Cup Final to Germany in extra time.",
            "I was converted by Pep into a centre-back later on in my career."
        ],
        "image": "mascherano.jpg",
        "silhouette": "mascherano.jpg",
        "position": "Defensive Midfielder / Centre-Back",
        "yearsActive": "2003–2020",
        "story": "Argentina's iron-lung defensive midfielder turned centre-back, Mascherano was the spine of a generation that never quite delivered the World Cup, runners-up in 2014, then knocked out by France in 2018. Started at River Plate, made his Argentina debut before his club debut, moved through Corinthians and West Ham (the Tevez-and-Mascherano summer at Upton Park is still unexplained), Liverpool under Benítez, then eight years at Barcelona where Guardiola converted him into a defender. Messi adored him, and his last-man tackle on Robben in the 2014 semi-final is still studied in coaching clinics.",
        "youtube": "https://www.youtube.com/watch?v=FSvtwgeB4XM",
        "clubs": ["River Plate", "Corinthians", "West Ham", "Liverpool", "Barcelona", "Hebei China Fortune", "Estudiantes"],
        "honours": ["Olympic Gold (2004, 2008)", "5x La Liga", "2x Champions League", "Copa America runner-up (2007, 2015, 2016)"],
        "numbers": "147 caps for Argentina, no goals",
        "didYouKnow": [
            "First Argentine to win two Olympic gold medals.",
            "Made his Argentina debut at 19 before his first senior club appearance.",
            "Tore his anus making a last-man tackle on Robben in the 2014 WC semi-final and continued playing."
        ]
    },
    # Day 56 — Wesley Sneijder (Netherlands)
    {
        "id": "sneijder",
        "name": "Wesley Sneijder",
        "country": "Netherlands",
        "countryFlag": "🇳🇱",
        "years": "2002–2019",
        "aliases": ["sneijder", "wesley sneijder"],
        "clues": [
            "I played in three World Cups (2006, 2010 and 2014), scoring 6 goals across 15 games.",
            "I came second in the Ballon d'Or vote to Messi in the same year that I lost a World Cup final.",
            "I am my country's most capped player with 134 caps and 31 goals.",
            "I was sold by one of the big clubs to make way for the incoming Ronaldo.",
            "I won the treble in Italy under Mourinho."
        ],
        "image": "sneijder.jpg",
        "silhouette": "sneijder.jpg",
        "position": "Attacking Midfielder",
        "yearsActive": "2002–2019",
        "story": "The Netherlands' most-capped player and 2010 World Cup tragic hero. Sneijder was the brain of the Inter treble side under Mourinho and dragged the Oranje to the 2010 World Cup final almost single-handedly: five goals, joint top scorer, lost the final 1-0 to Spain. Started at Ajax, big-money move to Real Madrid, sold cheap to Inter (one of the worst transfer windows in Madrid history), then Galatasaray, Nice and Al-Gharafa. Famously pipped to the 2010 Ballon d'Or by Messi by a whisker. Retired 2019 with a flair-meets-grit legacy.",
        "youtube": "https://www.youtube.com/watch?v=brkLQIu14lM",
        "clubs": ["Ajax", "Real Madrid", "Inter Milan", "Galatasaray", "Nice", "Al-Gharafa", "Utrecht"],
        "honours": ["Eredivisie", "La Liga", "Serie A (3x)", "Champions League (2010)", "Coppa Italia (3x)", "Süper Lig"],
        "numbers": "134 caps and 31 goals for the Netherlands",
        "didYouKnow": [
            "His Inter treble-winning side was the last Italian club to win the Champions League.",
            "Married a Dutch TV host who's still on screen every week.",
            "Sold by Real Madrid to fund the marquee signings of Ronaldo and Kaká."
        ]
    },
    # Day 57 — Antoine Griezmann (France)
    {
        "id": "griezmann",
        "name": "Antoine Griezmann",
        "country": "France",
        "countryFlag": "🇫🇷",
        "years": "2009–",
        "aliases": ["griezmann", "antoine griezmann", "grizou"],
        "clues": [
            "I played in three World Cups (2014, 2018 and 2022), scoring 6 goals across 17 games.",
            "I am a World Cup winner, even though I was rejected by every academy from my country for being too small as a teenager.",
            "I was signed for a huge fee by a club playing in the same league.",
            "I'm one of only three players to score in a World Cup final, a European Championship final and a Champions League final.",
            "I'm one of my country's all-time top scorers, behind only Giroud, Henry and Mbappé."
        ],
        "image": "griezmann.jpg",
        "silhouette": "griezmann.jpg",
        "position": "Forward",
        "yearsActive": "2009–",
        "story": "France's relentless forward who slipped through every French academy as a teenager (rejected by Lyon, Auxerre, Saint-Étienne) and moved at 14 to Real Sociedad, where he became their best player. Atlético Madrid signed him, where he scored 100+ goals, won the Europa League, lost two Champions League finals and earned a brief disastrous spell at Barcelona. Returned to Atlético. Internationally: golden generation 2014–22, won WC 2018, lost 2022 final to Argentina, lost Euro 2016 final at home to Portugal. The most decorated player of his era who never quite got the Ballon d'Or.",
        "youtube": "https://www.youtube.com/watch?v=1DD-QNbnTMI",
        "clubs": ["Real Sociedad", "Atlético Madrid", "Barcelona", "Atlético Madrid"],
        "honours": ["World Cup (2018)", "Europa League (2018)", "La Liga", "Copa America runner-up", "Euro 2016 Golden Boot"],
        "numbers": "44 goals in 137+ caps for France",
        "didYouKnow": [
            "Lived with the José family in San Sebastián from age 14 because his parents couldn't move with him.",
            "Almost signed for Manchester United in 2017 — Atlético's transfer ban saved the move.",
            "Has a tattoo of his daughter's birth chart on his back."
        ]
    },
    # Day 58 — Ashley Young (England)
    {
        "id": "ashley_young",
        "name": "Ashley Young",
        "country": "England",
        "countryFlag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "years": "2003–",
        "aliases": ["ashley young", "young"],
        "clues": [
            "I played at the 2018 World Cup, playing 3 games and scoring 0 goals for my country.",
            "I was PFA Young Player of the Year at Aston Villa before being signed by a Premier League giant.",
            "I have won the Premier League and Serie A.",
            "I lost the 2018 World Cup semi-final to Croatia in extra time.",
            "I was signed by Manchester United for £17 million in 2011."
        ],
        "image": "ashley_young.jpg",
        "silhouette": "ashley_young.jpg",
        "position": "Winger / Wing-back",
        "yearsActive": "2003–",
        "story": "A career that refused to die. Young burst out at Watford under Aidy Boothroyd, broke through at Aston Villa with PFA Young Player of the Year honours, then Manchester United (£17m signing, on-and-off career, frequently mocked for diving), then Inter Milan in his mid-30s where he won Serie A under Conte, before returning to England for Aston Villa swansong years and now Everton. World Cup 2018 with Gareth Southgate's semi-final England side. Renaissance career as a wing-back is one of football's quieter modern miracles.",
        "youtube": "https://www.youtube.com/watch?v=qAhrhOuI7Z4",
        "clubs": ["Watford", "Aston Villa", "Manchester United", "Inter Milan", "Aston Villa", "Everton"],
        "honours": ["Premier League (2013)", "Europa League (2017)", "Serie A (2021)", "England 2018 WC semi-final squad"],
        "numbers": "39 caps and 7 goals for England",
        "didYouKnow": [
            "PFA Young Player of the Year at Villa, then never quite Young Player again.",
            "Won Serie A in his first season at Inter after leaving Manchester United on a free.",
            "Holds the unofficial record for most diving accusations in a single PL season, depending on who you ask."
        ]
    },
    # Day 59 — Fernando Morientes (Spain)
    {
        "id": "morientes",
        "name": "Fernando Morientes",
        "country": "Spain",
        "countryFlag": "🇪🇸",
        "years": "1993–2010",
        "aliases": ["morientes", "fernando morientes", "nando"],
        "clues": [
            "I played at the 2002 World Cup, scoring 3 goals in 5 games for my country.",
            "I was a Premier League failure after a £6.3 million signing in 2005.",
            "I won the Champions League with the club that has won it most times.",
            "I played upfront for my international team with Raúl.",
            "I was replaced as first-choice striker at club level by the Brazilian Ronaldo."
        ],
        "image": "morientes.jpg",
        "silhouette": "morientes.jpg",
        "position": "Striker",
        "yearsActive": "1993–2010",
        "story": "The cult Spanish striker whose strike rate vs the Galácticos was actually better than Raúl's, but Raúl had the captain's armband. Morientes won three Champions Leagues in five years with Madrid (1998, 2000, 2002), was loaned to Monaco in 2003-04 where he scored the goal that knocked Real Madrid out of the Champions League en route to the final, then back to Real before a £6.3m move to Liverpool in 2005 (8 PL goals total, Premier League flop). Recovered at Valencia, retired in 2010. Spain hero of the 2002 World Cup with three goals.",
        "youtube": "https://www.youtube.com/watch?v=HpByhEoQ9k8",
        "clubs": ["Albacete", "Zaragoza", "Real Madrid", "Monaco (loan)", "Liverpool", "Valencia", "Marseille"],
        "honours": ["3x Champions League", "2x La Liga", "Intercontinental Cup", "Spanish Super Cup"],
        "numbers": "27 goals in 47 Spain caps",
        "didYouKnow": [
            "Scored for Real Madrid against Manchester United in the 2003 Champions League quarter-final.",
            "The next year, scored for Monaco against Real Madrid to knock his parent club out of the Champions League.",
            "His Liverpool teammates nicknamed him 'Nando' and he hated it."
        ]
    },
    # Day 60 — Olivier Giroud (France)
    {
        "id": "giroud",
        "name": "Olivier Giroud",
        "country": "France",
        "countryFlag": "🇫🇷",
        "years": "2005–",
        "aliases": ["giroud", "olivier giroud"],
        "clues": [
            "I played in three World Cups (2014, 2018 and 2022), scoring 4 goals across 17 games.",
            "I won Ligue 1 with Montpellier in 2012, one of the most unexpected title wins in French football history.",
            "I won Serie A with AC Milan in 2022, in my first season at the club after eight years in London.",
            "My scorpion kick against Crystal Palace on New Year's Day 2017 won the FIFA Puskás Award for goal of the year.",
            "I was my country's all-time leading scorer when I retired from international football. Mbappé has just overtaken me."
        ],
        "image": "giroud.jpg",
        "silhouette": "giroud.jpg",
        "position": "Striker",
        "yearsActive": "2005–",
        "story": "France's record international goalscorer at the time of his retirement, Giroud is the slow-burn striker who built a career out of being underrated. Late bloomer through Tours, Istres, then Montpellier (Ligue 1 title 2012). Arsenal years (Europa League 2020), Chelsea years (Champions League 2021), AC Milan (Serie A 2022), now LAFC in MLS. Internationally: won WC 2018 without scoring a single goal in the tournament (unique among winning strikers), then runner-up in 2022 where he finally scored crucial goals on the run to the final. The everyman finisher.",
        "youtube": "https://www.youtube.com/watch?v=IACFxcghqQ8",
        "clubs": ["Grenoble", "Istres", "Tours", "Montpellier", "Arsenal", "Chelsea", "AC Milan", "LAFC"],
        "honours": ["World Cup (2018)", "Ligue 1 (2012)", "Serie A (2022)", "Champions League (2021)", "Europa League (2020)", "3x FA Cup"],
        "numbers": "57 international goals in 137 caps",
        "didYouKnow": [
            "His scorpion kick vs Crystal Palace won the FIFA Puskás Award 2017.",
            "Played in Ligue 2 for Tours at age 23, the same age Henry was at Barcelona.",
            "Won the 2018 World Cup without scoring a single goal in the tournament."
        ]
    },
    # Day 61 — Asamoah Gyan (Ghana)
    {
        "id": "asamoah_gyan",
        "name": "Asamoah Gyan",
        "country": "Ghana",
        "countryFlag": "🇬🇭",
        "years": "2003–2022",
        "aliases": ["asamoah gyan", "gyan", "baby jet"],
        "clues": [
            "I played in three World Cups (2006, 2010 and 2014), scoring 6 goals across 11 games.",
            "I'm my country's all-time leading scorer with 51 international goals.",
            "I played for Sunderland in the Premier League, scoring 10 league goals in my first season.",
            "I missed a penalty in the last minute of a World Cup quarter-final after the opposition had been reduced to ten men for a handball on the line.",
            "I featured on a song called 'African Girls' with Castro while still playing, and it went viral in Ghana."
        ],
        "image": "asamoah_gyan.jpg",
        "silhouette": "asamoah_gyan.jpg",
        "position": "Striker",
        "yearsActive": "2003–2022",
        "story": "Africa's all-time World Cup top scorer (6 goals across three tournaments) and the man at the heart of football's cruellest moment: the Uruguay quarter-final 2010, when his last-minute penalty hit the bar after the handball on the line. Career took him through Udinese, Rennes, Sunderland (Premier League cult years), then a controversial massive move to Al Ain in the UAE in 2011 where he became one of the highest-paid footballers in world football, Shanghai SIPG, Kayserispor and back to Ghana. Captain of the Black Stars for a decade.",
        "youtube": "https://www.youtube.com/watch?v=tDpx9GGH79I",
        "clubs": ["Liberty Professionals", "Udinese", "Modena (loan)", "Rennes", "Sunderland", "Al Ain", "Shanghai SIPG", "Kayserispor", "NorthEast United", "Legon Cities"],
        "honours": ["Africa Cup of Nations runner-up (2010, 2015)", "African Player of the Year nominee"],
        "numbers": "51 goals in 109 caps for Ghana",
        "didYouKnow": [
            "Made his Ghana debut at 17 and was captain by 24.",
            "Became one of the world's highest-paid footballers at Al Ain on a reported $300k/week.",
            "Africa's all-time World Cup top scorer with six goals across three tournaments."
        ]
    },
    # Day 62 — Nigel De Jong (Netherlands)
    {
        "id": "nigel_de_jong",
        "name": "Nigel De Jong",
        "country": "Netherlands",
        "countryFlag": "🇳🇱",
        "years": "2002–2019",
        "aliases": ["nigel de jong", "de jong"],
        "clues": [
            "I played in two World Cups (2010 and 2014), playing 11 games and scoring 0 goals.",
            "I won the Eredivisie and KNVB Cup at Ajax before moving to Hamburg in 2006.",
            "I played for Manchester City for a number of years before winning Serie A with AC Milan.",
            "I lost the 2010 World Cup final.",
            "In that final, I was somehow not sent off for a kung-fu kick on the chest of Xabi Alonso."
        ],
        "image": "nigel_de_jong.jpg",
        "silhouette": "nigel_de_jong.jpg",
        "position": "Defensive Midfielder",
        "yearsActive": "2002–2019",
        "story": "The Netherlands' most controversial midfielder. The man who kung-fu kicked Xabi Alonso in the chest during the 2010 World Cup final and somehow only saw a yellow card. Career: Ajax youth, Hamburg, Manchester City (signed by Mark Hughes, kept under Mancini), AC Milan (Serie A 2011), LA Galaxy, Mainz, Galatasaray, Al-Shahania. Always a destroyer, never a finisher. 2014 World Cup semi-final at 31, 81 caps. The dark prince of Dutch football, beloved by City fans for his uncompromising tackles in the Tevez/Mancini era.",
        "youtube": "https://www.youtube.com/watch?v=uwqLn0F8jXk",
        "clubs": ["Ajax", "Hamburg", "Manchester City", "AC Milan", "LA Galaxy", "Mainz", "Galatasaray", "Al-Shahania"],
        "honours": ["Premier League (2012, with City after he'd left)", "Eredivisie", "KNVB Cup", "MLS Western Conference"],
        "numbers": "81 caps for the Netherlands, 1 goal",
        "didYouKnow": [
            "Of Dutch, Surinamese and Indonesian heritage.",
            "Famously broke Stuart Holden's leg in a USA-Netherlands friendly with a two-footed tackle.",
            "Came through the Ajax academy alongside Sneijder, van der Vaart and Babel."
        ]
    },
    # Day 63 — Lúcio (Brazil)
    {
        "id": "lucio",
        "name": "Lúcio",
        "country": "Brazil",
        "countryFlag": "🇧🇷",
        "years": "1997–2020",
        "aliases": ["lucio", "lúcio"],
        "clues": [
            "I played in three World Cups (2002, 2006 and 2010), playing 17 games and scoring 0 goals.",
            "I have won a World Cup and a Champions League.",
            "I have also lost a Champions League final, in which Zidane famously scored a spinning volley from outside the box.",
            "Both the manager of my World Cup win and the manager of my Champions League win were managers at Chelsea, but I never played for them.",
            "I won the treble in 2010."
        ],
        "image": "lucio.jpg",
        "silhouette": "lucio.jpg",
        "position": "Centre-Back",
        "yearsActive": "1997–2020",
        "story": "Brazil's no-nonsense centre-back from the 2002 World Cup-winning team. Lúcio formed a defensive partnership with Roque Júnior that stood firm in Japan/Korea under Big Phil Scolari. Career: Internacional, Bayer Leverkusen (famously losing the Bundesliga, Champions League and DFB-Pokal finals in 2002, the 'Neverkusen' team), Bayern Munich (multiple Bundesliga titles), Inter Milan under Mourinho (treble 2010), Juventus, São Paulo, Palmeiras, FC Goa, Brasiliense. 105 Brazil caps, two Copa Americas, three World Cups. Underrated outside Germany and Italy.",
        "youtube": "https://www.youtube.com/watch?v=ENWua9XRNyI",
        "clubs": ["Internacional", "Bayer Leverkusen", "Bayern Munich", "Inter Milan", "Juventus", "São Paulo", "Palmeiras", "FC Goa", "Brasiliense"],
        "honours": ["World Cup (2002)", "Champions League (2010)", "Serie A (2010)", "3x Bundesliga", "2x Copa America"],
        "numbers": "105 caps for Brazil, 4 goals",
        "didYouKnow": [
            "Lost three finals in 2002: Bundesliga, Champions League and DFB-Pokal, the 'Neverkusen' curse.",
            "Eight years later, won the Champions League final for Inter against his old club Bayern Munich.",
            "Scored a long-range free-kick in the 2010 Champions League quarter-final against CSKA Moscow."
        ]
    },
    # Day 64 — Tim Krul (Netherlands)
    {
        "id": "tim_krul",
        "name": "Tim Krul",
        "country": "Netherlands",
        "countryFlag": "🇳🇱",
        "years": "2005–",
        "aliases": ["tim krul", "krul"],
        "clues": [
            "I played at the 2014 World Cup, playing 1 game and conceding 0 goals.",
            "I won the Championship with Norwich City in 2019, after a season-long loan that became permanent.",
            "I joined Newcastle United at 17 from ADO Den Haag, and made over 150 Premier League appearances for them.",
            "I was substituted on in the 120th minute of a World Cup quarter-final, and saved two penalties.",
            "I'm a Dutch goalkeeper with 15 international caps, mostly playing back-up to Cillessen."
        ],
        "image": "tim_krul.jpg",
        "silhouette": "tim_krul.jpg",
        "position": "Goalkeeper",
        "yearsActive": "2005–",
        "story": "Football's most famous one-minute World Cup hero. Van Gaal substituted starting keeper Cillessen ON for Krul in the 120th minute of extra time of the 2014 quarter-final vs Costa Rica, purely for the penalty shootout. Krul saved two. Career: Newcastle United (10+ years, including their best Premier League season as 5th in 2012), Norwich (Premier League and Championship years), AZ Alkmaar, Luton Town. Quietly excellent shot-stopper, never a giant, but a top-half-of-the-Premier-League career.",
        "youtube": "https://www.youtube.com/watch?v=XMF6uu_HpZk",
        "clubs": ["ADO Den Haag (youth)", "Newcastle", "Falkirk (loan)", "Carlisle (loan)", "AZ (loan)", "Brighton (loan)", "Ajax (loan)", "Norwich City", "AZ Alkmaar", "Luton Town"],
        "honours": ["Championship (2019, Norwich)", "Eredivisie cup (2024)"],
        "numbers": "15 caps for the Netherlands",
        "didYouKnow": [
            "Van Gaal's WC 2014 sub-on for penalties was a masterstroke. Krul had been training for it.",
            "Had loans at Carlisle United and Falkirk before he ever played for Newcastle.",
            "Played for 10 different clubs across his career, including five loan spells before age 22."
        ]
    },
    # Day 65 — Nicolas Anelka (France)
    {
        "id": "anelka",
        "name": "Nicolas Anelka",
        "country": "France",
        "countryFlag": "🇫🇷",
        "years": "1995–2014",
        "aliases": ["anelka", "nicolas anelka", "le sulk"],
        "clues": [
            "I played at the 2010 World Cup, playing 1 game and scoring 0 goals for my country.",
            "I won a Champions League but also lost a Champions League final.",
            "I was sent home from a World Cup after a row with my coach.",
            "I have won the Premier League with two different clubs.",
            "I took the deciding penalty in the 2008 Champions League final for Chelsea against Manchester United, and missed."
        ],
        "image": "anelka.jpg",
        "silhouette": "anelka.jpg",
        "position": "Striker",
        "yearsActive": "1995–2014",
        "story": "Football's 'Le Sulk', the gifted French striker whose career took him through every elite club without ever feeling at home. Arsenal (£500k from PSG, sold for £22m to Real Madrid 18 months later, funding the new training ground), Real Madrid (CL 2000), back to PSG, Liverpool, Manchester City, Fenerbahçe, Bolton (genuinely loved his Bolton spell), Chelsea (Premier League 2010), Shanghai Shenhua, Juventus, West Brom, Mumbai City. The famous 2010 World Cup row with Domenech, sent home, French team went on strike, Anelka banned 18 games. Fast, sullen, talented, never satisfied.",
        "youtube": "https://www.youtube.com/watch?v=fdlRY1GXRhs",
        "clubs": ["PSG", "Arsenal", "Real Madrid", "PSG", "Liverpool (loan)", "Manchester City", "Fenerbahçe", "Bolton", "Chelsea", "Shanghai Shenhua", "Juventus", "West Brom", "Mumbai City"],
        "honours": ["2x Premier League (Arsenal 2002, Chelsea 2010)", "Champions League (2000)", "Euro 2000 with France", "3x FA Cup"],
        "numbers": "14 goals in 69 France caps",
        "didYouKnow": [
            "The Arsenal sale to Real Madrid (£500k to £22m) bankrolled Arsenal's training ground at London Colney.",
            "Sentenced to a 5-game ban for an antisemitic 'quenelle' celebration at West Brom in 2014.",
            "Played for 13 clubs in 19 years, including four in his last three seasons."
        ]
    },
    # Day 66 — Sofyan Amrabat (Morocco)
    {
        "id": "sofyan_amrabat",
        "name": "Sofyan Amrabat",
        "country": "Morocco",
        "countryFlag": "🇲🇦",
        "years": "2014–",
        "aliases": ["sofyan amrabat", "amrabat"],
        "clues": [
            "I played in two World Cups (2018 and 2022), playing 9 games and scoring 0 goals.",
            "I was born in the Netherlands and represented Dutch youth teams before switching to my parents' country at senior level.",
            "I was named Player of the Match against Spain in the 2022 World Cup Round of 16, when my country won on penalties.",
            "I later moved on loan to Manchester United.",
            "I was the heartbeat of the Moroccan side that became the first African team ever to reach a World Cup semi-final."
        ],
        "image": "sofyan_amrabat.jpg",
        "silhouette": "sofyan_amrabat.jpg",
        "position": "Defensive Midfielder",
        "yearsActive": "2014–",
        "story": "The Dutch-born Moroccan destroyer who emerged as one of the tournament's breakout stars at Qatar 2022. Career: Utrecht, Feyenoord, Club Brugge, Hellas Verona, Fiorentina (Conference League runners-up 2023), Manchester United (loan, didn't quite work), Fenerbahçe. The semi-final WC run with Morocco (beating Spain and Portugal en route) cemented his cult status, he ran 80km over the seven games. The reluctant heir to N'Golo Kanté's 'everywhere all at once' archetype.",
        "youtube": "https://www.youtube.com/watch?v=pQ48mznaySw",
        "clubs": ["Utrecht", "Feyenoord", "Club Brugge", "Hellas Verona", "Fiorentina", "Manchester United (loan)", "Fenerbahçe"],
        "honours": ["Africa Cup of Nations runner-up (2023)", "Conference League runner-up (2023)"],
        "numbers": "65+ caps for Morocco",
        "didYouKnow": [
            "Born in Huizen, Netherlands; represented Dutch youth teams before switching to Morocco.",
            "Older brother Nordin is also a footballer with Watford, Feyenoord and Anderlecht spells.",
            "Was on Liverpool's transfer shortlist before the Manchester United loan deal."
        ]
    },
    # Day 67 — Giorgio Chiellini (Italy)
    {
        "id": "chiellini",
        "name": "Giorgio Chiellini",
        "country": "Italy",
        "countryFlag": "🇮🇹",
        "years": "2000–2023",
        "aliases": ["chiellini", "giorgio chiellini"],
        "clues": [
            "I played in two World Cups (2010 and 2014), playing 6 games and scoring 0 goals.",
            "I lost two Champions League finals with Juventus.",
            "I was famously bitten in a World Cup.",
            "I controversially fouled a player in a European Championship final.",
            "I was awarded an Italian state honour, knighted by President Mattarella, for winning Euro 2020."
        ],
        "image": "chiellini.jpg",
        "silhouette": "chiellini.jpg",
        "position": "Centre-Back",
        "yearsActive": "2000–2023",
        "story": "Italy's iron centre-back captain who won nine consecutive Serie A titles with Juventus (2012-2020) and lifted Euro 2020 in his late thirties. Career: Livorno (youth), Fiorentina (loan), Juventus (16 years), then LA Galaxy MLS retirement years. Famously the bite-victim of Luis Suárez at WC 2014, and the shirt-puller of Bukayo Saka at the Euro 2020 final. Italy: missed Euro 2016 through injury, won Euro 2020, missed WC 2018 and 2022. One of the best defenders of his generation, beloved at Juve. Now Juventus board member.",
        "youtube": "https://www.youtube.com/watch?v=P2cZ8s87wAw",
        "clubs": ["Livorno", "Fiorentina (loan)", "Juventus", "LA Galaxy"],
        "honours": ["9x Serie A", "Euro 2020", "5x Coppa Italia"],
        "numbers": "117 caps for Italy, 8 goals",
        "didYouKnow": [
            "Has a Masters degree in Business Administration which he completed while playing.",
            "Lost two Champions League finals with Juventus (2015, 2017).",
            "Pulled Bukayo Saka's shirt in the 65th minute of the Euro 2020 final, conceding a yellow card."
        ]
    },
    # Day 68 — Pepe (Portugal)
    {
        "id": "pepe_portugal",
        "name": "Pepe",
        "country": "Portugal",
        "countryFlag": "🇵🇹",
        "years": "2001–2024",
        "aliases": ["pepe", "kepler"],
        "clues": [
            "I played in four World Cups (2010, 2014, 2018 and 2022), playing 13 games and scoring 1 goal.",
            "I scored in my last World Cup against Switzerland at age 39, becoming the oldest player ever to score in a World Cup knockout match.",
            "I won three Champions Leagues.",
            "I was banned for 10 games for an attack on a player in La Liga, including a stamp while he lay on the ground.",
            "I was known as one of the most physical and dirty players in European football, and Mourinho loved me."
        ],
        "image": "pepe_portugal.jpg",
        "silhouette": "pepe_portugal.jpg",
        "position": "Centre-Back",
        "yearsActive": "2001–2024",
        "story": "Brazil-born, Portugal-adopted, four-World-Cup centre-back. Marítimo, Porto (2 league titles), Real Madrid 2007-2017 (3 Champions Leagues), Beşiktaş, Porto again. Euro 2016 winner, 141 Portugal caps. Controversial in his Real Madrid years (red cards, on-pitch incidents), redeemed later as the experienced anchor of multiple Portugal generations. Played until age 41 at Porto. Often a Sergio Ramos counterpoint: the dirty cop.",
        "youtube": "https://www.youtube.com/watch?v=iAQRQv3-3iY",
        "clubs": ["Marítimo", "Porto", "Real Madrid", "Beşiktaş", "Porto"],
        "honours": ["Euro 2016", "3x Champions League", "2x La Liga", "5x Primeira Liga", "Nations League (2019)"],
        "numbers": "141 caps for Portugal, 8 goals",
        "didYouKnow": [
            "Held the record for oldest goalscorer in a WC knockout match at 39 years, 283 days.",
            "Suspended for 10 games for stamping on Casquero in 2009.",
            "Born in Maceió, Brazil; moved to Portugal at 18 to play for Marítimo."
        ]
    },
    # Day 69 — Shkodran Mustafi (Germany)
    {
        "id": "mustafi",
        "name": "Shkodran Mustafi",
        "country": "Germany",
        "countryFlag": "🇩🇪",
        "years": "2009–2024",
        "aliases": ["mustafi", "shkodran mustafi"],
        "clues": [
            "I played at the 2014 World Cup, playing 1 game and scoring 0 goals.",
            "I ended my career in Italy, where I'd also started it.",
            "I was signed for £35 million by a Premier League club. It was not a success.",
            "I won the 2014 World Cup, but hardly played.",
            "I won the FA Cup twice, under both Wenger and Arteta."
        ],
        "image": "mustafi.jpg",
        "silhouette": "mustafi.jpg",
        "position": "Centre-Back",
        "yearsActive": "2009–2024",
        "story": "The German centre-back who won the 2014 World Cup as a back-up, then earned the dubious honour of being the symbol of Arsenal's transfer-window decline. Career: Hamburg/Everton youth (released without a first-team game), Sampdoria, Valencia (Europa League final 2014), Arsenal (£35m, controversial buy, FA Cup wins, became a meme), Schalke, Levante, Como. Germany: WC 2014 winner (1 game), WC 2018 (group stage out). Always more competent than internet meme culture suggests, but never quite vindicated.",
        "youtube": "https://www.youtube.com/watch?v=JVL_jZ1Xk5M",
        "clubs": ["Hamburger SV", "Everton", "Sampdoria", "Valencia", "Arsenal", "Schalke", "Levante", "Como"],
        "honours": ["World Cup (2014)", "FA Cup (2017, 2020)"],
        "numbers": "20 caps for Germany",
        "didYouKnow": [
            "Released by Everton at 19, rebuilt his career from Serie B with Sampdoria.",
            "Was Wenger's last £30m+ signing and one of his most-criticised.",
            "Has Albanian heritage; born in Bad Hersfeld, Germany."
        ]
    },
    # Day 70 — Kalidou Koulibaly (Senegal)
    {
        "id": "koulibaly",
        "name": "Kalidou Koulibaly",
        "country": "Senegal",
        "countryFlag": "🇸🇳",
        "years": "2010–",
        "aliases": ["koulibaly", "kalidou koulibaly"],
        "clues": [
            "I played in two World Cups (2018 and 2022), playing 6 games and scoring 1 goal. I'm here again at the 2026 World Cup.",
            "I spent eight years at Napoli before a £33 million move to a Premier League club in 2022.",
            "I scored in the 2022 AFCON final penalty shootout against Egypt, which we went on to win for our first ever AFCON title.",
            "I was born in France but represent the country my parents emigrated from at international level.",
            "I scored the goal that put my country into the Round of 16 at the 2022 World Cup, against Ecuador."
        ],
        "image": "koulibaly.jpg",
        "silhouette": "koulibaly.jpg",
        "position": "Centre-Back",
        "yearsActive": "2010–",
        "story": "Senegal's commanding centre-back captain. Born in Saint-Dié, France, raised in the Vosges region, chose to represent his parents' Senegal. Career: Metz youth, Genk (Belgian title), Napoli (8 years, two Serie A runners-up, near-misses against Juventus), Chelsea (one underwhelming season), Al-Hilal Saudi. Senegal: AFCON winner 2022 (captain), WC 2018 group stage exit, WC 2022 Round of 16 (scored vs Ecuador). One of the most respected defenders of the modern era.",
        "youtube": "https://www.youtube.com/watch?v=Wj3NBjXB3AE",
        "clubs": ["Metz", "Genk", "Napoli", "Chelsea", "Al-Hilal"],
        "honours": ["AFCON (2022, captain)", "Belgian First Division (2011)", "Serie A runner-up (multiple)"],
        "numbers": "70+ caps for Senegal",
        "didYouKnow": [
            "First Senegalese captain to lift the AFCON.",
            "Has a degree in Sports Science from a French university.",
            "The Genk team he won the Belgian title with also included Thibaut Courtois and Kevin De Bruyne."
        ]
    },
    # Day 71 — Gennaro Gattuso (Italy)
    {
        "id": "gattuso",
        "name": "Gennaro Gattuso",
        "country": "Italy",
        "countryFlag": "🇮🇹",
        "years": "1995–2013",
        "aliases": ["gattuso", "rino gattuso", "gennaro gattuso"],
        "clues": [
            "I played in two World Cups (2002 and 2006), playing 11 games and scoring 0 goals.",
            "I won the Champions League twice, but famously lost one in Istanbul.",
            "I met my wife while playing football in Scotland.",
            "I headbutted the Tottenham Assistant Manager in 2011, and was known for my physical style of play.",
            "I won the 2006 World Cup, playing with Pirlo in the midfield."
        ],
        "image": "gattuso.jpg",
        "silhouette": "gattuso.jpg",
        "position": "Defensive Midfielder",
        "yearsActive": "1995–2013",
        "story": "Italy's snarling defensive midfielder. Gattuso was the destroyer in Cannavaro's WC 2006-winning team and Pirlo's protector at AC Milan for over a decade. Perugia, Rangers (Scottish football cult years), AC Milan (12 years, 2x Champions League 2003 + 2007, Serie A 2004 + 2011), Sion. 73 Italy caps. Later coached at Milan, Napoli, Valencia, Marseille (sacked for results), Hajduk Split. The original '100% commitment, 70% talent' archetype. Famously head-butted Joe Jordan on the touchline in 2011.",
        "youtube": "https://www.youtube.com/watch?v=HKUnGoEwlUw",
        "clubs": ["Perugia", "Rangers", "Salernitana", "AC Milan", "Sion"],
        "honours": ["World Cup (2006)", "2x Champions League (2003, 2007)", "2x Serie A", "Coppa Italia", "Scottish League Cup"],
        "numbers": "73 caps for Italy, 1 goal",
        "didYouKnow": [
            "Played for Rangers as a teenager and never lost his Glaswegian accent.",
            "Head-butted Tottenham assistant Joe Jordan during a Champions League match in 2011.",
            "His wife is Scottish; they met during his Rangers spell."
        ]
    }
]


def main():
    for path in (ANDROID, IOS):
        with open(path) as f:
            data = json.load(f)
        # replace indices 53..70 (Days 54..71) with new players
        data["footballers"][START_INDEX:START_INDEX + len(NEW_PLAYERS)] = NEW_PLAYERS
        with open(path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"updated {os.path.relpath(path, ROOT)} — {len(NEW_PLAYERS)} players replaced")

    # quick verify
    with open(ANDROID) as f:
        data = json.load(f)
    print(f"\nTotal players: {len(data['footballers'])}")
    for i in range(START_INDEX, START_INDEX + len(NEW_PLAYERS)):
        p = data["footballers"][i]
        print(f"  Day {i+1}: {p['name']} ({p['country']}) — youtube={p['youtube']}")
    # day 72 carry-over
    p = data["footballers"][START_INDEX + len(NEW_PLAYERS)]
    print(f"  Day {START_INDEX + len(NEW_PLAYERS) + 1}: {p['name']} (unchanged, original roster)")


if __name__ == "__main__":
    main()
