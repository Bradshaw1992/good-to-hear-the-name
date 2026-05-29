package com.goodtohearthename.widget

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent

/**
 * Arms a single alarm at the next UTC day boundary — the exact instant
 * [com.goodtohearthename.data.ContentRepository.forDay] switches to the next player
 * (day index = System.currentTimeMillis() / 86_400_000). The receiver re-renders the
 * widget and re-arms for the following day, so the silhouette swaps the moment the day
 * rolls over instead of waiting for the puzzle to be solved.
 */
object WidgetRefreshScheduler {

    const val ACTION_DAILY_REFRESH = "com.goodtohearthename.widget.ACTION_DAILY_REFRESH"
    private const val REQUEST_CODE = 9001
    private const val DAY_MILLIS = 86_400_000L

    fun scheduleNextRefresh(context: Context) {
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as? AlarmManager ?: return
        val now = System.currentTimeMillis()
        // Next multiple of a day in epoch millis, plus a 1s buffer so the day index has ticked over.
        val nextBoundary = ((now / DAY_MILLIS) + 1) * DAY_MILLIS + 1_000L

        val pendingIntent = PendingIntent.getBroadcast(
            context,
            REQUEST_CODE,
            Intent(context, WidgetRefreshReceiver::class.java).setAction(ACTION_DAILY_REFRESH),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )

        // Inexact + allow-while-idle: needs no exact-alarm permission and still fires in Doze.
        // A few minutes' drift is fine for a once-a-day widget swap.
        alarmManager.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, nextBoundary, pendingIntent)
    }
}
