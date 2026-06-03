#!/usr/bin/env python3
"""Apply v1.4.4 WC group-stage content (17 new players) to all four data files:
  - app/src/main/assets/content.json (Android)
  - ios/GoodToHearTheName/GoodToHearTheName/Resources/content.json (iOS)
  - docs/players.js (Web, top-level fields + clues)
  - docs/bios.js (Web, bio detail)

Replaces players at indices 37–53 (days 38–54). Other indices untouched.
"""
import json
import re
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ANDROID = os.path.join(ROOT, "app/src/main/assets/content.json")
IOS     = os.path.join(ROOT, "ios/GoodToHearTheName/GoodToHearTheName/Resources/content.json")
WEB_PL  = os.path.join(ROOT, "docs/players.js")
WEB_BIO = os.path.join(ROOT, "docs/bios.js")


# ============================================================================
# 17 NEW PLAYER ENTRIES (days 38–54). Order matters.
# ============================================================================
PLAYERS = [
    # ─── Day 38 ────────────────────────────────────────────────────────────
    {
        "id": "rafael_marquez",
        "name": "Rafael Márquez",
        "country": "Mexico",
        "countryFlag": "🇲🇽",
        "years": "1996–2018",
        "aliases": ["rafa marquez", "marquez", "rafael marquez", "el kaiser", "el káiser"],
        "clues": [
            "I played in five World Cups (2002, 2006, 2010, 2014 and 2018), scoring 3 goals across 19 games.",
            "I am currently an assistant manager at this World Cup, for the country I played for.",
            "I'm the only player in history to captain my country at five different World Cup finals. Guinness gave me the record for it.",
            "I won four league titles and two Champions Leagues in seven seasons at one of the biggest clubs in Spain.",
            "I'm Mexican. They called me 'El Káiser' at the Camp Nou.",
        ],
        "position": "Centre-Back",
        "yearsActive": "1996–2018",
        "story": "Rafael Márquez was the calm at the heart of Barcelona's tiki-taka generation, alongside Xavi, Iniesta and Puyol. They called him 'El Káiser' at the Camp Nou, where he won four La Liga titles and two Champions Leagues in seven seasons under Rijkaard and Guardiola. He had been a Monaco Ligue 1 winner before that, and started at Atlas in Guadalajara at sixteen. The international shirt is what defined him: five World Cups for Mexico from 2002 to 2018, captain at every one, the only footballer in history to do that. He returns to this World Cup on the bench as Aguirre's assistant and confirmed successor.",
        "youtube": "https://www.youtube.com/watch?v=WKQEUQ3kM6k",
        "clubs": ["Atlas", "AS Monaco", "FC Barcelona", "New York Red Bulls", "León", "Hellas Verona", "Atlas"],
        "honours": [
            "La Liga x4 (Barcelona, 2004–05, 2005–06, 2008–09, 2009–10)",
            "Champions League x2 (Barcelona, 2006, 2009)",
            "Copa del Rey x2 (Barcelona, 2009, 2012)",
            "CONCACAF Gold Cup x2 (Mexico, 2003, 2011)",
            "FIFA Confederations Cup (Mexico, 1999)",
        ],
        "numbers": "3 goals in 19 World Cup matches across five tournaments",
        "didYouKnow": [
            "He is the only footballer in history to captain his country at five different World Cup finals (Guinness World Record).",
            "He scored the equaliser against hosts South Africa in the opening match of the 2010 World Cup, denying Bafana Bafana the perfect start.",
            "He is one of only four players to appear at five World Cup tournaments, alongside Antonio Carbajal, Lothar Matthäus and Gianluigi Buffon.",
        ],
    },
    # ─── Day 39 ────────────────────────────────────────────────────────────
    {
        "id": "edin_dzeko",
        "name": "Edin Džeko",
        "country": "Bosnia & Herzegovina",
        "countryFlag": "🇧🇦",
        "years": "2003–present",
        "aliases": ["edin dzeko", "dzeko", "edin džeko"],
        "clues": [
            "I played at the 2014 World Cup, scoring 1 goal in 3 games for my country. I am here again at the 2026 World Cup.",
            "I'm my country's all-time leading goalscorer and most-capped player.",
            "I had a goal controversially disallowed for offside against Nigeria in my country's first ever World Cup match in 2014.",
            "I was Serie A's top scorer in 2016–17 with 29 goals for a club in Rome.",
            "I won the Bundesliga top-scorer trophy in 2009–10, then crossed Europe and won the Premier League twice in three years.",
        ],
        "position": "Striker",
        "yearsActive": "2003–present",
        "story": "Edin Džeko's family flat was shelled during the Siege of Sarajevo. Bosnia's youth academies rejected him for being too skinny. He left for Teplice in the Czech Republic at nineteen for about €25,000, and quietly became one of Europe's most reliable strikers. Bundesliga top scorer at Wolfsburg, two Premier League titles at Manchester City, Serie A top scorer at Roma at thirty-one, still scoring goals at forty for Schalke. Bosnia & Herzegovina's all-time leading goalscorer and the captain who took them to their first ever World Cup in 2014 and who carries the armband again at the 2026 tournament.",
        "youtube": "https://www.youtube.com/watch?v=vk8FvYutNwU",
        "clubs": ["Željezničar", "Teplice", "Ústí nad Labem (loan)", "VfL Wolfsburg", "Manchester City", "Roma", "Inter Milan", "Fenerbahçe", "Fiorentina", "Schalke 04"],
        "honours": [
            "Premier League x2 (Man City, 2011–12, 2013–14)",
            "FA Cup (Man City, 2010–11)",
            "Bundesliga (Wolfsburg, 2008–09); Bundesliga top scorer 2009–10",
            "Coppa Italia x2 (Inter, 2021–22, 2022–23)",
            "Serie A capocannoniere 2016–17 (Roma)",
            "Bosnia all-time top scorer",
        ],
        "numbers": "1 goal in 3 World Cup matches at the 2014 tournament",
        "didYouKnow": [
            "He scored Bosnia & Herzegovina's only ever World Cup victory, the winner in their 3-1 defeat of Iran at the 2014 tournament.",
            "He came on as a substitute against QPR on the final day of the 2011–12 Premier League season and scored the 92nd-minute equaliser that set up Sergio Agüero's title-winning goal.",
            "He is Bosnia & Herzegovina's all-time leading goalscorer and most-capped player.",
        ],
    },
    # ─── Day 40 ────────────────────────────────────────────────────────────
    {
        "id": "oscar_brazil",
        "name": "Oscar",
        "country": "Brazil",
        "countryFlag": "🇧🇷",
        "years": "2008–2026",
        "aliases": ["oscar", "oscar dos santos", "oscar emboaba"],
        "clues": [
            "I played at the 2014 World Cup, scoring 2 goals in 7 games for my country at the tournament they hosted.",
            "I won the Silver Ball at the 2011 FIFA Under-20 World Cup in Colombia, scoring a hat-trick in the final as my country beat Portugal 3-2 from 2-0 down.",
            "I won the Premier League twice in three seasons in London.",
            "I scored my country's only goal in their greatest humiliation against Germany.",
            "I left a London club for an Asian record fee of £60 million in January 2017. The new contract was reported as £400,000 a week.",
        ],
        "position": "Attacking Midfielder",
        "yearsActive": "2008–2026",
        "story": "Oscar was Brazil's golden boy. The São Paulo prodigy who lit up the FIFA U-20 World Cup in 2011 with a hat-trick in the final, and was sold to Chelsea at twenty for around £25 million. He won two Premier League titles and the Europa League at Stamford Bridge before, in January 2017 aged twenty-five, taking a £60 million Asian-record move to Shanghai SIPG on £400,000-a-week wages and effectively vanishing from elite European football. The 2014 World Cup at home was bookended by his clipped toe-poke against Croatia in the opener and his lone goal in the 7-1 humiliation by Germany. Retired April 2026, aged thirty-four, after a heart condition was detected in pre-season screening.",
        "youtube": "https://www.youtube.com/watch?v=0CB6nuxhQMw",
        "clubs": ["São Paulo", "Internacional", "Chelsea", "Shanghai SIPG / Shanghai Port", "São Paulo"],
        "honours": [
            "Premier League x2 (Chelsea, 2014–15, 2016–17)",
            "UEFA Europa League (Chelsea, 2012–13)",
            "EFL Cup (Chelsea, 2014–15)",
            "Chinese Super League x3 (Shanghai Port, 2018, 2023, 2024)",
            "FIFA U-20 World Cup Silver Ball (Brazil, 2011)",
            "Confederations Cup (Brazil, 2013)",
            "Olympic silver medal (Brazil, 2012)",
        ],
        "numbers": "2 goals in 7 World Cup matches at the 2014 tournament",
        "didYouKnow": [
            "He scored Brazil's only goal in their 7-1 semi-final defeat to Germany at the 2014 World Cup, the country's worst ever competitive result.",
            "He left Chelsea for Shanghai SIPG in January 2017 for £60 million, the largest fee ever paid for a player in the Chinese Super League at the time.",
            "He retired in April 2026 aged 34 after a heart condition was detected in pre-season screening at São Paulo.",
        ],
    },
    # ─── Day 41 ────────────────────────────────────────────────────────────
    {
        "id": "arjen_robben",
        "name": "Arjen Robben",
        "country": "Netherlands",
        "countryFlag": "🇳🇱",
        "years": "2000–2021",
        "aliases": ["arjen robben", "robben"],
        "clues": [
            "I played in three World Cups (2006, 2010 and 2014), scoring 6 goals across 15 games.",
            "I have been fouled more times at the World Cup than any other player since 2006.",
            "I scored the only goal of the 2013 Champions League final in the 89th minute against Borussia Dortmund.",
            "Iker Casillas stuck out a leg to save my one-on-one in the 83rd minute of the 2010 World Cup final. Andrés Iniesta scored the winner for Spain in extra time.",
            "I'm Dutch. They knew the cut-inside was coming, and they still couldn't stop it.",
        ],
        "position": "Right Winger",
        "yearsActive": "2000–2021",
        "story": "For fifteen years it was always the same: pick the ball up on the right, cut inside onto the left foot, rifle it into the far corner. Everyone knew it. Nobody stopped it. Arjen Robben won two Premier League titles at Chelsea before he was twenty-three, a La Liga at Real Madrid, then eight Bundesligas at Bayern Munich and the 89th-minute winner in the 2013 Champions League final against Borussia Dortmund. For the Netherlands he played at three World Cups. He came within an Iker Casillas leg of winning the 2010 final in normal time. Iniesta won it in extra time.",
        "youtube": "https://www.youtube.com/watch?v=q-9q38qZD9I",
        "clubs": ["FC Groningen", "PSV Eindhoven", "Chelsea", "Real Madrid", "Bayern Munich", "FC Groningen"],
        "honours": [
            "FIFA World Cup runner-up (Netherlands, 2010)",
            "UEFA Champions League (Bayern, 2012–13)",
            "Bundesliga x8 (Bayern Munich)",
            "DFB-Pokal x5 (Bayern)",
            "Premier League x2 (Chelsea, 2004–05, 2005–06)",
            "La Liga (Real Madrid, 2007–08)",
            "FA Cup (Chelsea, 2006–07)",
            "Eredivisie (PSV, 2002–03)",
        ],
        "numbers": "6 goals in 15 World Cup matches across three tournaments",
        "didYouKnow": [
            "Iker Casillas saved his one-on-one in the 83rd minute of the 2010 World Cup final. Andrés Iniesta scored the winner for Spain in extra time.",
            "He scored the only goal of the 2013 Champions League final, in the 89th minute against Borussia Dortmund.",
            "He has been fouled more times at the World Cup than any other player since 2006.",
        ],
    },
    # ─── Day 42 ────────────────────────────────────────────────────────────
    {
        "id": "diego_forlan",
        "name": "Diego Forlán",
        "country": "Uruguay",
        "countryFlag": "🇺🇾",
        "years": "1996–2019",
        "aliases": ["diego forlan", "diego forlán", "forlan", "forlán"],
        "clues": [
            "I played in three World Cups (2002, 2010 and 2014), scoring 6 goals across 10 games.",
            "After my best World Cup, I signed for an Italian giant aged 32 for around €5 million. I scored twice in Serie A all season.",
            "It took me nine months and 27 games to score my first Premier League goal.",
            "I won the European Golden Shoe twice, with two different Spanish clubs. I'm the only player to do that.",
            "I won the Golden Ball as best player at the 2010 World Cup, and shared the Golden Boot with Müller, Villa and Sneijder on five goals.",
        ],
        "position": "Forward",
        "yearsActive": "1996–2019",
        "story": "Diego Forlán took eight months and twenty-seven games to score his first Premier League goal at Manchester United, and was widely written off as a Sir Alex misfire. Then he went to Spain. He won the European Golden Shoe at Villarreal in 2004-05, won it again at Atlético Madrid in 2008-09, scored both goals in the 2010 Europa League final, and at the 2010 World Cup he turned thirty-one and was suddenly the best player on Earth. Five goals, the Golden Boot, the Golden Ball, a 30-yard dipping volley against Germany in the third-place playoff voted goal of the tournament. Inter Milan signed him next: two Serie A goals all season. His father played for Uruguay at the 1966 and 1974 World Cups.",
        "youtube": "https://www.youtube.com/watch?v=zj79yzTPhwk",
        "clubs": ["Independiente", "Manchester United", "Villarreal", "Atlético Madrid", "Inter Milan", "Internacional", "Cerezo Osaka", "Peñarol", "Mumbai City", "Kitchee"],
        "honours": [
            "World Cup Golden Ball (Uruguay, 2010)",
            "Copa América (Uruguay, 2011)",
            "European Golden Shoe x2 (Villarreal 2004–05, Atlético 2008–09)",
            "UEFA Europa League (Atlético, 2009–10)",
            "UEFA Super Cup (Atlético, 2010)",
            "Premier League (Man United, 2002–03)",
            "FA Cup (Man United, 2003–04)",
        ],
        "numbers": "6 goals in 10 World Cup matches across three tournaments (5 of them at South Africa 2010)",
        "didYouKnow": [
            "He won the Golden Ball as best player at the 2010 World Cup, and shared the Golden Boot (5 goals) with Thomas Müller, David Villa and Wesley Sneijder.",
            "His 30-yard dipping volley against Germany in the third-place playoff was voted the 2010 World Cup's goal of the tournament.",
            "His father Pablo Forlán played for Uruguay at the 1966 and 1974 World Cups.",
        ],
    },
    # ─── Day 43 ────────────────────────────────────────────────────────────
    {
        "id": "el_hadji_diouf",
        "name": "El Hadji Diouf",
        "country": "Senegal",
        "countryFlag": "🇸🇳",
        "years": "1998–2015",
        "aliases": ["el hadji diouf", "diouf", "el-hadji diouf"],
        "clues": [
            "I played at the 2002 World Cup, scoring 0 goals in 5 games for my country.",
            "I won the Scottish Premier League and the Scottish League Cup with a famous Glasgow club in 2010–11.",
            "I was named African Footballer of the Year in both 2001 and 2002, back-to-back, with my World Cup in between.",
            "I tormented France's defence in the opening match of the 2002 World Cup, skinning Frank Leboeuf on the byline to set up the goal that beat the reigning world champions 1-0.",
            "I joined Liverpool on the back of my country's heroics for around £10 million. I scored three Premier League goals in two seasons.",
        ],
        "position": "Winger / Forward",
        "yearsActive": "1998–2015",
        "story": "The most notorious player on Pelé's FIFA 100 list. El Hadji Diouf was a £10 million Liverpool flop who scored three Premier League goals in two seasons. He was banned for spitting at a Celtic fan from the bench, accused of spitting at a Portsmouth defender and a Middlesbrough ball boy, and was called a 'disgrace' by Sir Alex Ferguson. He was also African Footballer of the Year in both 2001 and 2002. At the 2002 World Cup he tormented Frank Leboeuf on the byline and set up the goal that beat reigning champions France 1-0 in the most iconic upset of the tournament. The drift through Bolton, Sunderland, Blackburn, Rangers, Doncaster and Leeds took him into his forties.",
        "youtube": "https://www.youtube.com/watch?v=UC-12ZNs2xg",
        "clubs": ["Sochaux", "Rennes", "Lens", "Liverpool", "Bolton Wanderers", "Sunderland", "Blackburn Rovers", "Rangers (loan)", "Doncaster Rovers", "Leeds United", "Sabah FA"],
        "honours": [
            "Football League Cup (Liverpool, 2002–03)",
            "Scottish Premier League (Rangers, 2010–11)",
            "Scottish League Cup (Rangers, 2010–11)",
            "African Footballer of the Year x2 (2001, 2002)",
            "2002 World Cup All-Star Team",
            "FIFA 100 (Pelé's list, 2004)",
        ],
        "numbers": "0 goals in 5 World Cup matches at the 2002 tournament",
        "didYouKnow": [
            "He set up Papa Bouba Diop's goal as Senegal beat reigning champions France 1-0 in the 2002 World Cup opener, the tournament's most iconic upset.",
            "He was African Footballer of the Year in both 2001 and 2002, back to back.",
            "He was named on Pelé's FIFA 100 list of greatest living footballers in 2004.",
        ],
    },
    # ─── Day 44 ────────────────────────────────────────────────────────────
    {
        "id": "james_rodriguez",
        "name": "James Rodríguez",
        "country": "Colombia",
        "countryFlag": "🇨🇴",
        "years": "2006–present",
        "aliases": ["james rodriguez", "james rodríguez", "james"],
        "clues": [
            "I played at the 2014 and 2018 World Cups, scoring 6 goals across 8 games for my country. I am here again at the 2026 World Cup as captain.",
            "I have played for clubs in Liverpool, Munich and Madrid.",
            "I won the Golden Boot at one of the World Cups I played at.",
            "I wore the No. 10 at Real Madrid.",
            "After an incredible volley against Uruguay, I became the fourth most expensive transfer in history at the time.",
        ],
        "position": "Attacking Midfielder",
        "yearsActive": "2006–present",
        "story": "Real Madrid paid roughly €80 million to bring James Rodríguez to Spain in the summer of 2014, days after his World Cup explosion. He was twenty-three. It was the fourth-most-expensive transfer in football history at the time. He scored seventeen in his first season under Carlo Ancelotti. Then Zidane arrived, the bench beckoned, the Bayern loan was offered, Bayern declined the buy option. The drift: Everton, Al-Rayyan, Olympiacos, São Paulo, Rayo Vallecano, León. He never recaptured the Brazilian summer he won the Golden Boot in. But here he is, thirty-four years old, captaining Colombia at his third World Cup.",
        "youtube": "https://www.youtube.com/watch?v=zI02ogMpjHU",
        "clubs": ["Envigado", "Banfield", "Porto", "Monaco", "Real Madrid", "Bayern Munich (loan)", "Everton", "Al-Rayyan", "Olympiacos", "São Paulo", "Rayo Vallecano", "León"],
        "honours": [
            "FIFA World Cup Golden Boot (Colombia, 2014)",
            "FIFA Goal of the Tournament (2014)",
            "UEFA Champions League x2 (Real Madrid, 2015–16, 2016–17)",
            "La Liga (Real Madrid, 2016–17)",
            "Bundesliga x2 (Bayern, 2017–18, 2018–19)",
            "FIFA Club World Cup x2 (Real Madrid)",
            "UEFA Europa League (Porto, 2010–11)",
        ],
        "numbers": "6 goals in 8 World Cup matches across two tournaments (all 6 at Brazil 2014)",
        "didYouKnow": [
            "His swerving left-footed volley against Uruguay in the 2014 round of 16 was voted FIFA Goal of the Tournament.",
            "He won the 2014 World Cup Golden Boot with 6 goals, scoring in every match Colombia played.",
            "Real Madrid signed him for around €80 million days after the 2014 World Cup, the fourth most expensive transfer in history at the time.",
        ],
    },
    # ─── Day 45 ────────────────────────────────────────────────────────────
    {
        "id": "pavel_nedved",
        "name": "Pavel Nedvěd",
        "country": "Czech Republic",
        "countryFlag": "🇨🇿",
        "years": "1991–2009",
        "aliases": ["pavel nedved", "pavel nedvěd", "nedved", "furia ceca"],
        "clues": [
            "I played at the 2006 World Cup, scoring 0 goals in 3 games for my country.",
            "I lost a major international tournament final to Germany on a Golden Goal.",
            "I have won Serie A with two clubs. I would have won a few more, depending on who you ask.",
            "I have won the Ballon d'Or.",
            "I stayed at Juventus when they were forcibly relegated to Serie B in the 2006 Calciopoli scandal. I played in the second tier with them.",
        ],
        "position": "Midfielder",
        "yearsActive": "1991–2009",
        "story": "The Czech Fury. Pavel Nedvěd ran for ninety minutes every game for ninety years. Lazio bought him from Sparta after his stunning Euro 96 (where the Czechs lost the final to Germany on a golden goal), and he won Serie A there in 2000, two Coppa Italias and the Cup Winners' Cup. He moved across to Juventus and won the Ballon d'Or in 2003 by 62 points over Thierry Henry. He stayed at Juve through their forced relegation to Serie B in the 2006 Calciopoli scandal, playing in the second tier with them. Two further Juve Serie A titles were stripped retrospectively. He was later Juventus vice-chairman until he resigned in 2022.",
        "youtube": "https://www.youtube.com/watch?v=DHKx20X4_HM",
        "clubs": ["Škoda Plzeň", "Dukla Prague (loan)", "Sparta Prague", "Lazio", "Juventus"],
        "honours": [
            "Ballon d'Or 2003",
            "Serie A x3 (Lazio 1999–2000; Juventus 2001–02, 2002–03)",
            "UEFA Cup Winners' Cup (Lazio, 1998–99)",
            "UEFA Super Cup (Lazio, 1999)",
            "Coppa Italia x2 (Lazio, 1997–98, 1999–2000)",
            "UEFA Euro 1996 runner-up (Czech Republic)",
            "Czech Footballer of the Year x7",
            "FIFA 100 (Pelé's list, 2004)",
        ],
        "numbers": "0 goals in 3 World Cup matches at the 2006 tournament",
        "didYouKnow": [
            "He won the 2003 Ballon d'Or by 62 points over Thierry Henry.",
            "He stayed at Juventus when they were forcibly relegated to Serie B in the 2006 Calciopoli scandal and played in the second tier with them.",
            "He lost the Euro 1996 final to Germany on a golden goal at Wembley.",
        ],
    },
    # ─── Day 46 ────────────────────────────────────────────────────────────
    {
        "id": "tim_howard",
        "name": "Tim Howard",
        "country": "United States",
        "countryFlag": "🇺🇸",
        "years": "1997–2020",
        "aliases": ["tim howard", "howard"],
        "clues": [
            "I played in two World Cups (2010 and 2014) for my country.",
            "I won the FA Cup and the Community Shield in my first season at my Premier League club.",
            "I have played for a Premier League club in both Manchester and Liverpool.",
            "I made 16 saves in a single World Cup match against Belgium in 2014, the most by any goalkeeper in any World Cup match since records began in 1966.",
            "Sir Alex Ferguson signed me from the New York MetroStars in 2003 to replace Fabien Barthez.",
        ],
        "position": "Goalkeeper",
        "yearsActive": "1997–2020",
        "story": "Tim Howard spent a decade at Everton, almost four hundred Premier League games as the Toffees' goalkeeper from 2006 to 2016. Before that, Sir Alex Ferguson had signed him from the New York MetroStars in 2003 to replace Fabien Barthez at Manchester United, where he won the FA Cup in his first season before losing his place to Edwin van der Sar. The defining game came at the 2014 World Cup in Salvador, where he made sixteen saves over 120 minutes against Belgium, the most by any goalkeeper in any World Cup match since records began in 1966. The United States still lost 2-1 in extra time. He is his country's most-capped goalkeeper ever.",
        "youtube": "https://www.youtube.com/watch?v=BgXhlxRMOBA",
        "clubs": ["North Jersey Imperials", "MetroStars / New York Red Bulls", "Manchester United", "Everton (loan, then permanent)", "Colorado Rapids", "Memphis 901 FC"],
        "honours": [
            "FA Cup (Manchester United, 2003–04)",
            "FA Community Shield (Manchester United, 2003)",
            "CONCACAF Gold Cup x2 (USA, 2007, 2017)",
            "FIFA Confederations Cup runner-up (USA, 2009)",
            "US Soccer National Hall of Fame (2024)",
            "Most-capped USMNT goalkeeper",
        ],
        "numbers": "16 saves in a single World Cup match vs Belgium 2014, most by any goalkeeper since records began in 1966",
        "didYouKnow": [
            "His 16 saves against Belgium in the 2014 round of 16 are the most by any goalkeeper in a single World Cup match since records began in 1966.",
            "After that game, somebody edited the Wikipedia entry for the US Secretary of Defense to read 'Tim Howard'.",
            "He scored a 100-yard wind-aided goal for Everton against Bolton in January 2012.",
        ],
    },
    # ─── Day 47 ────────────────────────────────────────────────────────────
    {
        "id": "wout_weghorst",
        "name": "Wout Weghorst",
        "country": "Netherlands",
        "countryFlag": "🇳🇱",
        "years": "2010–present",
        "aliases": ["wout weghorst", "weghorst"],
        "clues": [
            "I played at the 2022 World Cup, scoring 2 goals in 4 games for my country.",
            "I was booked in the 2022 World Cup before even coming on as a substitute.",
            "In the same game, I scored deep in added time from a clever free-kick routine.",
            "I had a disastrous spell at a Premier League club after a £12 million transfer, in which I only scored 2 goals and we got relegated.",
            "I was signed as an emergency loan for one of the Premier League's biggest clubs under a manager of my own nationality.",
        ],
        "position": "Striker",
        "yearsActive": "2010–present",
        "story": "A 6'6\" striker who started in the Dutch second tier with FC Emmen and didn't make his Eredivisie debut until twenty-three. Wout Weghorst then became one. Seventy goals in 144 games at Wolfsburg, second only to Robert Lewandowski in the Bundesliga during his stint. A £12 million transfer to Burnley in January 2022 produced two Premier League goals in twenty appearances as the Clarets were relegated. An emergency loan to Manchester United under fellow Dutchman Erik ten Hag the next season won him his first trophy at thirty, the EFL Cup. At the 2022 World Cup he came off the bench in the quarter-final against Argentina and scored two goals in twelve minutes to force extra time, the second a powered header off an audacious low free-kick routine. The Netherlands lost on penalties.",
        "youtube": "https://www.youtube.com/watch?v=qIOLKjT9JBQ",
        "clubs": ["Willem II (youth)", "FC Emmen", "Heracles Almelo", "AZ Alkmaar", "VfL Wolfsburg", "Burnley", "Beşiktaş (loan)", "Manchester United (loan)", "TSG Hoffenheim (loan)", "Ajax"],
        "honours": [
            "EFL Cup (Manchester United, 2022–23)",
            "2022 FIFA World Cup quarter-finalist (Netherlands)",
            "UEFA Nations League runner-up (Netherlands, 2023)",
            "UEFA Euro 2024 semi-finalist (Netherlands)",
        ],
        "numbers": "2 goals in 4 World Cup matches at the 2022 tournament (both in the QF vs Argentina)",
        "didYouKnow": [
            "He came off the bench in the 2022 World Cup quarter-final and scored twice in twelve minutes to force extra time against Argentina, including a header off a low free-kick routine.",
            "Argentina won on penalties, and Messi's 'Andá pa' allá, bobo' to Weghorst in the post-match interview became one of the iconic images of the tournament.",
            "He had scored zero goals in 20 Premier League games for Burnley before that World Cup.",
        ],
    },
    # ─── Day 48 ────────────────────────────────────────────────────────────
    {
        "id": "keisuke_honda",
        "name": "Keisuke Honda",
        "country": "Japan",
        "countryFlag": "🇯🇵",
        "years": "2005–present",
        "aliases": ["keisuke honda", "honda"],
        "clues": [
            "I played in three World Cups (2010, 2014 and 2018), scoring 4 goals across 10 games.",
            "I won the Russian Premier League and two Russian Cups with CSKA Moscow.",
            "I'm the only Asian player with 4 World Cup goals.",
            "I joined AC Milan in 2014 and wore the No. 10 shirt previously worn by Seedorf, Boban and Rui Costa.",
            "I'm Japanese. I won the AFC Asian Cup in 2011 and was named tournament MVP.",
        ],
        "position": "Attacking Midfielder",
        "yearsActive": "2005–present",
        "story": "Keisuke Honda was Japan's player of the early 2010s. He won the AFC Asian Cup in 2011 as tournament MVP, won the Russian Premier League and two Russian Cups at CSKA Moscow, then signed for AC Milan in 2014 and wore the No. 10 shirt previously worn by Seedorf, Boban and Rui Costa. Three consecutive World Cups, four goals across them, the only Japanese player to score at three different tournaments and the only Asian player with four. His 2010 free-kick against Denmark from thirty yards dipped into the top corner past Thomas Sørensen. His 2018 goal against Senegal made him the first professional footballer to score competitive goals on all six continents. The club career drifted through ten countries and he was briefly head coach of Cambodia while still playing for Botafogo.",
        "youtube": "https://www.youtube.com/watch?v=7kJ54U_rcmM",
        "clubs": ["Nagoya Grampus Eight", "VVV-Venlo", "CSKA Moscow", "AC Milan", "Pachuca", "Melbourne Victory", "Vitesse", "Botafogo", "Portimonense", "Neftçi Baku", "Sūduva"],
        "honours": [
            "AFC Asian Cup (Japan, 2011), Tournament MVP",
            "Russian Premier League (CSKA Moscow, 2012–13)",
            "Russian Cup x2 (CSKA, 2010–11, 2012–13)",
            "J1 League (Nagoya Grampus, 2008)",
        ],
        "numbers": "4 goals in 10 World Cup matches across three tournaments",
        "didYouKnow": [
            "He is the only Japanese player to score at three different World Cups, and the only Asian player with 4 World Cup goals.",
            "His 2018 goal against Senegal made him the first professional footballer to score a competitive goal on all six continents.",
            "He was briefly head coach of Cambodia's national team while still playing club football for Botafogo.",
        ],
    },
    # ─── Day 49 ────────────────────────────────────────────────────────────
    {
        "id": "maxi_rodriguez",
        "name": "Maxi Rodríguez",
        "country": "Argentina",
        "countryFlag": "🇦🇷",
        "years": "1999–2021",
        "aliases": ["maxi rodriguez", "maxi rodríguez", "la fiera"],
        "clues": [
            "I played in three World Cups (2006, 2010 and 2014), scoring 3 goals across 12 games.",
            "I was runner-up in a World Cup final after losing in extra time.",
            "I scored the goal of the tournament at the 2006 World Cup.",
            "I won the League Cup with Liverpool.",
            "I started and ended my career at Newell's Old Boys in Argentina.",
        ],
        "position": "Winger / Attacking Midfielder",
        "yearsActive": "1999–2021",
        "story": "La Fiera, the Beast. Maxi Rodríguez made his name in eight seasons in La Liga with Espanyol and Atlético Madrid (cup-tied for Atlético's 2009-10 Europa League win), then signed for Liverpool in 2010 for around £1.5 million. He scored hat-tricks against Birmingham and Fulham, and Liverpool's last ever Anfield goal under Kenny Dalglish, against Chelsea in May 2012. He played in three World Cups for Argentina, scored Goal of the Tournament with an extra-time volley at the 2006 round of 16 against Mexico, and slotted home the decisive penalty in the 2014 semi-final shootout against the Netherlands. He started and ended his career at Newell's Old Boys in Rosario, twenty-two years apart.",
        "youtube": "https://www.youtube.com/watch?v=aiY9Mz8N5SQ",
        "clubs": ["Newell's Old Boys", "RCD Espanyol", "Atlético Madrid", "Liverpool", "Newell's Old Boys", "Peñarol", "Newell's Old Boys"],
        "honours": [
            "2014 FIFA World Cup runner-up (Argentina)",
            "2005 FIFA Confederations Cup runner-up",
            "2001 FIFA U-20 World Cup (Argentina)",
            "League Cup (Liverpool, 2011–12)",
            "Argentine Primera División (Newell's, 2013 Torneo Final)",
            "Uruguayan Primera División x2 (Peñarol, 2017, 2018)",
        ],
        "numbers": "3 goals in 12 World Cup matches across three tournaments",
        "didYouKnow": [
            "His extra-time volley against Mexico in the 2006 round of 16 was voted FIFA Goal of the Tournament.",
            "He scored the decisive penalty in the 2014 World Cup semi-final shootout against the Netherlands to put Argentina in the final for the first time since 1990.",
            "He started and ended his career at boyhood club Newell's Old Boys in Rosario, twenty-two years apart.",
        ],
    },
    # ─── Day 50 ────────────────────────────────────────────────────────────
    {
        "id": "joe_cole",
        "name": "Joe Cole",
        "country": "England",
        "countryFlag": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
        "years": "1998–2018",
        "aliases": ["joe cole", "cole"],
        "clues": [
            "I played in three World Cups (2002, 2006 and 2010), scoring 1 goal across 8 games.",
            "I was on £10,000 a week as a teenager at my boyhood club, eye-watering at the time.",
            "I became captain of my boyhood club at twenty-one, but I would reach my greatest success at another club in the same city.",
            "I won three Premier League titles, two FA Cups and a League Cup at one West London club under Mourinho and Ancelotti.",
            "I scored a 35-yard dipping volley against Sweden at the 2006 World Cup, still cited as one of England's best ever World Cup goals.",
        ],
        "position": "Attacking Midfielder",
        "yearsActive": "1998–2018",
        "story": "Sven-Göran Eriksson and the British press once tipped him as the 'English Zidane'. Joe Cole was West Ham's captain at twenty-one, was earning £10,000 a week as a teenager. Then five years at Chelsea under Mourinho and Ancelotti: three Premier League titles, two FA Cups, a League Cup, and the volley against Sweden at the 2006 World Cup that is still cited as one of England's best ever. He left Chelsea on a free in 2010 for Liverpool on reported wages of £90,000 a week and scored five goals in forty-one games before being released. The drift took him back to West Ham, then Aston Villa, Coventry, Tampa Bay.",
        "youtube": "https://www.youtube.com/watch?v=OJ29PgBD130",
        "clubs": ["West Ham United", "Chelsea", "Liverpool", "Lille (loan)", "West Ham United", "Aston Villa", "Coventry City (loan, then permanent)", "Tampa Bay Rowdies"],
        "honours": [
            "Premier League x3 (Chelsea, 2004–05, 2005–06, 2009–10)",
            "FA Cup x2 (Chelsea, 2006–07, 2009–10)",
            "League Cup (Chelsea, 2004–05)",
            "UEFA Intertoto Cup (West Ham, 1999)",
        ],
        "numbers": "1 goal in 8 World Cup matches across three tournaments (vs Sweden, 2006)",
        "didYouKnow": [
            "His 35-yard dipping volley against Sweden at the 2006 World Cup is widely cited as one of England's best ever World Cup goals.",
            "He left Chelsea on a free in 2010 and signed for Liverpool on reported wages of £90,000 a week, scoring 5 in 41 games before being released.",
            "Sven-Göran Eriksson once tipped him as the 'English Zidane'.",
        ],
    },
    # ─── Day 51 ────────────────────────────────────────────────────────────
    {
        "id": "maicon",
        "name": "Maicon",
        "country": "Brazil",
        "countryFlag": "🇧🇷",
        "years": "2000–2023",
        "aliases": ["maicon", "maicon douglas"],
        "clues": [
            "I played in two World Cups (2010 and 2014), scoring 1 goal across 8 games.",
            "I was named in the 2010 World Cup All-Star team.",
            "I won four consecutive Serie A titles between 2006 and 2010.",
            "I played for Manchester City for one season.",
            "I won the Champions League while playing at right-back.",
        ],
        "position": "Right-Back",
        "yearsActive": "2000–2023",
        "story": "For two seasons Maicon was the best right-back on Earth. The 2009-10 Inter Milan treble was built on his runs down the right: four consecutive Serie A titles, the Champions League final win over Bayern, UEFA Defender of the Year. Then in October 2010, Gareth Bale hat-tricked him at the San Siro, and the unravelling was televised. Manchester City signed him in 2012 as a marquee replacement for Pablo Zabaleta. One season later he was gone. The drift went through Roma, Brazilian lower divisions, and ended at San Marino's Tre Penne at the age of forty-one. At the 2010 World Cup he scored against North Korea from an impossibly tight angle on the right flank. He insisted it was a deliberate shot.",
        "youtube": "https://www.youtube.com/watch?v=0SjvhrLP93A",
        "clubs": ["Cruzeiro", "Monaco", "Inter Milan", "Manchester City", "Roma", "Avaí", "Criciúma", "Villa Nova", "Sona", "Tre Penne"],
        "honours": [
            "UEFA Champions League (Inter, 2009–10)",
            "Serie A x4 (Inter, 2006–07, 2007–08, 2008–09, 2009–10)",
            "FIFA Club World Cup (Inter, 2010)",
            "Copa América x2 (Brazil, 2004, 2007)",
            "FIFA Confederations Cup x2 (Brazil, 2005, 2009)",
            "2010 World Cup All-Star Team",
            "UEFA Defender of the Year 2009–10",
        ],
        "numbers": "1 goal in 8 World Cup matches across two tournaments",
        "didYouKnow": [
            "His goal against North Korea at the 2010 World Cup was scored from an absurdly tight angle on the right flank. He insisted it was a shot; many still call it a mishit cross.",
            "He started the 2010 UEFA Champions League final against Bayern Munich as part of Inter Milan's famous treble-winning side.",
            "Gareth Bale's hat-trick against him at the San Siro in October 2010 is widely cited as the public turning point in his career.",
        ],
    },
    # ─── Day 52 ────────────────────────────────────────────────────────────
    {
        "id": "serge_aurier",
        "name": "Serge Aurier",
        "country": "Côte d'Ivoire",
        "countryFlag": "🇨🇮",
        "years": "2010–present",
        "aliases": ["serge aurier", "aurier"],
        "clues": [
            "I played at the 2014 World Cup, scoring 0 goals in 3 games for my country.",
            "I captained my country to victory at the Africa Cup of Nations.",
            "When I was signed by a Premier League club, my UK visa was initially blocked over a conviction in France.",
            "I was an unused substitute in the 2019 Champions League Final.",
            "In the 2014 World Cup, I delivered two assists to Bony and Gervinho and was named Man of the Match.",
        ],
        "position": "Right-Back",
        "yearsActive": "2010–present",
        "story": "Serge Aurier broke through at Toulouse in 2013-14 and was moved to PSG within a year. Three seasons of Ligue 1 titles and domestic cups followed, but he never quite locked down the starting spot. Tottenham came next in 2017, four years on the right of the Spurs defence after an initial UK visa block. Then Villarreal, Nottingham Forest, Galatasaray (where he won the Süper Lig in 2023-24) and Persepolis in Iran. For Ivory Coast he made his name at the 2014 World Cup in Recife with two assists for Bony and Gervinho and a Man of the Match in the opening win against Japan, and he later captained his country to the 2023 Africa Cup of Nations title on home soil.",
        "youtube": "https://www.youtube.com/watch?v=KpG_korY2ds",
        "clubs": ["RC Lens", "Toulouse", "Paris Saint-Germain", "Tottenham Hotspur", "Villarreal", "Nottingham Forest", "Galatasaray", "Persepolis"],
        "honours": [
            "Africa Cup of Nations x2 (Ivory Coast, 2015, 2023)",
            "Ligue 1 x2 (PSG, 2014–15, 2015–16)",
            "Coupe de France x3 (PSG)",
            "Coupe de la Ligue x3 (PSG)",
            "Trophée des Champions x3 (PSG)",
            "Süper Lig (Galatasaray, 2023–24)",
        ],
        "numbers": "0 goals in 3 World Cup matches at the 2014 tournament; Man of the Match in the opening win over Japan",
        "didYouKnow": [
            "He provided two crosses for Wilfried Bony and Gervinho headers in Ivory Coast's 2014 World Cup opener against Japan, was named Man of the Match, and was sold to PSG within months.",
            "He captained Ivory Coast to the 2023 Africa Cup of Nations title on home soil despite his country sacking their head coach mid-tournament.",
            "He was an unused substitute for Tottenham in their 2019 Champions League final defeat to Liverpool.",
        ],
    },
    # ─── Day 53 ────────────────────────────────────────────────────────────
    {
        "id": "youri_djorkaeff",
        "name": "Youri Djorkaeff",
        "country": "France",
        "countryFlag": "🇫🇷",
        "years": "1984–2006",
        "aliases": ["youri djorkaeff", "djorkaeff", "the snake"],
        "clues": [
            "I played in two World Cups (1998 and 2002), scoring 1 goal across 9 games.",
            "I won the UEFA Cup and the Cup Winners' Cup with an Italian and a French club respectively.",
            "I played for two clubs in northern England later in my career.",
            "I have shared a pitch with Ronaldo in a UEFA Cup final and a World Cup final. Not necessarily on the same side.",
            "In the 1998 World Cup final, I insisted on taking the corner that Zinedine Zidane headed home for our second goal. I told him to 'stay there, you're good with the head'.",
        ],
        "position": "Attacking Midfielder",
        "yearsActive": "1984–2006",
        "story": "They called him 'The Snake' for the dribbling and the bending shots. Youri Djorkaeff came up at Monaco, won the Cup Winners' Cup with PSG in 1996, then went to Inter Milan and won the UEFA Cup in 1998 alongside Ronaldo, scoring in the final. He was France's World Cup winner that summer. He took the corner that Zidane headed in for the second goal of the final, telling the playmaker: 'Stay here, you're good with the head.' Euro 2000 winner. Then the late drift to Kaiserslautern, Bolton, Blackburn, and New York Red Bulls in MLS. Polish-Kalmyk and Armenian heritage. His father Jean captained France and played at the 1966 World Cup. He is now CEO of the FIFA Foundation.",
        "youtube": "https://www.youtube.com/watch?v=tmjFa9LB7Pg",
        "clubs": ["Grenoble", "Strasbourg", "Monaco", "Paris Saint-Germain", "Inter Milan", "Kaiserslautern", "Bolton Wanderers", "Blackburn Rovers", "New York Red Bulls (MetroStars)"],
        "honours": [
            "FIFA World Cup (France, 1998)",
            "UEFA Euro 2000 (France)",
            "FIFA Confederations Cup (France, 2001)",
            "UEFA Cup (Inter, 1997–98), scored in the final",
            "UEFA Cup Winners' Cup (PSG, 1995–96)",
            "Coupe de France (Monaco, 1990–91)",
        ],
        "numbers": "1 goal in 9 World Cup matches across two tournaments (1998 group stage)",
        "didYouKnow": [
            "He took the corner in the 1998 World Cup final that Zinedine Zidane headed in for France's second goal. He had told Zidane to 'stay there, you're good with the head'.",
            "He scored an overhead-kick winner against Germany at Euro 96 and a scissor-kick goal against Spain at Euro 2000.",
            "His father Jean Djorkaeff captained France and played at the 1966 World Cup.",
        ],
    },
    # ─── Day 54 ────────────────────────────────────────────────────────────
    {
        "id": "davor_suker",
        "name": "Davor Šuker",
        "country": "Croatia",
        "countryFlag": "🇭🇷",
        "years": "1984–2003",
        "aliases": ["davor suker", "davor šuker", "suker", "šuker"],
        "clues": [
            "I played at the 1998 World Cup, scoring 6 goals in 7 games for my country.",
            "I famously chipped Peter Schmeichel from outside the box at Euro 96 with a sublime left-foot lob.",
            "I'm the only Croatian on Pelé's FIFA 100 list of greatest living players.",
            "I won the Champions League with Real Madrid in 1997–98, two months before that World Cup.",
            "I'm Croatian. I'm my country's all-time leading international goalscorer with 45 goals.",
        ],
        "position": "Striker",
        "yearsActive": "1984–2003",
        "story": "Davor Šuker had won the Champions League with Real Madrid two months before the 1998 World Cup. Then he carried debutant Croatia to France, scored six goals across seven games including the opening goal of the semi-final against the eventual winners France, and left with the Golden Boot, the Silver Ball and a bronze medal around his neck. The chip over Peter Schmeichel at Euro 96 had announced him. The post-1998 fall was swift. He signed for Arsenal for around £3.5 million, started fifteen league games, dropped to West Ham for one season, finished at 1860 Munich. Croatia's all-time leading international goalscorer with 45 goals, and Pelé's only Croatian addition to the FIFA 100 list.",
        "youtube": "https://www.youtube.com/watch?v=L2oiDIlwbuU",
        "clubs": ["NK Osijek", "Dinamo Zagreb", "Sevilla", "Real Madrid", "Arsenal", "West Ham United", "1860 Munich"],
        "honours": [
            "1998 World Cup Golden Boot (6 goals)",
            "1998 World Cup Silver Ball",
            "1998 World Cup bronze medal (Croatia)",
            "UEFA Champions League (Real Madrid, 1997–98)",
            "La Liga (Real Madrid, 1996–97)",
            "FIFA 100 (Pelé's list, 2004)",
            "Croatia all-time top scorer (45 international goals)",
        ],
        "numbers": "6 goals in 7 World Cup matches at the 1998 tournament: Golden Boot, Silver Ball, bronze medal",
        "didYouKnow": [
            "He won both the Golden Boot (6 goals) and the Silver Ball at the 1998 World Cup, behind Ronaldo, taking debutant Croatia to a bronze medal.",
            "Two months before the 1998 World Cup he won the Champions League with Real Madrid.",
            "He is Croatia's all-time leading international goalscorer with 45 international goals, a record that still stands.",
        ],
    },
]


