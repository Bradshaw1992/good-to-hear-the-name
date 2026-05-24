@file:OptIn(
    androidx.compose.foundation.layout.ExperimentalLayoutApi::class,
    androidx.compose.material3.ExperimentalMaterial3Api::class,
)

package com.goodtohearthename.ui

import android.graphics.Bitmap
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.goodtohearthename.data.Footballer
import com.goodtohearthename.data.GuessRecord
import com.goodtohearthename.data.NameEntry
import com.goodtohearthename.data.Stats

private const val TOTAL_CLUES = 5

internal val COMMENTARY_QUOTES = mapOf(
    1 to listOf(
        "He's got no right to score from there!",
        "I cannot believe what I've just seen!",
        "Absolutely world class!",
        "What a hit, son! What a hit!",
        "Would you BELIEVE IT?! That sums it all up!"
    ),
    2 to listOf(
        "Magisterial!",
        "That... is sensational!",
        "Take a bow, son!",
        "You beauty!",
        "Unbelievable, Jeff!",
        "That was liquid football!",
        "Dennis Bergkamp! Dennis Bergkamp! Dennis Bergkamp!"
    ),
    3 to listOf(
        "Cool as you like!",
        "A lovely, lovely goal!",
        "Football. Bloody hell!",
        "He's done it!",
        "They think it's all over! It is now!",
        "Corner taken quickly, ORIGI!",
        "Lovely cushioned header for GerrAAAAAARRRDD!",
        "It's two against four but one of them is Messi"
    ),
    4 to listOf(
        "It's been coming!",
        "Persistence pays off!",
        "They've broken the deadlock!",
        "He's ground that one out!",
        "Thomas... it's up for grabs now!",
        "Beckham could raise the roof here... AND HE HAS!",
        "Shabalala!!!",
        "ROMA HAVE RISEN FROM THEIR RUINS!",
        "Arshavin! Fooouuurrr!! Just Astonishing!!"
    ),
    5 to listOf(
        "And Solskjaer has won it!",
        "Right at the death!",
        "The great escape!",
        "AGUEEERROOO! I swear you'll never see anything like this ever again! So watch it. Drink it in.",
        "Here's Dele Alli... here's Lucas Moura-- OHH THEY'VE DONE IT! LUCAS MOURA WITH THE LAST KICK OF THE GAME!",
        "Here's Hogg... DEENEY!!!!!"
    )
)

fun getCommentaryQuote(clueNumber: Int): String {
    val quotes = COMMENTARY_QUOTES[clueNumber] ?: COMMENTARY_QUOTES[3]!!
    return quotes.random()
}

data class GameUiState(
    val query: TextFieldValue = TextFieldValue(""),
    val wrongGuesses: List<GuessRecord> = emptyList(),
    val skips: Int = 0,
    val currentClueIndex: Int = 0,
    val revealed: Boolean = false,
    val wasCorrect: Boolean = false,
    val commentaryQuote: String? = null,
)

