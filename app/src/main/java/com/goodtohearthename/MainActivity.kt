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
import com.goodtohearthename.data.GuessRecord
import com.goodtohearthename.data.NameEntry
import com.goodtohearthename.ui.AppTheme
import com.goodtohearthename.ui.GameScreen
import com.goodtohearthename.ui.GameUiState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = applicationContext
        val player = ContentRepository.forToday(app)
        val today = System.currentTimeMillis() / 86_400_000L

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
                LaunchedEffect(query.text, allNames) {
                    val q = ContentRepository.normalize(query.text)
                    if (q.length < 2 || allNames.isEmpty()) {
                        suggestions = emptyList()
                        return@LaunchedEffect
                    }
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
                        suggestions = (prefix + substring).take(8)
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
                }

                fun pickSuggestion(e: NameEntry) {
                    if (revealed) return
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
                    onQueryChange = { query = it },
                    onPickSuggestion = ::pickSuggestion,
                    onReveal = ::reveal,
                )
            }
        }
    }
}
