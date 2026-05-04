// 27 players + their clues + bio data.
// Clues are placeholders — Bradshaw to replace with real ones.
// Order is the order they're shown (clue 1 visible from start, then one per wrong guess).

window.PLAYERS = [
  {
    id: "vieri", name: "Christian Vieri", country: "Italy", flag: "🇮🇹",
    aliases: ["bobo vieri", "christian vieri"],
    clues: [
      "Italian striker, 1990s and 2000s",
      "Played for seven Serie A clubs",
      "World's most expensive player when signed in 1999",
      "Spent his childhood in Sydney",
      "194 club goals — Inter's lethal No. 9 alongside Ronaldo",
    ],
  },
  {
    id: "overmars", name: "Marc Overmars", country: "Netherlands", flag: "🇳🇱",
    aliases: ["marc overmars", "overmars"],
    clues: [
      "Dutch winger of the 1990s and 2000s",
      "Champions League winner with Ajax in 1995",
      "Key player in Arsenal's 1997–98 Double",
      "Once announced his £25m transfer on his personal website",
      "Tore his ACL in 1995, came back faster than ever",
    ],
  },
  {
    id: "koumas", name: "Jason Koumas", country: "Wales", flag: "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
    aliases: ["jason koumas", "koumas"],
    clues: [
      "Welsh attacking midfielder",
      "Came through the Liverpool academy with Gerrard and Owen",
      "Championship Player of the Year, 2006–07",
      "Played for Tranmere, West Brom, Cardiff and Wigan",
      "His son Lewis came through Liverpool too",
    ],
  },
  {
    id: "okocha", name: "Jay-Jay Okocha", country: "Nigeria", flag: "🇳🇬",
    aliases: ["jay-jay okocha", "jay jay okocha", "okocha", "augustine okocha"],
    clues: [
      "Nigerian attacking midfielder",
      "Olympic gold with Nigeria in 1996",
      "Famous for outrageous skill at Bolton Wanderers",
      "Played at Eintracht Frankfurt, Fenerbahçe and PSG",
      "So good they named him twice",
    ],
  },
  {
    id: "yakubu", name: "Yakubu Aiyegbeni", country: "Nigeria", flag: "🇳🇬",
    aliases: ["yakubu", "the yak", "yakubu aiyegbeni"],
    clues: [
      "Nigerian striker, 2000s",
      "Played for Maccabi Haifa, Portsmouth, Middlesbrough and Everton",
      "Scored 7 in 8 Champions League games for Maccabi Haifa",
      "Known as 'The Yak'",
      "Played barefoot on the streets of Benin City as a kid",
    ],
  },
  {
    id: "ivan_campo", name: "Iván Campo", country: "Spain", flag: "🇪🇸",
    aliases: ["ivan campo", "iván campo", "campo"],
    clues: [
      "Spanish defender / midfielder",
      "Two-time Champions League winner with Real Madrid",
      "Famous wild hair and ended up at Bolton",
      "Loved Bolton so much he turned a loan into a permanent move",
      "La Liga champion 2000–01 with Madrid",
    ],
  },
  {
    id: "rui_costa", name: "Rui Costa", country: "Portugal", flag: "🇵🇹",
    aliases: ["rui costa", "manuel rui costa"],
    clues: [
      "Portuguese attacking midfielder",
      "Champions League winner with AC Milan in 2002–03",
      "Spent seven years at Fiorentina",
      "Currently president of Benfica",
      "Starred in Nike's 1996 'Good vs Evil' commercial",
    ],
  },
  {
    id: "andy_johnson", name: "Andrew Johnson", country: "England", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    aliases: ["andy johnson", "andrew johnson", "aj"],
    clues: [
      "English striker, 2000s",
      "Crystal Palace cult hero",
      "Was eligible for Poland through his grandfather",
      "Mourinho once called him 'untrustworthy' over diving",
      "Played for Birmingham, Palace, Everton, Fulham and QPR",
    ],
  },
  {
    id: "trezeguet", name: "David Trezeguet", country: "France", flag: "🇫🇷",
    aliases: ["david trezeguet", "trezeguet", "trezegol"],
    clues: [
      "French striker, 1990s and 2000s",
      "Argentine-born, French-made",
      "Stayed at Juventus when they were relegated",
      "Scored the golden goal in the Euro 2000 final",
      "Juventus's all-time top foreign scorer",
    ],
  },
  {
    id: "jan_koller", name: "Jan Koller", country: "Czech Republic", flag: "🇨🇿",
    aliases: ["jan koller", "koller", "dino"],
    clues: [
      "Czech striker, 6'8\"",
      "All-time top scorer for the Czech Republic",
      "Bundesliga champion with Borussia Dortmund 2001–02",
      "Once went in goal for Dortmund mid-match and kept a clean sheet",
      "Nicknamed 'Dino'",
    ],
  },
  {
    id: "adel_taarabt", name: "Adel Taarabt", country: "Morocco", flag: "🇲🇦",
    aliases: ["adel taarabt", "taarabt"],
    clues: [
      "Moroccan attacking midfielder",
      "Championship Player of the Year, 2010–11 with QPR",
      "Started at Tottenham",
      "Won the Primeira Liga with Benfica in 2018–19 as a deep midfielder",
      "Switched allegiance from France youth to Morocco senior",
    ],
  },
  {
    id: "charlie_adam", name: "Charlie Adam", country: "Scotland", flag: "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    aliases: ["charlie adam", "adam"],
    clues: [
      "Scottish midfielder",
      "Heart of Blackpool's 2010–11 Premier League season",
      "Played for Liverpool, Stoke and Rangers",
      "Scored a 65-yard goal against Chelsea in 2015",
      "Captained Dundee to promotion in 2021",
    ],
  },
  {
    id: "danny_rose", name: "Danny Rose", country: "England", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    aliases: ["danny rose"],
    clues: [
      "English left-back",
      "Spent over a decade at Tottenham",
      "Champions League finalist 2018–19",
      "Premier League debut goal: a screamer against Arsenal",
      "Spoke openly about depression in 2018",
    ],
  },
  {
    id: "ravanelli", name: "Fabrizio Ravanelli", country: "Italy", flag: "🇮🇹",
    aliases: ["fabrizio ravanelli", "ravanelli", "the white feather"],
    clues: [
      "Italian striker, 1990s and 2000s",
      "Champions League winner with Juventus in 1996",
      "Famous shirt-over-the-head celebration",
      "Premier League hat-trick on debut for Middlesbrough",
      "Nicknamed 'The White Feather' for his hair",
    ],
  },
  {
    id: "geovanni", name: "Geovanni", country: "Brazil", flag: "🇧🇷",
    aliases: ["geovanni", "geovanni gomez"],
    clues: [
      "Brazilian attacking midfielder",
      "Played for Barcelona, Benfica and Manchester City",
      "Scored Hull City's first ever Premier League goal",
      "Twice Benfica Player of the Year",
      "First-ever MLS Designated Player at San Jose Earthquakes",
    ],
  },
  {
    id: "morten_gamst_pedersen", name: "Morten Gamst Pedersen", country: "Norway", flag: "🇳🇴",
    aliases: ["morten gamst pedersen", "gamst pedersen", "pedersen"],
    clues: [
      "Norwegian left winger",
      "Spent nine years at Blackburn Rovers",
      "Famous for his left foot and dead-ball deliveries",
      "Mikel Arteta once poked him in the eye on the pitch",
      "Has Sami heritage; fronted a Norwegian footballer boyband",
    ],
  },
  {
    id: "schwarzer", name: "Mark Schwarzer", country: "Australia", flag: "🇦🇺",
    aliases: ["mark schwarzer", "schwarzer"],
    clues: [
      "Australian goalkeeper",
      "Spent over a decade at Middlesbrough",
      "First non-Briton to 500 Premier League appearances",
      "Won the Premier League with Leicester in 2015–16",
      "Oldest player ever to debut in the Champions League (41)",
    ],
  },
  {
    id: "benni_mccarthy", name: "Benni McCarthy", country: "South Africa", flag: "🇿🇦",
    aliases: ["benni mccarthy", "benni", "mccarthy"],
    clues: [
      "South African striker",
      "Champions League winner with Porto in 2003–04",
      "All-time top scorer for South Africa",
      "Spent four seasons at Blackburn Rovers",
      "Scored 4 goals in 13 minutes at AFCON 1998",
    ],
  },
  {
    id: "brad_friedel", name: "Brad Friedel", country: "United States", flag: "🇺🇸",
    aliases: ["brad friedel", "friedel"],
    clues: [
      "American goalkeeper",
      "Played for Liverpool, Blackburn, Aston Villa and Tottenham",
      "Holds the Premier League record for consecutive appearances (310)",
      "Once scored from open play for Blackburn",
      "Saved two penalties in the 2002 World Cup",
    ],
  },
  {
    id: "niko_kranjcar", name: "Niko Kranjčar", country: "Croatia", flag: "🇭🇷",
    aliases: ["niko kranjcar", "kranjcar", "kranjčar"],
    clues: [
      "Croatian attacking midfielder",
      "Followed Harry Redknapp to three different clubs",
      "Played for Portsmouth, Tottenham, QPR and Rangers",
      "FA Cup winner with Portsmouth, 2007–08",
      "His father Zlatko coached Croatia to the 1998 World Cup semi-final",
    ],
  },
  {
    id: "sylvain_distin", name: "Sylvain Distin", country: "France", flag: "🇫🇷",
    aliases: ["sylvain distin", "distin"],
    clues: [
      "French centre-back",
      "Played for Manchester City, Portsmouth and Everton",
      "Most Premier League appearances by a foreign outfielder (400+)",
      "Never picked for France — once 'retired' from internationals on Twitter",
      "FA Cup winner with Portsmouth in 2008",
    ],
  },
  {
    id: "paul_konchesky", name: "Paul Konchesky", country: "England", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    aliases: ["paul konchesky", "konchesky"],
    clues: [
      "English left-back",
      "Came through Charlton, played for West Ham, Fulham, Liverpool",
      "Two England caps",
      "Disastrous brief Liverpool spell under Roy Hodgson",
      "Now runs a pie and mash café in Brentwood",
    ],
  },
  {
    id: "llorente", name: "Fernando Llorente", country: "Spain", flag: "🇪🇸",
    aliases: ["fernando llorente", "llorente", "el rey leon"],
    clues: [
      "Tall Spanish striker",
      "World Cup and Euro winner with Spain",
      "Athletic Bilbao's number 9 under Marcelo Bielsa",
      "Champions League runner-up with Spurs in 2018–19",
      "Famous for his aerial threat as a super-sub",
    ],
  },
  {
    id: "michu", name: "Michu", country: "Spain", flag: "🇪🇸",
    aliases: ["michu", "miguel pérez cuesta"],
    clues: [
      "Spanish forward, 2010s",
      "Bargain £2m signing for Swansea City",
      "Scored 22 goals in his debut Premier League season",
      "League Cup winner with Swansea in 2012–13",
      "Career ended early by chronic ankle injuries",
    ],
  },
  {
    id: "ray_parlour", name: "Ray Parlour", country: "England", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    aliases: ["ray parlour", "parlour", "the romford pele"],
    clues: [
      "English midfielder",
      "Spent twelve years at Arsenal",
      "Three Premier League titles, four FA Cups",
      "Scored a 30-yard screamer in the 2002 FA Cup final",
      "Nicknamed 'The Romford Pelé'",
    ],
  },
  {
    id: "ricardo_carvalho", name: "Ricardo Carvalho", country: "Portugal", flag: "🇵🇹",
    aliases: ["ricardo carvalho", "carvalho"],
    clues: [
      "I was born on the 18th of May 1978. I played 89 times for my country, scoring 5 goals.",
      "Jose Mourinho once suggested I should take an IQ test, after I publicly questioned why he hadn't started me in a season opener.",
      "I was named UEFA Club Defender of the Year in 2003–04.",
      "I've been managed by Jose Mourinho at three different clubs.",
      "At the 2006 World Cup, Wayne Rooney was sent off for stamping on me.",
    ],
  },
  {
    id: "wes_brown", name: "Wes Brown", country: "England", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    aliases: ["wes brown", "brown"],
    clues: [
      "English defender",
      "Spent fifteen years at Manchester United",
      "Five Premier League titles",
      "Two Champions Leagues",
      "Sir Alex Ferguson called him 'the best natural defender' at the club",
    ],
  },
];

