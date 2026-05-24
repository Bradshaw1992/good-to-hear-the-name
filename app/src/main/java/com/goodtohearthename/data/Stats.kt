package com.goodtohearthename.data

import android.content.Context

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
    val lastResultClue: Int = -1,
) {
    val winPct: Int get() = if (played == 0) 0 else (won * 100) / played
}

object StatsPersistence {
    private const val PREFS = "gthn_stats_v1"
    private const val K_PLAYED = "played"
    private const val K_WON = "won"
    private const val K_CUR_STREAK = "current_streak"
    private const val K_MAX_STREAK = "max_streak"
    private const val K_DIST = "dist"
    private const val K_LAST_WON_DAY = "last_won_day"
    private const val K_LAST_RESULT_DAY = "last_result_day"
    private const val K_LAST_RESULT_WON = "last_result_won"
    private const val K_LAST_RESULT_ATTEMPT = "last_result_attempt"
    private const val K_LAST_RESULT_CLUE = "last_result_clue"

    fun load(context: Context): Stats {
        val p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val distRaw = p.getString(K_DIST, "0,0,0,0,0,0") ?: "0,0,0,0,0,0"
        var dist = distRaw.split(",").mapNotNull { it.toIntOrNull() }.toIntArray()
        if (dist.size == 7) {
            dist = intArrayOf(dist[0], dist[1], dist[2], dist[3], dist[4] + dist[5], dist[6])
            p.edit().putString(K_DIST, dist.joinToString(",")).apply()
        }
        if (dist.size != 6) dist = IntArray(6)
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
            lastResultClue = p.getInt(K_LAST_RESULT_CLUE, -1),
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
            .putInt(K_LAST_RESULT_CLUE, s.lastResultClue)
            .apply()
    }

    fun recordResult(context: Context, today: Long, won: Boolean, attempt: Int, clue: Int): Stats {
        val s = load(context)
        if (s.lastResultDay == today) return s
        val newDist = s.distribution.copyOf()
        if (won) newDist[clue]++ else newDist[5]++
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
            lastResultAttempt = attempt,
            lastResultClue = clue,
        )
        save(context, updated)
        return updated
    }
}
