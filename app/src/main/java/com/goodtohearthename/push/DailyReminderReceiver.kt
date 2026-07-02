package com.goodtohearthename.push

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.goodtohearthename.MainActivity
import com.goodtohearthename.R

class DailyReminderReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != ACTION_FIRE) return

        // Always re-arm tomorrow first so a crash below can't break the chain.
        DailyReminderScheduler.scheduleNext(context)

        if (!PushPrefs.isEnabled(context)) return
        if (!hasPostPermission(context)) return

        val todayIndex = System.currentTimeMillis() / 86_400_000L

        // Smart silence: already played today.
        if (PushPrefs.lastPlayedDayIndex(context) == todayIndex) return

        val message = pickMessage(context, todayIndex) ?: return
        postNotification(context, message)
    }

    /**
     * Decides which line to post tonight (or null = stay silent).
     *
     * Winback stages:
     *   0 = no winback fired yet
     *   1 = first winback fired (silent until day 21)
     *   2 = second winback fired (stop forever)
     */
    private fun pickMessage(ctx: Context, todayIndex: Long): String? {
        val lastOpen = PushPrefs.lastOpenDayIndex(ctx)
        val daysSinceOpen = if (lastOpen < 0) Long.MAX_VALUE else todayIndex - lastOpen
        val stage = PushPrefs.winbackStage(ctx)

        return when {
            stage >= 2 -> null
            stage == 1 && daysSinceOpen >= 21 -> {
                PushPrefs.setWinbackStage(ctx, 2)
                WINBACK_FINAL
            }
            stage == 1 -> null
            stage == 0 && daysSinceOpen >= 7 -> {
                PushPrefs.setWinbackStage(ctx, 1)
                WINBACK_FIRST
            }
            else -> DAILY_COPY.random()
        }
    }

    private fun hasPostPermission(ctx: Context): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) return true
        return ContextCompat.checkSelfPermission(
            ctx, Manifest.permission.POST_NOTIFICATIONS,
        ) == PackageManager.PERMISSION_GRANTED
    }

    private fun postNotification(ctx: Context, text: String) {
        ensureChannel(ctx)
        val tapIntent = Intent(ctx, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val pi = PendingIntent.getActivity(
            ctx, 0, tapIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val n = NotificationCompat.Builder(ctx, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle("Good to Hear")
            .setContentText(text)
            .setAutoCancel(true)
            .setContentIntent(pi)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()
        val nm = ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        nm.notify(NOTIF_ID_DAILY, n)
    }

    private fun ensureChannel(ctx: Context) {
        val nm = ctx.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        if (nm.getNotificationChannel(CHANNEL_ID) != null) return
        nm.createNotificationChannel(
            NotificationChannel(
                CHANNEL_ID, "Daily player",
                NotificationManager.IMPORTANCE_DEFAULT,
            ).apply { description = "One ping a day when the new player drops." }
        )
    }

    companion object {
        const val ACTION_FIRE = "com.goodtohearthename.push.DAILY_FIRE"
        const val CHANNEL_ID = "daily_player"
        const val NOTIF_ID_DAILY = 2001

        private val DAILY_COPY = listOf(
            "New player's up.",
            "Today's player is waiting.",
            "New day, new player.",
            "Fresh silhouette. Five clues.",
        )

        private const val WINBACK_FIRST = "Six players since you were last in."
        private const val WINBACK_FINAL = "Still here when you want it."
    }
}
