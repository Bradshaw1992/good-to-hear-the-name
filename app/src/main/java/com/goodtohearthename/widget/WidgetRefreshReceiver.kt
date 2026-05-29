package com.goodtohearthename.widget

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.glance.appwidget.updateAll
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * Re-renders the daily widget and re-arms the next day-boundary alarm.
 *
 * Fires for:
 *  - [WidgetRefreshScheduler.ACTION_DAILY_REFRESH] at UTC midnight (the player swap),
 *  - BOOT_COMPLETED / MY_PACKAGE_REPLACED to restore the alarm after a reboot or app update,
 *  - TIME_SET / TIMEZONE_CHANGED so a manual clock change re-arms against the new wall clock.
 */
class WidgetRefreshReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        // Always re-arm first so a single missed fire can't break the daily chain.
        WidgetRefreshScheduler.scheduleNextRefresh(context)

        val pending = goAsync()
        val appContext = context.applicationContext
        CoroutineScope(Dispatchers.Default).launch {
            try {
                DailyWidget().updateAll(appContext)
            } finally {
                pending.finish()
            }
        }
    }
}
