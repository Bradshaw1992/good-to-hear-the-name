package com.goodtohearthename.data

import android.content.Context

/**
 * Wordle-style local stats. Persisted in SharedPreferences.
 *
 * `distribution[0..4]` = wins on attempts 1..5; `distribution[5]` = losses (gave up / 5 wrong).
 */
data class Stats(
    val played: Int = 0,
    val won: Int = 0,
    val currentStreak: Int = 0,
    val maxStreak: Int = 0,
    val distribution: IntArray = IntArray(6),
    val lastWonDay: Long = -999L,
    val lastResultDay: Long = -999L,
    val lastResultWon: Boolean = false,
    val lastResultAttempt: Int = 0,
) {
    val winPct: Int get() = if (played == 0) 0 else (won * 100) / played
}

object StatsPersistence {
    private const val PREFS = "gthn_stats_v1"
    private const val K_PLAYED = "played"
    private const val K_WON = "won"
    private const val K_CUR_STREAK = "current_streak"
    private const val K_MAX_STREAK = "max_streak"
    private const val K_DIST = "dist" // comma-separated 6 ints
    private const val K_LAST_WON_DAY = "last_won_day"
    private const val K_LAST_RESULT_DAY = "last_result_day"
    private const val K_LAST_RESULT_WON = "last_result_won"
    private const val K_LAST_RESULT_ATTEMPT = "last_result_attempt"

    fun load(context: Context): Stats {
        val p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val distRaw = p.getString(K_DIST, "0,0,0,0,0,0") ?: "0,0,0,0,0,0"
        val dist = distRaw.split(",").mapNotNull { it.toIntOrNull() }.toIntArray()
            .let { if (it.size == 6) it else IntArray(6) }
        return Stats(
            played = p.getInt(K_PLAYED, 0),
            won = p.getInt(K_WON, 0),
            currentStreak = p.getInt(K_CUR_STREAK, 0),
            maxStreak = p.getInt(K_MAX_STREAK, 0),
            distribution = dist,
            lastWonDay = p.getLong(K_LAST_WON_DAY, -999L),
            lastResultDay = p.getLong(K_LAST_RESULT_DAY, -999L),
            lastResultWon = p.getBoolean(K_LAST_RESULT_WON, false),
            lastResultAttempt = p.getInt(K_LAST_RESULT_ATTEMPT, 0),
        )
    }

    fun save(context: Context, s: Stats) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
            .putInt(K_PLAYED, s.played)
            .putInt(K_WON, s.won)
            .putInt(K_CUR_STREAK, s.currentStreak)
            .putInt(K_MAX_STREAK, s.maxStreak)
            .putString(K_DIST, s.distribution.joinToString(","))
            .putLong(K_LAST_WON_DAY, s.lastWonDay)
            .putLong(K_LAST_RESULT_DAY, s.lastResultDay)
            .putBoolean(K_LAST_RESULT_WON, s.lastResultWon)
            .putInt(K_LAST_RESULT_ATTEMPT, s.lastResultAttempt)
            .apply()
    }

    /** Apply a result for `today`. No-op if already recorded today. */
    fun recordResult(context: Context, today: Long, won: Boolean, attempt: Int): Stats {
        val s = load(context)
        if (s.lastResultDay == today) return s
        val newDist = s.distribution.copyOf()
        if (won) newDist[(attempt.coerceIn(1, 5)) - 1]++ else newDist[5]++
        val newCurrent = if (won) {
            if (today - s.lastWonDay == 1L) s.currentStreak + 1 else 1
        } else 0
        val updated = s.copy(
            played = s.played + 1,
            won = if (won) s.won + 1 else s.won,
            distribution = newDist,
            currentStreak = newCurrent,
            maxStreak = if (newCurrent > s.maxStreak) newCurrent else s.maxStreak,
            lastWonDay = if (won) today else s.lastWonDay,
            lastResultDay = today,
            lastResultWon = won,
            lastResultAttempt = if (won) attempt else 0,
        )
        save(context, updated)
        return updated
    }
}
