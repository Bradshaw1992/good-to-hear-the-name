@file:OptIn(
    androidx.compose.foundation.layout.ExperimentalLayoutApi::class,
    androidx.compose.material3.ExperimentalMaterial3Api::class,
)

package com.goodtohearthename.ui

import android.graphics.Bitmap
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
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.goodtohearthename.data.Footballer
import com.goodtohearthename.data.GuessRecord
import com.goodtohearthename.data.NameEntry
import com.goodtohearthename.data.Stats

private const val MAX_GUESSES = 5

data class GameUiState(
    val query: TextFieldValue = TextFieldValue(""),
    val wrongGuesses: List<GuessRecord> = emptyList(),
    val currentClueIndex: Int = 0,
    val revealed: Boolean = false,
    val wasCorrect: Boolean = false,
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
    onQueryChange: (TextFieldValue) -> Unit,
    onPickSuggestion: (NameEntry) -> Unit,
    onReveal: () -> Unit,
    onShare: () -> Unit,
) {
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
            item { Header(dayNumber = dayNumber) }
            item { Spacer(Modifier.height(12.dp)) }
            item { HeroCard(silhouette = silhouette, photo = photo, revealed = state.revealed) }
            item { Spacer(Modifier.height(14.dp)) }
            item { CluesCard(player = player, upToIndex = state.currentClueIndex) }

            if (!state.revealed) {
                item { Spacer(Modifier.height(14.dp)) }
                if (suggestions.isNotEmpty() && state.query.text.length >= 2) {
                    item {
                        SuggestionList(suggestions = suggestions, onPick = onPickSuggestion)
                    }
                    item { Spacer(Modifier.height(8.dp)) }
                }
                item {
                    GuessInput(
                        value = state.query,
                        onValueChange = onQueryChange,
                    )
                }
                item { Spacer(Modifier.height(10.dp)) }
                item {
                    PipsRow(
                        used = state.wrongGuesses.size,
                        max = MAX_GUESSES,
                        onReveal = onReveal,
                    )
                }
                if (state.wrongGuesses.isEmpty()) {
                    item { Spacer(Modifier.height(10.dp)) }
                    item { TipCard() }
                }
                if (state.wrongGuesses.isNotEmpty()) {
                    item { Spacer(Modifier.height(12.dp)) }
                    item { WrongGuessesCard(state.wrongGuesses) }
                }
            } else {
                item { Spacer(Modifier.height(14.dp)) }
                item {
                    RevealBanner(
                        correct = state.wasCorrect,
                        playerName = player.name,
                        attempt = state.wrongGuesses.size + (if (state.wasCorrect) 1 else 0),
                    )
                }
                item { Spacer(Modifier.height(12.dp)) }
                item { AllCluesCard(player = player, seenUpTo = state.currentClueIndex) }
                if (stats != null) {
                    item { Spacer(Modifier.height(12.dp)) }
                    item { StatsCard(stats = stats) }
                }
                item { Spacer(Modifier.height(12.dp)) }
                item { ShareButton(onShare = onShare) }
                if (player.story.isNotEmpty()) {
                    item { Spacer(Modifier.height(12.dp)) }
                    item { BioStorySection(player) }
                }
                if (player.clubs.isNotEmpty()) {
                    item { Spacer(Modifier.height(10.dp)) }
                    item { BioChipsCard("Notable clubs", player.clubs) }
                }
                if (player.honours.isNotEmpty()) {
                    item { Spacer(Modifier.height(10.dp)) }
                    item { BioListCard("Honours", player.honours) }
                }
                if (player.numbers.isNotEmpty()) {
                    item { Spacer(Modifier.height(10.dp)) }
                    item { BioStorySection(player, sectionTitle = "By the numbers", body = player.numbers) }
                }
                if (player.didYouKnow.isNotEmpty()) {
                    item { Spacer(Modifier.height(10.dp)) }
                    item { BioListCard("Did you know?", player.didYouKnow) }
                }
            }
            item { Spacer(Modifier.height(40.dp)) }
        }
    }
}

@Composable
private fun Header(dayNumber: Int) {
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
                "It's good to hear the name",
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
            val today = remember {
                java.text.SimpleDateFormat("EEEE d MMMM", java.util.Locale.getDefault())
                    .format(java.util.Date())
                    .uppercase()
            }
            Text(today, color = AppColors.Muted, fontSize = 11.sp, fontWeight = FontWeight.SemiBold, letterSpacing = 0.5.sp)
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
                "Type a footballer's name above. You get 5 guesses and a new clue each time you're wrong. New player every day.",
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
    val photoAlpha by animateFloatAsState(
        targetValue = if (revealed) 1f else 0f,
        animationSpec = tween(durationMillis = 700),
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
                "ALL 5 CLUES",
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
private fun GuessInput(value: TextFieldValue, onValueChange: (TextFieldValue) -> Unit) {
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
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = AppColors.Card),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        border = androidx.compose.foundation.BorderStroke(1.dp, AppColors.Line),
    ) {
        Column {
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
private fun PipsRow(used: Int, max: Int, onReveal: () -> Unit) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(horizontal = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        repeat(max) { i ->
            Box(
                modifier = Modifier
                    .padding(end = 6.dp)
                    .size(14.dp)
                    .clip(CircleShape)
                    .background(if (i < used) AppColors.Bad else AppColors.Line)
            )
        }
        Spacer(Modifier.width(6.dp))
        Text(
            "${max - used} left",
            color = AppColors.TextSoft,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
        )
        Spacer(Modifier.weight(1f))
        Text(
            "Bottle it",
            color = AppColors.Accent,
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
private fun RevealBanner(correct: Boolean, playerName: String, attempt: Int) {
    val color = if (correct) AppColors.Good else AppColors.Bad
    val bgColor = if (correct) AppColors.GoodSoft else AppColors.BadSoft
    val ordinal = when (attempt) {
        1 -> "1st"; 2 -> "2nd"; 3 -> "3rd"; else -> "${attempt}th"
    }
    val scoreLine = if (correct) {
        if (attempt == 1) "First try 🎯" else "Nailed it on the $ordinal"
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
private fun StatsCard(stats: Stats) {
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
                "GUESS DISTRIBUTION",
                color = AppColors.Muted,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.4.sp,
            )
            Spacer(Modifier.height(8.dp))
            val labels = listOf("1", "2", "3", "4", "5", "X")
            val maxN = (stats.distribution.maxOrNull() ?: 1).coerceAtLeast(1)
            val todayBar = if (stats.lastResultWon) (stats.lastResultAttempt - 1) else 5
            for (i in 0..5) {
                val n = stats.distribution[i]
                val widthFrac = if (n == 0) 0.06f else 0.06f + (n.toFloat() / maxN) * 0.74f
                val isToday = i == todayBar
                Row(modifier = Modifier.fillMaxWidth().padding(vertical = 3.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(labels[i], color = AppColors.Muted, fontSize = 13.sp, modifier = Modifier.width(20.dp))
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
