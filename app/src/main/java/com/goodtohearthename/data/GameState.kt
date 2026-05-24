package com.goodtohearthename.data

import android.content.Context

data class GuessRecord(val name: String, val flag: String, val years: String)

data class GameState(
    val playerId: String,
    val wrongGuesses: List<GuessRecord> = emptyList(),
    val skips: Int = 0,
    val currentClueIndex: Int = 0,
    val revealed: Boolean = false,
    val wasCorrect: Boolean = false,
    val commentaryQuote: String? = null,
)

/** Result for a completed day — used by the archive calendar. */
data class DayResult(val won: Boolean, val attempt: Int)

object GameStatePersistence {
    private const val PREFS = "gthn_game_state"
    private const val K_DAY = "day_index"
    private const val K_PLAYER = "player_id"
    private const val K_GUESSES = "wrong_guesses"
    private const val K_CLUE = "clue_index"
    private const val K_REVEALED = "revealed"
    private const val K_CORRECT = "was_correct"
    private const val K_SKIPS = "skips"
    private const val K_QUOTE = "commentary_quote"

    // Per-day prefs
    private const val PREFS_PREFIX = "gthn_day_"

    private const val SEP = ""
    private const val ROW_SEP = ""

    /** Load game state for a specific day. */
    fun load(context: Context, dayIndex: Long): GameState? {
        // Try per-day store first
        val perDay = loadPerDay(context, dayIndex)
        if (perDay != null) return perDay
        // Fall back to legacy single-day store
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val savedDay = prefs.getLong(K_DAY, -1L)
        if (savedDay != dayIndex) return null
        return loadFromPrefs(prefs)
    }

    private fun loadPerDay(context: Context, dayIndex: Long): GameState? {
        val prefs = context.getSharedPreferences(PREFS_PREFIX + dayIndex, Context.MODE_PRIVATE)
        return loadFromPrefs(prefs)
    }

    private fun loadFromPrefs(prefs: android.content.SharedPreferences): GameState? {
        val playerId = prefs.getString(K_PLAYER, null) ?: return null
        val guessesRaw = prefs.getString(K_GUESSES, "") ?: ""
        val guesses = if (guessesRaw.isEmpty()) emptyList() else guessesRaw.split(ROW_SEP).map {
            val parts = it.split(SEP)
            GuessRecord(parts.getOrNull(0) ?: "", parts.getOrNull(1) ?: "", parts.getOrNull(2) ?: "")
        }
        val commentaryQuote = prefs.getString(K_QUOTE, null)
        return GameState(
            playerId = playerId,
            wrongGuesses = guesses,
            skips = prefs.getInt(K_SKIPS, 0),
            currentClueIndex = prefs.getInt(K_CLUE, 0),
            revealed = prefs.getBoolean(K_REVEALED, false),
            wasCorrect = prefs.getBoolean(K_CORRECT, false),
            commentaryQuote = commentaryQuote,
        )
    }

    /** Save game state for a specific day (per-day store). */
    fun save(context: Context, dayIndex: Long, state: GameState) {
        val guessesRaw = state.wrongGuesses.joinToString(ROW_SEP) {
            "${it.name}$SEP${it.flag}$SEP${it.years}"
        }
        // Write to per-day store
        context.getSharedPreferences(PREFS_PREFIX + dayIndex, Context.MODE_PRIVATE).edit()
            .putString(K_PLAYER, state.playerId)
            .putString(K_GUESSES, guessesRaw)
            .putInt(K_SKIPS, state.skips)
            .putInt(K_CLUE, state.currentClueIndex)
            .putBoolean(K_REVEALED, state.revealed)
            .putBoolean(K_CORRECT, state.wasCorrect)
            .putString(K_QUOTE, state.commentaryQuote)
            .apply()
        // Also write to legacy store so the widget still works
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putLong(K_DAY, dayIndex)
            .putString(K_PLAYER, state.playerId)
            .putString(K_GUESSES, guessesRaw)
            .putInt(K_SKIPS, state.skips)
            .putInt(K_CLUE, state.currentClueIndex)
            .putBoolean(K_REVEALED, state.revealed)
            .putBoolean(K_CORRECT, state.wasCorrect)
            .putString(K_QUOTE, state.commentaryQuote)
            .apply()
    }

    /** Get result for a completed day (for the archive calendar). */
    fun getDayResult(context: Context, dayIndex: Long): DayResult? {
        val state = load(context, dayIndex) ?: return null
        if (!state.revealed) return null
        val attempt = state.wrongGuesses.size + (if (state.wasCorrect) 1 else 0)
        return DayResult(won = state.wasCorrect, attempt = attempt)
    }
}