@Composable
fun GameScreen(
    player: Footballer,
    state: GameUiState,
    silhouette: Bitmap?,
    photo: Bitmap?,
    suggestions: List<NameEntry>,
    stats: Stats?,
    dayNumber: Int,
    isArchiveDay: Boolean = false,
    onQueryChange: (TextFieldValue) -> Unit,
    onPickSuggestion: (NameEntry) -> Unit,
    onSubmitGuess: () -> Unit,
    onSkip: () -> Unit,
    onReveal: () -> Unit,

    onShare: () -> Unit,
    onOpenArchive: () -> Unit = {},
    onBackToToday: () -> Unit = {},
    showCelebration: Boolean = false,
    onDismissCelebration: () -> Unit = {},
) {
    Box(modifier = Modifier.fillMaxSize()) {
        Scaffold(
            containerColor = AppColors.Bg,
        ) { padding ->
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .imePadding(),
                contentPadding = PaddingValues(horizontal = 16.dp, vertical = 12.dp),
            ) {
                item { Header(dayNumber = dayNumber, onOpenArchive = onOpenArchive) }
                if (isArchiveDay) {
                    item {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(8.dp))
                                .background(AppColors.AccentSoft)
                                .clickable { onBackToToday() }
                                .padding(vertical = 6.dp),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(
                                "PLAYING DAY #$dayNumber — tap to return to today",
                                color = AppColors.Accent,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 0.08.sp,
                            )
                        }
                    }
                }
                item { Spacer(Modifier.height(12.dp)) }
                item { HeroCard(silhouette = silhouette, photo = photo, revealed = state.revealed) }

                if (state.revealed) {
                    item { Spacer(Modifier.height(14.dp)) }
                    item {
                        RevealBanner(
                            correct = state.wasCorrect,
                            playerName = player.name,
                            attempt = state.wrongGuesses.size + (if (state.wasCorrect) 1 else 0),
                            clue = state.currentClueIndex + 1,
                            totalClues = player.clues.size,
                            commentaryQuote = state.commentaryQuote,
                        )
                    }
                }

                item { Spacer(Modifier.height(14.dp)) }
                item {
                    ContentTabs(
                        player = player,
                        state = state,
                        stats = stats,
                        suggestions = suggestions,
                        isArchiveDay = isArchiveDay,
                        onQueryChange = onQueryChange,
                        onPickSuggestion = onPickSuggestion,
                        onSubmitGuess = onSubmitGuess,
                        onSkip = onSkip,
                        onReveal = onReveal,

                        onShare = onShare,
                        onBackToToday = onBackToToday,
                    )
                }
                item { Spacer(Modifier.height(40.dp)) }
            }
        }

        AnimatedVisibility(
            visible = showCelebration && state.wasCorrect && state.commentaryQuote != null,
            enter = fadeIn(),
            exit = fadeOut(),
        ) {
            // Dimmed backdrop
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.4f))
                    .clickable(
                        interactionSource = remember { androidx.compose.foundation.interaction.MutableInteractionSource() },
                        indication = null
                    ) { onDismissCelebration() },
                contentAlignment = Alignment.Center,
            ) {
                // Card
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 24.dp)
                        .clickable(enabled = false) {},
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = Color.White),
                    elevation = CardDefaults.cardElevation(defaultElevation = 8.dp),
                ) {
                    // Green top accent
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(4.dp)
                            .background(AppColors.Accent)
                    )
                    Column(
                        modifier = Modifier.fillMaxWidth().padding(28.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                    ) {
                        Text(
                            "✓ CORRECT!",
                            color = AppColors.Accent,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 1.5.sp,
                        )
                        Spacer(Modifier.height(12.dp))
                        Text(
                            "\"${state.commentaryQuote}\"",
                            color = AppColors.Text,
                            fontSize = if ((state.commentaryQuote?.length ?: 0) > 60) 18.sp else 22.sp,
                            fontWeight = FontWeight.ExtraBold,
                            textAlign = TextAlign.Center,
                            lineHeight = if ((state.commentaryQuote?.length ?: 0) > 60) 26.sp else 30.sp,
                            fontStyle = FontStyle.Italic,
                        )
                        Spacer(Modifier.height(10.dp))
                        val clue = state.currentClueIndex + 1
                        Text(
                            if (clue == 1) "First try" else "$clue/${player.clues.size}",
                            color = AppColors.Muted,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.SemiBold,
                        )
                        Spacer(Modifier.height(20.dp))
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(12.dp))
                                .background(AppColors.Accent)
                                .clickable { onShare() }
                                .padding(vertical = 14.dp),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(
                                "📤  Share with mates",
                                color = Color.White,
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Bold,
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ContentTabs(
    player: Footballer,
    state: GameUiState,
    stats: Stats?,
    suggestions: List<NameEntry>,
    isArchiveDay: Boolean,
    onQueryChange: (TextFieldValue) -> Unit,
    onPickSuggestion: (NameEntry) -> Unit,
    onSubmitGuess: () -> Unit,
    onSkip: () -> Unit,
    onReveal: () -> Unit,

    onShare: () -> Unit,
    onBackToToday: () -> Unit,
) {
    var selectedTab by remember { mutableStateOf(0) }
    val hasAbout = player.story.isNotEmpty()
    val hasHighlights = !player.youtube.isNullOrEmpty()

    // Tab bar
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(AppColors.Line)
            .padding(3.dp),
        horizontalArrangement = Arrangement.spacedBy(3.dp),
    ) {
        TabPill("Clues", selected = selectedTab == 0, locked = false, modifier = Modifier.weight(1f)) { selectedTab = 0 }
        if (hasAbout) {
            TabPill("About", selected = selectedTab == 1, locked = !state.revealed, modifier = Modifier.weight(1f)) {
                if (state.revealed) selectedTab = 1
            }
        }
        if (hasHighlights) {
            TabPill("Highlights", selected = selectedTab == 2, locked = !state.revealed, modifier = Modifier.weight(1f)) {
                if (state.revealed) selectedTab = 2
            }
        }
    }

    Spacer(Modifier.height(14.dp))

    // Tab content
    when (selectedTab) {
        0 -> CluesTabContent(
            player = player,
            state = state,
            stats = stats,
            suggestions = suggestions,
            isArchiveDay = isArchiveDay,
            onQueryChange = onQueryChange,
            onPickSuggestion = onPickSuggestion,
            onSubmitGuess = onSubmitGuess,
            onSkip = onSkip,
            onReveal = onReveal,
            onShare = onShare,
            onBackToToday = onBackToToday,
        )
        1 -> if (state.revealed) AboutTabContent(player = player)
        2 -> if (state.revealed && hasHighlights) HighlightsTabContent(youtubeUrl = player.youtube!!)
    }
}

@Composable
private fun TabPill(label: String, selected: Boolean, locked: Boolean, modifier: Modifier = Modifier, onClick: () -> Unit) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(10.dp))
            .background(if (selected) AppColors.Card else Color.Transparent)
            .clickable(enabled = !locked, onClick = onClick)
            .padding(vertical = 10.dp),
        contentAlignment = Alignment.Center,
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.Center,
        ) {
            if (locked) {
                Text("🔒 ", fontSize = 11.sp)
            }
            Text(
                label,
                color = when {
                    selected -> AppColors.Accent
                    locked -> AppColors.Muted.copy(alpha = 0.5f)
                    else -> AppColors.TextSoft
                },
                fontSize = 13.sp,
                fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
            )
        }
    }
}

