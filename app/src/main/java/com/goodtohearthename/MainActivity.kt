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
import androidx.compose.ui.text.input.TextFieldValue
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

                var silhouette by remember(playingDayIndex) { mutableStateOf<Bitmap?>(null) }
                var photo by remember(playingDayIndex) { mutableStateOf<Bitmap?>(null) }
                var suggestions by remember { mutableStateOf<List<NameEntry>>(emptyList()) }
                var allNames by remember { mutableStateOf<List<NameEntry>>(emptyList()) }
                var stats by remember(playingDayIndex) { mutableStateOf<Stats?>(null) }

                LaunchedEffect(revealed, playingDayIndex) {
                    if (revealed && stats == null) {
                        val attempt = wrongGuesses.size + (if (wasCorrect) 1 else 0)
                        // Only record stats for today's game
                        stats = if (playingDayIndex == todayDayIndex) {
                            StatsPersistence.recordResult(ctx, playingDayIndex, wasCorrect, attempt)
                        } else {
                            StatsPersistence.load(ctx)
                        }
                    }
                }

                fun shareResult() {
                    val attempt = wrongGuesses.size + (if (wasCorrect) 1 else 0)
                    val score = if (wasCorrect) "$attempt/5" else "✕/5"
                    val grid = if (wasCorrect) "❌".repeat(attempt - 1) + "⚽" else "❌".repeat(5)
                    val text = "⚽ It's good to hear the name — Day #$dayNumber\n$score  $grid\nbradshaw1992.github.io/good-to-hear-the-name"
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
                    delay(200)
                    withContext(Dispatchers.Default) {
                        val prefix = mutableListOf<NameEntry>()
                        val substring = mutableListOf<NameEntry>()
                        for (e in allNames) {
                            val norm = ContentRepository.normalize(e.n)
                            when {
                                norm.startsWith(q) -> prefix.add(e)
                                norm.contains(q) -> substring.add(e)
                            }
                            if (prefix.size >= 8) break
                        }
                        val matches = (prefix + substring).take(8)
                        matches
                    }.let {
                        suggestions = it
                        if (it.isNotEmpty()) suggestionsReadyAt = System.currentTimeMillis() + 200
                    }
                }

                fun persistState() {
                    GameStatePersistence.save(
                        ctx, playingDayIndex,
                        GameState(
                            playerId = player.id,
                            wrongGuesses = wrongGuesses.toList(),
                            currentClueIndex = clueIndex,
                            revealed = revealed,
                            wasCorrect = wasCorrect,
                        )
                    )
                    // Refresh widget so it can swap silhouette → photo on correct
                    if (revealed && playingDayIndex == todayDayIndex) {
                        scope.launch { DailyWidget().updateAll(ctx) }
                    }
                }

                fun pickSuggestion(e: NameEntry) {
                    if (revealed || System.currentTimeMillis() < suggestionsReadyAt) return
                    if (ContentRepository.isCorrect(player, e.n)) {
                        wasCorrect = true
                        revealed = true
                        query = TextFieldValue("")
                        suggestions = emptyList()
                    } else {
                        wrongGuesses.add(GuessRecord(e.n, e.f, e.y))
                        query = TextFieldValue("")
                        suggestions = emptyList()
                        if (clueIndex < player.clues.size - 1 && wrongGuesses.size < 5) {
                            clueIndex++
                        }
                        if (wrongGuesses.size >= 5) {
                            wasCorrect = false
                            revealed = true
                        }
                    }
                    persistState()
                }

                fun skipClue() {
                    if (revealed) return
                    if (clueIndex < player.clues.size - 1) {
                        clueIndex++
                        persistState()
                    }
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
                        currentClueIndex = clueIndex,
                        revealed = revealed,
                        wasCorrect = wasCorrect,
                    ),
                    silhouette = silhouette,
                    photo = photo,
                    suggestions = suggestions,
                    stats = stats,
                    dayNumber = dayNumber,
                    isArchiveDay = isArchiveDay,
                    onQueryChange = { query = it },
                    onPickSuggestion = ::pickSuggestion,
                    onReveal = ::reveal,
                    onSkipClue = ::skipClue,
                    onShare = ::shareResult,
                    onOpenArchive = { showArchive = true },
                    onBackToToday = { playingDayIndex = todayDayIndex },
                )
            }
        }
    }
}
