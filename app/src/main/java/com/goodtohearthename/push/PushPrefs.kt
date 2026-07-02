package com.goodtohearthename.push

import android.content.Context

object PushPrefs {
    private const val PREFS = "gthn_push"

    const val KEY_LAST_PLAYED_DAY_INDEX = "last_played_day_index"
    const val KEY_DAILY_REMINDER_HOUR = "daily_reminder_hour"
    const val KEY_DAILY_REMINDER_MINUTE = "daily_reminder_minute"
    const val KEY_DAILY_REMINDER_ENABLED = "daily_reminder_enabled"
    const val KEY_LAST_OPEN_DAY_INDEX = "last_open_day_index"
    const val KEY_WINBACK_STAGE = "winback_stage"
    const val KEY_OPT_IN_PROMPT_SHOWN = "opt_in_prompt_shown"

    fun prefs(ctx: Context) = ctx.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun isEnabled(ctx: Context): Boolean =
        prefs(ctx).getBoolean(KEY_DAILY_REMINDER_ENABLED, false)

    fun setEnabled(ctx: Context, enabled: Boolean) =
        prefs(ctx).edit().putBoolean(KEY_DAILY_REMINDER_ENABLED, enabled).apply()

    fun reminderHour(ctx: Context): Int = prefs(ctx).getInt(KEY_DAILY_REMINDER_HOUR, 19)
    fun reminderMinute(ctx: Context): Int = prefs(ctx).getInt(KEY_DAILY_REMINDER_MINUTE, 30)

    fun setReminderTime(ctx: Context, hour: Int, minute: Int) =
        prefs(ctx).edit()
            .putInt(KEY_DAILY_REMINDER_HOUR, hour)
            .putInt(KEY_DAILY_REMINDER_MINUTE, minute)
            .apply()

    fun lastPlayedDayIndex(ctx: Context): Long =
        prefs(ctx).getLong(KEY_LAST_PLAYED_DAY_INDEX, -1L)

    fun setLastPlayedDayIndex(ctx: Context, dayIndex: Long) =
        prefs(ctx).edit().putLong(KEY_LAST_PLAYED_DAY_INDEX, dayIndex).apply()

    fun lastOpenDayIndex(ctx: Context): Long =
        prefs(ctx).getLong(KEY_LAST_OPEN_DAY_INDEX, -1L)

    fun setLastOpenDayIndex(ctx: Context, dayIndex: Long) =
        prefs(ctx).edit().putLong(KEY_LAST_OPEN_DAY_INDEX, dayIndex).apply()

    fun winbackStage(ctx: Context): Int = prefs(ctx).getInt(KEY_WINBACK_STAGE, 0)
    fun setWinbackStage(ctx: Context, stage: Int) =
        prefs(ctx).edit().putInt(KEY_WINBACK_STAGE, stage).apply()

    fun optInPromptShown(ctx: Context): Boolean =
        prefs(ctx).getBoolean(KEY_OPT_IN_PROMPT_SHOWN, false)

    fun setOptInPromptShown(ctx: Context, shown: Boolean) =
        prefs(ctx).edit().putBoolean(KEY_OPT_IN_PROMPT_SHOWN, shown).apply()
}