@Composable
private fun CluesTabContent(
    player: Footballer,
    state: GameUiState,
    stats: Stats?,
    suggestions: List<NameEntry>,
    isArchiveDay: Boolean,
    onQueryChange: (TextFieldValue) -> Unit,
    onPickSuggestion: (NameEntry) -> Unit,
    onSubmitGuess: () -> Unit,
    onSkip: () -> Unit,
    onReveal: () -> Unit,

    onShare: () -> Unit,
    onBackToToday: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        if (!state.revealed) {
            CluesCard(player = player, upToIndex = state.currentClueIndex)
            // Input row + suggestions overlay below
            Box {
                Column {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Box(modifier = Modifier.weight(1f)) {
                            GuessInput(value = state.query, onValueChange = onQueryChange, onSubmitGuess = onSubmitGuess)
                        }
                        if (state.query.text.isNotBlank()) {
                            Box(
                                modifier = Modifier
                                    .size(48.dp)
                                    .clip(RoundedCornerShape(14.dp))
                                    .background(AppColors.Accent)
                                    .clickable { onSubmitGuess() },
                                contentAlignment = Alignment.Center,
                            ) {
                                Text("→", color = Color.White, fontSize = 20.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                    if (suggestions.isNotEmpty() && state.query.text.length >= 2) {
                        SuggestionList(suggestions = suggestions, onPick = onPickSuggestion)
                    }
                }
            }
            PipsRow(
                usedCount = state.wrongGuesses.size + state.skips,
                total = player.clues.size,
                canSkip = state.currentClueIndex < player.clues.size - 1,
                onSkip = onSkip,
                onReveal = onReveal,
            )
            if (state.wrongGuesses.isEmpty() && state.skips == 0) {
                TipCard()
            }
            if (state.wrongGuesses.isNotEmpty()) {
                WrongGuessesCard(state.wrongGuesses)
            }
        } else {
            AllCluesCard(player = player, seenUpTo = state.currentClueIndex)
            if (stats != null) {
                StatsCard(stats = stats, isArchiveDay = isArchiveDay)
            }
            ShareButton(onShare = onShare)
            if (isArchiveDay) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(14.dp))
                        .background(AppColors.Text)
                        .clickable { onBackToToday() }
                        .padding(vertical = 16.dp),
                    contentAlignment = Alignment.Center,
                ) {
                    Text("↩  Back to today's player", color = Color.White, fontSize = 15.sp, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
private fun AboutTabContent(player: Footballer) {
    Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
        BioStorySection(player)
        if (player.clubs.isNotEmpty()) {
            BioChipsCard("Notable clubs", player.clubs)
        }
        if (player.honours.isNotEmpty()) {
            BioListCard("Honours", player.honours)
        }
        if (player.numbers.isNotEmpty()) {
            BioStorySection(player, sectionTitle = "By the numbers", body = player.numbers)
        }
        if (player.didYouKnow.isNotEmpty()) {
            BioListCard("Did you know?", player.didYouKnow)
        }
    }
}

@Composable
private fun HighlightsTabContent(youtubeUrl: String) {
    val videoId = youtubeUrl.substringAfter("v=").substringBefore("&")
    val context = androidx.compose.ui.platform.LocalContext.current
    val thumbnailUrl = "https://img.youtube.com/vi/$videoId/hqdefault.jpg"
    var thumbnail by remember { mutableStateOf<Bitmap?>(null) }

    androidx.compose.runtime.LaunchedEffect(videoId) {
        kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
            try {
                val url = java.net.URL(thumbnailUrl)
                thumbnail = android.graphics.BitmapFactory.decodeStream(url.openStream())
            } catch (_: Exception) {}
        }
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable {
                val intent = android.content.Intent(
                    android.content.Intent.ACTION_VIEW,
                    android.net.Uri.parse(youtubeUrl),
                )
                context.startActivity(intent)
            },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.Black),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .aspectRatio(16f / 9f),
            contentAlignment = Alignment.Center,
        ) {
            thumbnail?.let {
                Image(
                    bitmap = it.asImageBitmap(),
                    contentDescription = "Video thumbnail",
                    contentScale = ContentScale.Crop,
                    modifier = Modifier.fillMaxSize(),
                )
            }
            Box(
                modifier = Modifier
                    .size(64.dp)
                    .clip(CircleShape)
                    .background(Color.Red),
                contentAlignment = Alignment.Center,
            ) {
                Text("▶", color = Color.White, fontSize = 28.sp)
            }
        }
    }
}

@Composable
private fun Header(dayNumber: Int, onOpenArchive: () -> Unit = {}) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(28.dp)
                    .clip(CircleShape)
                    .background(AppColors.Accent),
                contentAlignment = Alignment.Center,
            ) {
                Text("⚽", fontSize = 16.sp)
            }
            Spacer(Modifier.width(10.dp))
            Text(
                "Good to Hear the Name",
                color = AppColors.Text,
                fontSize = 18.sp,
                fontWeight = FontWeight.Bold,
            )
        }
        Spacer(Modifier.height(8.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .clip(RoundedCornerShape(50))
                    .background(AppColors.AccentSoft)
                    .padding(horizontal = 9.dp, vertical = 3.dp),
            ) {
                Text(
                    "DAY #$dayNumber",
                    color = AppColors.Accent,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 0.8.sp,
                )
            }
            Spacer(Modifier.width(10.dp))
            val epochDay = java.time.LocalDate.of(2026, 5, 5).toEpochDay()
            val playingDate = remember(dayNumber) {
                val dayEpoch = epochDay + (dayNumber - 1)
                java.text.SimpleDateFormat("EEEE d MMMM", java.util.Locale.getDefault())
                    .format(java.util.Date(dayEpoch * 86_400_000L))
                    .uppercase()
            }
            Text(playingDate, color = AppColors.Muted, fontSize = 11.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 0.5.sp)
            Text(
                " · ",
                color = AppColors.Muted,
                fontSize = 11.sp,
            )
            Text(
                "📅 Previous days",
                color = AppColors.Accent,
                fontSize = 11.sp,
                fontWeight = FontWeight.SemiBold,
                letterSpacing = 0.5.sp,
                modifier = Modifier.clickable { onOpenArchive() },
            )
        }
        Spacer(Modifier.height(10.dp))
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(1.dp)
                .background(AppColors.Line)
        )
    }
}