# ============================================================================
# Apply to Android + iOS content.json
# ============================================================================
def update_content_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["footballers"]) == 77, f"Expected 77, got {len(data['footballers'])}"

    # Construct full per-player entries with image+silhouette fields filled in
    new_entries = []
    for p in PLAYERS:
        entry = {
            "id":           p["id"],
            "name":         p["name"],
            "country":      p["country"],
            "countryFlag":  p["countryFlag"],
            "years":        p["years"],
            "aliases":      p["aliases"],
            "clues":        p["clues"],
            "image":        f"{p['id']}.jpg",
            "silhouette":   f"{p['id']}.jpg",
            "position":     p["position"],
            "yearsActive":  p["yearsActive"],
            "story":        p["story"],
            "youtube":      p["youtube"],
            "clubs":        p["clubs"],
            "honours":      p["honours"],
            "numbers":      p["numbers"],
            "didYouKnow":   p["didYouKnow"],
        }
        new_entries.append(entry)

    # Replace indices 37–53 (days 38–54)
    data["footballers"][37:54] = new_entries

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  wrote {path} (now {len(data['footballers'])} players)")


# ============================================================================
# Apply to Web players.js
# ============================================================================
def update_players_js():
    with open(WEB_PL, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"window\.PLAYERS\s*=\s*(\[.*\])\s*;?\s*\Z", src, re.DOTALL)
    if not m:
        raise RuntimeError("Could not parse players.js")
    players = json.loads(m.group(1))
    assert len(players) == 77, f"Expected 77 in players.js, got {len(players)}"

    new_entries = []
    for p in PLAYERS:
        new_entries.append({
            "id":       p["id"],
            "name":     p["name"],
            "country":  p["country"],
            "flag":     p["countryFlag"],   # web uses 'flag' not 'countryFlag'
            "years":    p["years"],
            "approved": True,
            "aliases":  p["aliases"],
            "clues":    p["clues"],
        })
    players[37:54] = new_entries

    new_src = "window.PLAYERS = " + json.dumps(players, ensure_ascii=False, indent=2) + ";\n"
    with open(WEB_PL, "w", encoding="utf-8") as f:
        f.write(new_src)
    print(f"  wrote {WEB_PL} (now {len(players)} players)")


