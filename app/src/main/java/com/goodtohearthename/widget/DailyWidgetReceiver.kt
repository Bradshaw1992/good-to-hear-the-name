package com.goodtohearthename.widget

import android.appwidget.AppWidgetManager
import android.content.Context
import androidx.glance.appwidget.GlanceAppWidget
import androidx.glance.appwidget.GlanceAppWidgetReceiver

class DailyWidgetReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget: GlanceAppWidget = DailyWidget()

    override fun onEnabled(context: Context) {
        super.onEnabled(context)
        WidgetRefreshScheduler.scheduleNextRefresh(context)
    }

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray,
    ) {
        super.onUpdate(context, appWidgetManager, appWidgetIds)
        // Re-arm on every system update tick as a backstop in case a midnight alarm was missed.
        WidgetRefreshScheduler.scheduleNextRefresh(context)
    }
}