@Composable
private fun TipCard() {
    androidx.compose.foundation.layout.Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .border(1.dp, AppColors.Line, RoundedCornerShape(14.dp))
            .background(AppColors.Card)
            .padding(horizontal = 16.dp, vertical = 14.dp),
    ) {
        Row(verticalAlignment = Alignment.Top) {
            Text(
                "HOW TO PLAY",
                color = AppColors.Accent,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.0.sp,
                modifier = Modifier.padding(end = 12.dp, top = 1.dp),
            )
            Text(
                "One guess per clue — or skip to reveal the next clue. Either way, it costs a chance. 5 clues, 5 chances. New player every day.",
                color = AppColors.TextSoft,
                fontSize = 13.sp,
                lineHeight = 19.sp,
                modifier = Modifier.weight(1f),
            )
        }
    }
}

@Composable
private fun ShareButton(onShare: () -> Unit) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(AppColors.Accent)
            .clickable { onShare() }
            .padding(vertical = 16.dp),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            "📤  Share with mates",
            color = Color.White,
            fontSize = 15.sp,
            fontWeight = FontWeight.Bold,
        )
    }
}


@Composable
private fun HeroCard(silhouette: Bitmap?, photo: Bitmap?, revealed: Boolean) {
    // Only animate the reveal transition; when photo is null (day switch) snap to 0
    val photoAlpha by animateFloatAsState(
        targetValue = if (revealed && photo != null) 1f else 0f,
        animationSpec = if (photo == null) tween(durationMillis = 0) else tween(durationMillis = 700),
        label = "photo-fade",
    )
    // Dynamic aspect = match the silhouette's natural dimensions so cover
    // fits perfectly (no zoom, no letterbox bars). Falls back to 3:4 portrait
    // before the bitmap loads.
    val ratio = silhouette
        ?.let { it.width.toFloat() / it.height.toFloat() }
        ?: (3f / 4f)
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(ratio)
            .heightIn(max = 540.dp),
        shape = RoundedCornerShape(18.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Box(modifier = Modifier.fillMaxSize()) {
            silhouette?.let {
                Image(
                    bitmap = it.asImageBitmap(),
                    contentDescription = null,
                    contentScale = ContentScale.Crop,
                    alignment = Alignment.Center,
                    modifier = Modifier.fillMaxSize(),
                )
            }
            photo?.let {
                Image(
                    bitmap = it.asImageBitmap(),
                    contentDescription = null,
                    contentScale = ContentScale.Crop,
                    alignment = Alignment.Center,
                    modifier = Modifier.fillMaxSize().alpha(photoAlpha),
                )
            }
        }
    }
}