# ============================================================================
# Apply to Web bios.js
# ============================================================================
def update_bios_js():
    with open(WEB_BIO, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"window\.BIOS\s*=\s*(\{.*\})\s*;?\s*\Z", src, re.DOTALL)
    if not m:
        raise RuntimeError("Could not parse bios.js")
    bios = json.loads(m.group(1))

    for p in PLAYERS:
        bios[p["id"]] = {
            "position":    p["position"],
            "yearsActive": p["yearsActive"],
            "story":       p["story"],
            "clubs":       p["clubs"],
            "honours":     p["honours"],
            "numbers":     p["numbers"],
            "didYouKnow":  p["didYouKnow"],
            "youtube":     p["youtube"],
        }

    new_src = "window.BIOS = " + json.dumps(bios, ensure_ascii=False, indent=2) + ";\n"
    with open(WEB_BIO, "w", encoding="utf-8") as f:
        f.write(new_src)
    print(f"  wrote {WEB_BIO} (now {len(bios)} player bios)")


# ============================================================================
# Run all
# ============================================================================
if __name__ == "__main__":
    print("Updating Android content.json…")
    update_content_json(ANDROID)
    print("Updating iOS content.json…")
    update_content_json(IOS)
    print("Updating web players.js…")
    update_players_js()
    print("Updating web bios.js…")
    update_bios_js()
    print("\nDone.")
