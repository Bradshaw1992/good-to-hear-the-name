package com.goodtohearthename

import android.graphics.Bitmap
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshots.SnapshotStateList
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.input.TextFieldValue
import android.view.HapticFeedbackConstants
import com.goodtohearthename.data.ContentRepository
import com.goodtohearthename.data.GameState
import com.goodtohearthename.data.GameStatePersistence
import android.content.Intent
import com.goodtohearthename.data.GuessRecord
import com.goodtohearthename.data.NameEntry
import com.goodtohearthename.data.Stats
import com.goodtohearthename.data.StatsPersistence
import com.goodtohearthename.widget.DailyWidget
import androidx.glance.appwidget.updateAll
import com.goodtohearthename.ui.AppTheme
import com.goodtohearthename.ui.ArchiveDialog
import com.goodtohearthename.ui.GameScreen
import com.goodtohearthename.ui.GameUiState
import com.goodtohearthename.ui.getCommentaryQuote
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = applicationContext
        val todayMillis = System.currentTimeMillis()
        val todayDayIndex = todayMillis / 86_400_000L
        val epochDay = java.time.LocalDate.of(2026, 5, 5).toEpochDay()

        setContent {
            AppTheme {
                val ctx = LocalContext.current
                val view = LocalView.current
                val scope = rememberCoroutineScope()

                // Which day we're playing — can differ from today when using archive
                var playingDayIndex by remember { mutableStateOf(todayDayIndex) }
                var showArchive by remember { mutableStateOf(false) }

                // Derived from playingDayIndex
                val player = remember(playingDayIndex) {
                    ContentRepository.forDay(app, playingDayIndex * 86_400_000L)
                }
                val dayNumber = remember(playingDayIndex) {
                    ((playingDayIndex - epochDay) + 1).toInt().coerceAtLeast(1)
                }
                val isArchiveDay = playingDayIndex != todayDayIndex

                // Game state — reset when day changes
                var query by remember(playingDayIndex) { mutableStateOf(TextFieldValue("")) }
                val wrongGuesses = remember(playingDayIndex) {
                    val saved = GameStatePersistence.load(app, playingDayIndex)
                        ?.takeIf { it.playerId == player.id }
                    mutableStateListOf<GuessRecord>().apply {
                        addAll(saved?.wrongGuesses ?: emptyList())
                    }
                }
                var clueIndex by remember(playingDayIndex) {
                    val saved = GameStatePersistence.load(app, playingDayIndex)
                        ?.takeIf { it.playerId == player.id }
                    mutableStateOf(saved?.currentClueIndex ?: 0)
                }
                var revealed by remember(playingDayIndex) {
                    val saved = GameStatePersistence.load(app, playingDayIndex)
                        ?.takeIf { it.playerId == player.id }
                    mutableStateOf(saved?.revealed ?: false)
                }
                var wasCorrect by remember(playingDayIndex) {
                    val saved = GameStatePersistence.load(app, playingDayIndex)
                        ?.takeIf { it.playerId == player.id }
                    mutableStateOf(saved?.wasCorrect ?: false)
                }
                var skips by remember(playingDayIndex) {
                    val saved = GameStatePersistence.load(app, playingDayIndex)
                        ?.takeIf { it.playerId == player.id }
                    mutableStateOf(saved?.skips ?: 0)
                }

                var commentaryQuote by remember(playingDayIndex) {
                    val saved = GameStatePersistence.load(app, playingDayIndex)
                        ?.takeIf { it.playerId == player.id }
                    mutableStateOf(saved?.commentaryQuote)
                }
                var showCelebration by remember(playingDayIndex) { mutableStateOf(false) }

                var silhouette by remember(playingDayIndex) { mutableStateOf<Bitmap?>(null) }
                var photo by remember(playingDayIndex) { mutableStateOf<Bitmap?>(null) }
                var suggestions by remember { mutableStateOf<List<NameEntry>>(emptyList()) }
                var allNames by remember { mutableStateOf<List<NameEntry>>(emptyList()) }
                var stats by remember(playingDayIndex) { mutableStateOf<Stats?>(null) }

                LaunchedEffect(revealed, playingDayIndex) {
                    if (revealed && stats == null) {
                        val attempt = wrongGuesses.size + (if (wasCorrect) 1 else 0)
                        stats = if (playingDayIndex == todayDayIndex) {
                            StatsPersistence.recordResult(ctx, playingDayIndex, wasCorrect, attempt, clueIndex)
                        } else {
                            StatsPersistence.load(ctx)
                        }
                    }
                }


                fun shareResult() {
                    val total = player.clues.size
                    val streak = stats?.currentStreak ?: 0
                    val streakStr = if (streak > 0) " 🔥$streak" else ""
                    val line = if (wasCorrect) {
                        val clue = clueIndex + 1
                        val dots = (1..total).joinToString("") { i ->
                            when {
                                i < clue -> "🔴"
                                i == clue -> "🟢"
                                else -> "⚪"
                            }
                        }
                        "$dots $clue/$total$streakStr"
                    } else {
                        "⚫".repeat(total) + " X/$total"
                    }
                    val quoteLine = commentaryQuote?.let { "\"$it\"\n" } ?: ""
                    val text = "⚽ Good to Hear the Name — Day #$dayNumber\n$line\n${quoteLine}#GoodToHear goodtohearthename.co.uk — daily footballer quiz"
                    val intent = Intent(Intent.ACTION_SEND).apply {
                        type = "text/plain"
                        putExtra(Intent.EXTRA_TEXT, text)
                    }
                    startActivity(Intent.createChooser(intent, "Share result"))
                }

                LaunchedEffect(player.id) {
                    withContext(Dispatchers.IO) {
                        val sil = ContentRepository.loadSilhouette(ctx, player)
                        val orig = ContentRepository.loadOriginal(ctx, player)
                        silhouette = sil
                        photo = orig
                    }
                }
                LaunchedEffect(Unit) {
                    withContext(Dispatchers.IO) {
                        allNames = ContentRepository.autocompleteNames(ctx)
                    }
                }
                var suggestionsReadyAt by remember { mutableStateOf(0L) }

                LaunchedEffect(query.text, allNames) {
                    val q = ContentRepository.normalize(query.text)
                    if (q.length < 3 || allNames.isEmpty()) {
                        suggestions = emptyList()
                        return@LaunchedEffect
                    }
                    delay(350)
                    withContext(Dispatchers.Default) {
                        val prefix = mutableListOf<NameEntry>()
                        val substring = mutableListOf<NameEntry>()
                        for (e in allNames) {
                            val norm = ContentRepository.normalize(e.n)
                            when {
                                norm.startsWith(q) -> prefix.add(e)
                                norm.contains(q) -> substring.add(e)
                            }
                            if (prefix.size >= 15) break
                        }
                        val matches = (prefix + substring).take(15)
                        matches
                    }.let {
                        suggestions = it
                        if (it.isNotEmpty()) suggestionsReadyAt = System.currentTimeMillis() + 400
                    }
                }

                fun persistState() {
                    GameStatePersistence.save(
                        ctx, playingDayIndex,
                        GameState(
                            playerId = player.id,
                            wrongGuesses = wrongGuesses.toList(),
                            skips = skips,
                            currentClueIndex = clueIndex,
                            revealed = revealed,
                            wasCorrect = wasCorrect,
                            commentaryQuote = commentaryQuote,
                        )
                    )
                    // Refresh widget so it can swap silhouette → photo on correct
                    if (revealed && playingDayIndex == todayDayIndex) {
                        scope.launch { DailyWidget().updateAll(ctx) }
                    }
                }

                fun submitCurrentGuess() {
                    if (revealed) return
                    val name = query.text.trim()
                    if (name.isEmpty()) return
                    if (ContentRepository.isCorrect(player, name)) {
                        view.performHapticFeedback(HapticFeedbackConstants.CONFIRM)
                        wasCorrect = true
                        revealed = true
                        commentaryQuote = getCommentaryQuote(clueIndex + 1)
                        showCelebration = true
                        query = TextFieldValue("")
                        suggestions = emptyList()
                    } else {
                        val entry = allNames.find {
                            ContentRepository.normalize(it.n) == ContentRepository.normalize(name)
                        }
                        wrongGuesses.add(GuessRecord(name, entry?.f ?: "", entry?.y ?: ""))
                        clueIndex = (wrongGuesses.size + skips).coerceAtMost(player.clues.size - 1)
                        if (wrongGuesses.size + skips >= player.clues.size) {
                            wasCorrect = false
                            revealed = true
                        }
                        query = TextFieldValue("")
                        suggestions = emptyList()
                    }
                    persistState()
                }

                fun pickSuggestion(e: NameEntry) {
                    if (revealed || System.currentTimeMillis() < suggestionsReadyAt) return
                    query = TextFieldValue(e.n)
                    suggestions = emptyList()
                    submitCurrentGuess()
                }


                fun skipClue() {
                    if (revealed) return
                    if (clueIndex >= player.clues.size - 1) return
                    skips++
                    clueIndex = (wrongGuesses.size + skips).coerceAtMost(player.clues.size - 1)
                    if (wrongGuesses.size + skips >= player.clues.size) {
                        wasCorrect = false
                        revealed = true
                    }
                    persistState()
                }

                fun reveal() {
                    if (revealed) return
                    wasCorrect = false
                    revealed = true
                    persistState()
                }

                // Archive dialog
                if (showArchive) {
                    ArchiveDialog(
                        onDismiss = { showArchive = false },
                        onDaySelected = { selectedDayIndex ->
                            showArchive = false
                            playingDayIndex = selectedDayIndex
                        },
                    )
                }

                GameScreen(
                    player = player,
                    state = GameUiState(
                        query = query,
                        wrongGuesses = wrongGuesses.toList(),
                        skips = skips,
                        currentClueIndex = clueIndex,
                        revealed = revealed,
                        wasCorrect = wasCorrect,
                        commentaryQuote = commentaryQuote,
                    ),
                    silhouette = silhouette,
                    photo = photo,
                    suggestions = suggestions,
                    stats = stats,
                    dayNumber = dayNumber,
                    isArchiveDay = isArchiveDay,
                    onQueryChange = { query = it },
                    onPickSuggestion = ::pickSuggestion,
                    onSubmitGuess = ::submitCurrentGuess,
                    onSkip = ::skipClue,
                    onReveal = ::reveal,
                    onShare = ::shareResult,
                    onOpenArchive = { showArchive = true },
                    onBackToToday = { playingDayIndex = todayDayIndex },
                    showCelebration = showCelebration,
                    onDismissCelebration = { showCelebration = false },
                )
            }
        }
    }
}