@Composable
private fun CluesCard(player: Footballer, upToIndex: Int) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        // Left accent bar via Row
        Row(modifier = Modifier.fillMaxWidth()) {
            Box(
                modifier = Modifier
                    .width(3.dp)
                    .heightIn(min = 60.dp)
                    .background(AppColors.Accent)
            )
            Column(modifier = Modifier.padding(horizontal = 18.dp, vertical = 16.dp)) {
                val maxIdx = upToIndex.coerceAtMost(player.clues.size - 1)
                for (i in 0..maxIdx) {
                    val isLatest = i == maxIdx
                    if (i > 0) {
                        Spacer(Modifier.height(10.dp))
                        Box(
                            modifier = Modifier.fillMaxWidth().height(1.dp).background(AppColors.Line)
                        )
                        Spacer(Modifier.height(10.dp))
                    }
                    Text(
                        "CLUE ${i + 1}",
                        color = AppColors.Accent,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.4.sp,
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(
                        player.clues[i],
                        color = if (isLatest) AppColors.Text else AppColors.TextSoft,
                        fontSize = if (isLatest) 17.sp else 15.sp,
                        lineHeight = 22.sp,
                    )
                }
            }
        }
    }
}

@Composable
private fun AllCluesCard(player: Footballer, seenUpTo: Int) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Text(
                "ALL CLUES",
                color = AppColors.Muted,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.4.sp,
            )
            Spacer(Modifier.height(6.dp))
            for (i in player.clues.indices) {
                val seen = i <= seenUpTo
                if (i > 0) {
                    Box(
                        modifier = Modifier.fillMaxWidth().height(1.dp).background(AppColors.Line)
                    )
                }
                Row(modifier = Modifier.padding(vertical = 10.dp), verticalAlignment = Alignment.Top) {
                    Text(
                        "${i + 1}.",
                        color = AppColors.Accent,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.width(22.dp),
                    )
                    Text(
                        player.clues[i],
                        color = AppColors.TextSoft,
                        fontSize = 14.sp,
                        lineHeight = 20.sp,
                        modifier = Modifier.weight(1f),
                    )
                    if (!seen) {
                        Spacer(Modifier.width(6.dp))
                        Box(
                            modifier = Modifier
                                .clip(RoundedCornerShape(6.dp))
                                .background(AppColors.AccentSoft)
                                .padding(horizontal = 6.dp, vertical = 2.dp)
                        ) {
                            Text(
                                "MISSED",
                                color = AppColors.Accent,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 0.5.sp,
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun GuessInput(value: TextFieldValue, onValueChange: (TextFieldValue) -> Unit, onSubmitGuess: () -> Unit = {}) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, AppColors.Line),
    ) {
        BasicTextField(
            value = value,
            onValueChange = onValueChange,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 18.dp, vertical = 14.dp),
            textStyle = LocalTextStyle.current.copy(
                color = AppColors.Text,
                fontSize = 16.sp,
            ),
            cursorBrush = SolidColor(AppColors.Accent),
            singleLine = true,
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Go),
            keyboardActions = KeyboardActions(onGo = { onSubmitGuess() }),
            decorationBox = { inner ->
                if (value.text.isEmpty()) {
                    Text(
                        "Type a footballer's name…",
                        color = AppColors.Muted,
                        fontSize = 16.sp,
                    )
                }
                inner()
            },
        )
    }
}