// A pool of well-known footballer names from the 1995–2025 era.
// Used purely for the autocomplete dropdown (so players can't just process-of-eliminate).
// Format: "Name|🇺🇸". Will be merged with the 27 above for suggestions.
window.NAME_POOL = `
Alessandro Del Piero|🇮🇹
Andrea Pirlo|🇮🇹
Andriy Shevchenko|🇺🇦
Andy Cole|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Angel Di Maria|🇦🇷
Antonio Cassano|🇮🇹
Arjen Robben|🇳🇱
Ashley Cole|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Carles Puyol|🇪🇸
Cesc Fabregas|🇪🇸
Clarence Seedorf|🇳🇱
Cristiano Ronaldo|🇵🇹
Damien Duff|🇮🇪
Daniel Agger|🇩🇰
David Beckham|🏴󠁧󠁢󠁥󠁮󠁧󠁿
David Silva|🇪🇸
David Villa|🇪🇸
Davor Suker|🇭🇷
Deco|🇵🇹
Dennis Bergkamp|🇳🇱
Diego Forlan|🇺🇾
Diego Maradona|🇦🇷
Dimitar Berbatov|🇧🇬
Dirk Kuyt|🇳🇱
Dwight Yorke|🇹🇹
Eden Hazard|🇧🇪
Edgar Davids|🇳🇱
Edinson Cavani|🇺🇾
Edwin van der Sar|🇳🇱
Eidur Gudjohnsen|🇮🇸
Emile Heskey|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Eric Cantona|🇫🇷
Fabio Cannavaro|🇮🇹
Fernando Hierro|🇪🇸
Fernando Morientes|🇪🇸
Fernando Torres|🇪🇸
Filippo Inzaghi|🇮🇹
Francesco Totti|🇮🇹
Frank de Boer|🇳🇱
Frank Lampard|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Frank Rijkaard|🇳🇱
Fredrik Ljungberg|🇸🇪
Gabriel Batistuta|🇦🇷
Gareth Bale|🏴󠁧󠁢󠁷󠁬󠁳󠁿
Gary Cahill|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Gary Neville|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Gennaro Gattuso|🇮🇹
Gianfranco Zola|🇮🇹
Gianluca Vialli|🇮🇹
Gianluigi Buffon|🇮🇹
Glen Johnson|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Hernan Crespo|🇦🇷
Hugo Sanchez|🇲🇽
Iker Casillas|🇪🇸
Jaap Stam|🇳🇱
James Milner|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Jamie Carragher|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Javier Mascherano|🇦🇷
Javier Saviola|🇦🇷
Javier Zanetti|🇦🇷
Jermain Defoe|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Joe Cole|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Joe Hart|🏴󠁧󠁢󠁥󠁮󠁧󠁿
John Arne Riise|🇳🇴
John O'Shea|🇮🇪
John Terry|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Jorge Campos|🇲🇽
Jose Antonio Reyes|🇪🇸
Juan Roman Riquelme|🇦🇷
Juninho Pernambucano|🇧🇷
Junichi Inamoto|🇯🇵
Kaka|🇧🇷
Karim Benzema|🇫🇷
Kevin Davies|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Kevin Nolan|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Kim Kallstrom|🇸🇪
Kolo Toure|🇨🇮
Lassana Diarra|🇫🇷
Laurent Blanc|🇫🇷
Lee Bowyer|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Ledley King|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Lilian Thuram|🇫🇷
Lionel Messi|🇦🇷
Loic Remy|🇫🇷
Lothar Matthaus|🇩🇪
Louis Saha|🇫🇷
Luca Toni|🇮🇹
Lucas Radebe|🇿🇦
Luis Figo|🇵🇹
Luis Suarez|🇺🇾
Luka Modric|🇭🇷
Mario Balotelli|🇮🇹
Mario Gomez|🇩🇪
Mario Stanic|🇭🇷
Marouane Chamakh|🇲🇦
Marouane Fellaini|🇧🇪
Mauro Camoranesi|🇮🇹
Mehmet Scholl|🇩🇪
Mesut Ozil|🇩🇪
Michael Ballack|🇩🇪
Michael Carrick|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Michael Essien|🇬🇭
Michael Owen|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Mikel Arteta|🇪🇸
Mikel John Obi|🇳🇬
Miroslav Klose|🇩🇪
Nemanja Vidic|🇷🇸
Nicolas Anelka|🇫🇷
Nigel de Jong|🇳🇱
Nwankwo Kanu|🇳🇬
Obafemi Martins|🇳🇬
Olivier Bernard|🇫🇷
Olof Mellberg|🇸🇪
Oliver Kahn|🇩🇪
Park Ji-sung|🇰🇷
Patrice Evra|🇫🇷
Patrick Kluivert|🇳🇱
Patrick Vieira|🇫🇷
Paul Scholes|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Paulo Maldini|🇮🇹
Paulo Wanchope|🇨🇷
Pavel Nedved|🇨🇿
Peter Crouch|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Peter Schmeichel|🇩🇰
Petr Cech|🇨🇿
Philippe Albert|🇧🇪
Pierre van Hooijdonk|🇳🇱
Rafael Marquez|🇲🇽
Raul|🇪🇸
Rene Meulensteen|🇳🇱
Ricardo Quaresma|🇵🇹
Rio Ferdinand|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Robbie Fowler|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Robbie Keane|🇮🇪
Robbie Savage|🏴󠁧󠁢󠁷󠁬󠁳󠁿
Robert Pires|🇫🇷
Roberto Carlos|🇧🇷
Robin van Persie|🇳🇱
Roman Pavlyuchenko|🇷🇺
Romario|🇧🇷
Ronaldinho|🇧🇷
Ronaldo Nazario|🇧🇷
Roque Santa Cruz|🇵🇾
Roy Keane|🇮🇪
Ruud Gullit|🇳🇱
Ruud van Nistelrooy|🇳🇱
Ryan Babel|🇳🇱
Ryan Giggs|🏴󠁧󠁢󠁷󠁬󠁳󠁿
Sami Hyypia|🇫🇮
Samir Nasri|🇫🇷
Samuel Eto'o|🇨🇲
Sebastian Larsson|🇸🇪
Sergio Aguero|🇦🇷
Sergio Busquets|🇪🇸
Sergio Ramos|🇪🇸
Shaun Wright-Phillips|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Shay Given|🇮🇪
Shinji Kagawa|🇯🇵
Sol Campbell|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Sotirios Kyrgiakos|🇬🇷
Stephen Ireland|🇮🇪
Steve McManaman|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Steven Gerrard|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Sulley Muntari|🇬🇭
Teddy Sheringham|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Theo Walcott|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Thierry Henry|🇫🇷
Thomas Gravesen|🇩🇰
Thomas Muller|🇩🇪
Tim Cahill|🇦🇺
Tim Howard|🇺🇸
Tomas Rosicky|🇨🇿
Tony Adams|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Tugay Kerimoglu|🇹🇷
Vincent Kompany|🇧🇪
Wayne Bridge|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Wayne Rooney|🏴󠁧󠁢󠁥󠁮󠁧󠁿
Wesley Sneijder|🇳🇱
Xabi Alonso|🇪🇸
Xavi Hernandez|🇪🇸
Yaya Toure|🇨🇮
Yossi Benayoun|🇮🇱
Younes Kaboul|🇫🇷
Zinedine Zidane|🇫🇷
Zlatan Ibrahimovic|🇸🇪
`.trim().split("\n").map(line => {
  const [name, flag] = line.split("|");
  return { name: name.trim(), flag: (flag || "").trim() };
});
