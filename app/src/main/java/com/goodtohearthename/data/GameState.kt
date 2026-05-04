package com.goodtohearthename.data

import android.content.Context

data class GuessRecord(val name: String, val flag: String, val years: String)

data class GameState(
    val playerId: String,
    val wrongGuesses: List<GuessRecord> = emptyList(),
    val currentClueIndex: Int = 0,
    val revealed: Boolean = false,
    val wasCorrect: Boolean = false,
)

object GameStatePersistence {
    private const val PREFS = "gthn_game_state"
    private const val K_DAY = "day_index"
    private const val K_PLAYER = "player_id"
    private const val K_GUESSES = "wrong_guesses"
    private const val K_CLUE = "clue_index"
    private const val K_REVEALED = "revealed"
    private const val K_CORRECT = "was_correct"

    private const val SEP = ""
    private const val ROW_SEP = ""

    fun load(context: Context, todayDayIndex: Long): GameState? {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val savedDay = prefs.getLong(K_DAY, -1L)
        if (savedDay != todayDayIndex) return null
        val playerId = prefs.getString(K_PLAYER, null) ?: return null
        val guessesRaw = prefs.getString(K_GUESSES, "") ?: ""
        val guesses = if (guessesRaw.isEmpty()) emptyList() else guessesRaw.split(ROW_SEP).map {
            val parts = it.split(SEP)
            GuessRecord(parts.getOrNull(0) ?: "", parts.getOrNull(1) ?: "", parts.getOrNull(2) ?: "")
        }
        return GameState(
            playerId = playerId,
            wrongGuesses = guesses,
            currentClueIndex = prefs.getInt(K_CLUE, 0),
            revealed = prefs.getBoolean(K_REVEALED, false),
            wasCorrect = prefs.getBoolean(K_CORRECT, false),
        )
    }

    fun save(context: Context, todayDayIndex: Long, state: GameState) {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val guessesRaw = state.wrongGuesses.joinToString(ROW_SEP) {
            "${it.name}$SEP${it.flag}$SEP${it.years}"
        }
        prefs.edit()
            .putLong(K_DAY, todayDayIndex)
            .putString(K_PLAYER, state.playerId)
            .putString(K_GUESSES, guessesRaw)
            .putInt(K_CLUE, state.currentClueIndex)
            .putBoolean(K_REVEALED, state.revealed)
            .putBoolean(K_CORRECT, state.wasCorrect)
            .apply()
    }
}