@Composable
private fun SuggestionList(suggestions: List<NameEntry>, onPick: (NameEntry) -> Unit) {
    Card(
        modifier = Modifier.fillMaxWidth().heightIn(max = 280.dp),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, AppColors.Line),
    ) {
        Column(modifier = Modifier.verticalScroll(androidx.compose.foundation.rememberScrollState())) {
            suggestions.forEachIndexed { idx, e ->
                if (idx > 0) {
                    Box(modifier = Modifier.fillMaxWidth().height(1.dp).background(AppColors.Line))
                }
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onPick(e) }
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        e.n,
                        color = AppColors.Text,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Medium,
                        modifier = Modifier.weight(1f),
                    )
                    if (e.y.isNotEmpty()) {
                        Text(
                            e.y,
                            color = AppColors.Muted,
                            fontSize = 12.sp,
                            modifier = Modifier.padding(end = 10.dp),
                        )
                    }
                    if (e.f.isNotEmpty()) {
                        Text(e.f, fontSize = 18.sp)
                    }
                }
            }
        }
    }
}

@Composable
private fun PipsRow(usedCount: Int, total: Int, canSkip: Boolean, onSkip: () -> Unit, onReveal: () -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            for (i in 0 until total) {
                val color = if (i < usedCount) AppColors.Bad else AppColors.Line
                Box(
                    modifier = Modifier
                        .size(10.dp)
                        .background(color, shape = CircleShape),
                )
            }
        }
        Spacer(Modifier.weight(1f))
        if (canSkip) {
            Text(
                "Skip clue",
                color = AppColors.Accent,
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                modifier = Modifier.clickable { onSkip() }.padding(end = 14.dp),
            )
        }
        Text(
            "Bottle it",
            color = AppColors.TextSoft,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
            modifier = Modifier.clickable { onReveal() },
        )
    }
}

