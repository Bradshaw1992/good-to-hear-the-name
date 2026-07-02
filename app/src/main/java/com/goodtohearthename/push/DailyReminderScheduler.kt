package com.goodtohearthename.push

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import java.util.Calendar

object DailyReminderScheduler {
    private const val REQ_DAILY = 1001

    fun scheduleNext(ctx: Context) {
        if (!PushPrefs.isEnabled(ctx)) return
        val am = ctx.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val triggerAt = nextTriggerMillis(
            PushPrefs.reminderHour(ctx),
            PushPrefs.reminderMinute(ctx),
        )
        am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, triggerAt, pendingIntent(ctx))
    }

    fun cancel(ctx: Context) {
        val am = ctx.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        am.cancel(pendingIntent(ctx))
    }

    private fun pendingIntent(ctx: Context): PendingIntent {
        val intent = Intent(ctx, DailyReminderReceiver::class.java).apply {
            action = DailyReminderReceiver.ACTION_FIRE
        }
        return PendingIntent.getBroadcast(
            ctx, REQ_DAILY, intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
    }

    private fun nextTriggerMillis(hour: Int, minute: Int): Long {
        val now = Calendar.getInstance()
        val target = (now.clone() as Calendar).apply {
            set(Calendar.HOUR_OF_DAY, hour)
            set(Calendar.MINUTE, minute)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        if (!target.after(now)) target.add(Calendar.DAY_OF_YEAR, 1)
        return target.timeInMillis
    }
}
