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
        val player = ContentRepository.forToday(app)
        val today = System.currentTimeMillis() / 86_400_000L
        val epochDay = java.time.LocalDate.of(2026, 5, 5).toEpochDay()
        val dayNumber = ((today - epochDay) + 1).toInt().coerceAtLeast(1)

        val savedState = GameStatePersistence.load(app, today)?.takeIf { it.playerId == player.id }
        val initial = savedState ?: GameState(playerId = player.id)

        setContent {
            AppTheme {
                val ctx = LocalContext.current
                val scope = rememberCoroutineScope()

                var query by remember { mutableStateOf(TextFieldValue("")) }
                val wrongGuesses = remember {
                    mutableStateListOf<GuessRecord>().apply { addAll(initial.wrongGuesses) }
                }
                var clueIndex by remember { mutableStateOf(initial.currentClueIndex) }
                var revealed by remember { mutableStateOf(initial.revealed) }
                var wasCorrect by remember { mutableStateOf(initial.wasCorrect) }

                var silhouette by remember { mutableStateOf<Bitmap?>(null) }
                var photo by remember { mutableStateOf<Bitmap?>(null) }
                var suggestions by remember { mutableStateOf<List<NameEntry>>(emptyList()) }
                var allNames by remember { mutableStateOf<List<NameEntry>>(emptyList()) }
                var stats by remember { mutableStateOf<Stats?>(null) }

                LaunchedEffect(revealed) {
                    if (revealed && stats == null) {
                        val attempt = wrongGuesses.size + (if (wasCorrect) 1 else 0)
                        stats = StatsPersistence.recordResult(ctx, today, wasCorrect, attempt)
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
                        if (matches.size < 3) emptyList() else matches
                    }.let {
                        suggestions = it
                        if (it.isNotEmpty()) suggestionsReadyAt = System.currentTimeMillis() + 200
                    }
                }

                fun persistState() {
                    GameStatePersistence.save(
                        ctx, today,
                        GameState(
                            playerId = player.id,
                            wrongGuesses = wrongGuesses.toList(),
                            currentClueIndex = clueIndex,
                            revealed = revealed,
                            wasCorrect = wasCorrect,
                        )
                    )
                    // Refresh widget so it can swap silhouette → photo on correct
                    if (revealed) {
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

                fun reveal() {
                    if (revealed) return
                    wasCorrect = false
                    revealed = true
                    persistState()
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
                    onQueryChange = { query = it },
                    onPickSuggestion = ::pickSuggestion,
                    onReveal = ::reveal,
                    onShare = ::shareResult,
                )
            }
        }
    }
}