@Composable
private fun WrongGuessesCard(guesses: List<GuessRecord>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(horizontal = 18.dp, vertical = 14.dp)) {
            Text(
                "PREVIOUS GUESSES",
                color = AppColors.Muted,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.4.sp,
            )
            Spacer(Modifier.height(8.dp))
            guesses.forEachIndexed { idx, g ->
                if (idx > 0) {
                    Box(modifier = Modifier.fillMaxWidth().height(1.dp).background(AppColors.Line))
                }
                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(
                        modifier = Modifier
                            .size(22.dp)
                            .clip(CircleShape)
                            .background(AppColors.BadSoft),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text("✕", color = AppColors.Bad, fontSize = 12.sp, fontWeight = FontWeight.Bold)
                    }
                    Spacer(Modifier.width(10.dp))
                    Text(g.name, color = AppColors.TextSoft, fontSize = 14.sp, modifier = Modifier.weight(1f))
                    if (g.years.isNotEmpty()) {
                        Text(g.years, color = AppColors.Muted, fontSize = 12.sp)
                        Spacer(Modifier.width(8.dp))
                    }
                    if (g.flag.isNotEmpty()) Text(g.flag, fontSize = 16.sp)
                }
            }
        }
    }
}

@Composable
private fun RevealBanner(correct: Boolean, playerName: String, attempt: Int, clue: Int = 1, totalClues: Int = 5, commentaryQuote: String? = null) {
    val color = if (correct) AppColors.Good else AppColors.Bad
    val bgColor = if (correct) AppColors.GoodSoft else AppColors.BadSoft
    val scoreLine = if (correct) {
        if (clue == 1) "First try" else "$clue/$totalClues"
    } else null
    // Subtle entrance animation: fade + slight rise
    val animProgress by animateFloatAsState(
        targetValue = 1f,
        animationSpec = tween(durationMillis = 480),
        label = "banner-in",
    )
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .alpha(animProgress),
        shape = RoundedCornerShape(14.dp),
        colors = CardDefaults.cardColors(containerColor = bgColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
        border = androidx.compose.foundation.BorderStroke(2.dp, color),
    ) {
        Column(
            modifier = Modifier.fillMaxWidth().padding(18.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            // First line: prefix + name
            val prefix = if (correct) "✓" else "✕ It was"
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "$prefix ",
                    color = color,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold,
                )
            }
            Text(
                playerName,
                color = color,
                fontSize = 24.sp,
                fontWeight = FontWeight.ExtraBold,
                textAlign = TextAlign.Center,
                letterSpacing = (-0.2).sp,
            )
            commentaryQuote?.let { quote ->
                Spacer(Modifier.height(8.dp))
                Text(
                    "\"$quote\"",
                    color = color,
                    fontSize = if (quote.length > 60) 14.sp else 17.sp,
                    fontWeight = FontWeight.Bold,
                    fontStyle = FontStyle.Italic,
                    textAlign = TextAlign.Center,
                    lineHeight = if (quote.length > 60) 20.sp else 24.sp,
                    modifier = Modifier.padding(horizontal = 8.dp),
                )
            }
            scoreLine?.let {
                Spacer(Modifier.height(6.dp))
                Text(
                    it,
                    color = color.copy(alpha = 0.85f),
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium,
                )
            }
        }
    }
}

