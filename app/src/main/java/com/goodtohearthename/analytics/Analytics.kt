package com.goodtohearthename.analytics

import android.content.Context
import android.os.Bundle
import com.google.firebase.analytics.FirebaseAnalytics

/**
 * Thin wrapper around FirebaseAnalytics so call sites don't depend on Firebase types
 * and copy/event names stay in one place.
 *
 * Consent Mode is set to default-denied in [GoodToHearApp]; with that, Firebase still
 * gathers anonymised aggregates for DAU/MAU/retention but no user-linked data.
 */
object Analytics {

    private const val EVENT_PUZZLE_STARTED = "puzzle_started"
    private const val EVENT_PUZZLE_WON = "puzzle_won"
    private const val EVENT_PUZZLE_GIVEN_UP = "puzzle_given_up"
    private const val EVENT_ARCHIVE_OPENED = "archive_opened"
    private const val EVENT_SHARE_TAPPED = "share_tapped"

    private fun fa(ctx: Context) = FirebaseAnalytics.getInstance(ctx.applicationContext)

    /**
     * Fired the first time the user interacts with today's puzzle (first guess or first skip).
     * Caller is responsible for de-duping per day.
     */
    fun puzzleStarted(ctx: Context, dayNumber: Int) {
        fa(ctx).logEvent(EVENT_PUZZLE_STARTED, Bundle().apply {
            putInt("day_number", dayNumber)
        })
    }

    fun puzzleWon(ctx: Context, dayNumber: Int, cluesUsed: Int, wrongGuesses: Int, skips: Int) {
        fa(ctx).logEvent(EVENT_PUZZLE_WON, Bundle().apply {
            putInt("day_number", dayNumber)
            putInt("clues_used", cluesUsed)
            putInt("wrong_guesses", wrongGuesses)
            putInt("skips", skips)
        })
    }

    fun puzzleGivenUp(ctx: Context, dayNumber: Int, wrongGuesses: Int, skips: Int) {
        fa(ctx).logEvent(EVENT_PUZZLE_GIVEN_UP, Bundle().apply {
            putInt("day_number", dayNumber)
            putInt("wrong_guesses", wrongGuesses)
            putInt("skips", skips)
        })
    }

    fun archiveOpened(ctx: Context, dayNumber: Int) {
        fa(ctx).logEvent(EVENT_ARCHIVE_OPENED, Bundle().apply {
            putInt("day_number", dayNumber)
        })
    }

    fun shareTapped(ctx: Context, dayNumber: Int, won: Boolean) {
        fa(ctx).logEvent(EVENT_SHARE_TAPPED, Bundle().apply {
            putInt("day_number", dayNumber)
            putBoolean("won", won)
        })
    }
}