@Composable
private fun StatsCard(stats: Stats, isArchiveDay: Boolean = false) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Text(
                "YOUR STATS",
                color = AppColors.Accent,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.4.sp,
            )
            Spacer(Modifier.height(14.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                StatCell(value = stats.played.toString(), label = "Played")
                StatCell(value = "${stats.winPct}%", label = "Win")
                StatCell(value = stats.currentStreak.toString(), label = "Streak")
                StatCell(value = stats.maxStreak.toString(), label = "Best")
            }
            Spacer(Modifier.height(18.dp))
            Text(
                "CLUE DISTRIBUTION",
                color = AppColors.Muted,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.4.sp,
            )
            Spacer(Modifier.height(8.dp))
            val labels = listOf("Clue 1", "Clue 2", "Clue 3", "Clue 4", "Clue 5", "X")
            val maxN = (stats.distribution.maxOrNull() ?: 1).coerceAtLeast(1)
            val currentDay = System.currentTimeMillis() / 86_400_000L
            val playedToday = !isArchiveDay && stats.lastResultDay == currentDay
            val todayBar = if (playedToday && stats.lastResultWon && stats.lastResultClue >= 0) stats.lastResultClue
                else if (playedToday && !stats.lastResultWon) 5
                else -1
            for (i in 0..5) {
                val n = stats.distribution[i]
                val widthFrac = if (n == 0) 0.06f else 0.06f + (n.toFloat() / maxN) * 0.74f
                val isToday = i == todayBar
                Row(modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(labels[i], color = AppColors.Muted, fontSize = 12.sp, modifier = Modifier.width(46.dp))
                    Spacer(Modifier.width(8.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth(widthFrac)
                            .height(22.dp)
                            .clip(RoundedCornerShape(4.dp))
                            .background(if (n > 0 || isToday) AppColors.Accent else AppColors.Line)
                            .then(if (isToday) Modifier.border(2.dp, AppColors.AccentSoft, RoundedCornerShape(4.dp)) else Modifier),
                        contentAlignment = Alignment.CenterEnd,
                    ) {
                        if (n > 0) {
                            Text(
                                n.toString(),
                                color = Color.White,
                                fontSize = 12.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 8.dp),
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun StatCell(value: String, label: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, color = AppColors.Text, fontSize = 26.sp, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(2.dp))
        Text(label.uppercase(), color = AppColors.Muted, fontSize = 10.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 0.6.sp)
    }
}

@Composable
private fun BioStorySection(player: Footballer, sectionTitle: String? = null, body: String? = null) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            if (sectionTitle == null) {
                Text(
                    player.name,
                    color = AppColors.Text,
                    fontSize = 28.sp,
                    fontWeight = FontWeight.Bold,
                    lineHeight = 32.sp,
                )
                Spacer(Modifier.height(4.dp))
                Text(
                    "${player.countryFlag} ${player.position} · ${player.yearsActive.ifEmpty { player.years }}",
                    color = AppColors.Muted,
                    fontSize = 13.sp,
                )
                if (player.story.isNotEmpty()) {
                    Spacer(Modifier.height(12.dp))
                    Text(
                        "THE STORY",
                        color = AppColors.Accent,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 1.4.sp,
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(player.story, color = AppColors.TextSoft, fontSize = 15.sp, lineHeight = 22.sp)
                }
            } else {
                Text(
                    sectionTitle.uppercase(),
                    color = AppColors.Accent,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.4.sp,
                )
                Spacer(Modifier.height(8.dp))
                Text(body ?: "", color = AppColors.TextSoft, fontSize = 15.sp, lineHeight = 22.sp)
            }
        }
    }
}

@Composable
private fun BioChipsCard(title: String, items: List<String>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Text(
                title.uppercase(),
                color = AppColors.Accent,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.4.sp,
            )
            Spacer(Modifier.height(10.dp))
            androidx.compose.foundation.layout.FlowRow(
                horizontalArrangement = Arrangement.spacedBy(6.dp),
                verticalArrangement = Arrangement.spacedBy(6.dp),
            ) {
                items.forEach { label ->
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(50))
                            .background(AppColors.AccentSoft)
                            .padding(horizontal = 12.dp, vertical = 4.dp),
                    ) {
                        Text(label, color = AppColors.Accent, fontSize = 13.sp, fontWeight = FontWeight.Medium)
                    }
                }
            }
        }
    }
}

@Composable
private fun BioListCard(title: String, items: List<String>) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            Text(
                title.uppercase(),
                color = AppColors.Accent,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.4.sp,
            )
            Spacer(Modifier.height(8.dp))
            items.forEach { item ->
                Row(modifier = Modifier.padding(vertical = 4.dp), verticalAlignment = Alignment.Top) {
                    Text(
                        "•",
                        color = AppColors.Accent,
                        fontSize = 14.sp,
                        modifier = Modifier.padding(end = 8.dp),
                    )
                    Text(item, color = AppColors.TextSoft, fontSize = 15.sp, lineHeight = 22.sp)
                }
            }
        }
    }
}

