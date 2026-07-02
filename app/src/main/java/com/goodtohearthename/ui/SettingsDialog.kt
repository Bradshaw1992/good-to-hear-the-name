package com.goodtohearthename.ui

import android.Manifest
import android.content.pm.PackageManager
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.core.content.ContextCompat
import com.goodtohearthename.push.DailyReminderScheduler
import com.goodtohearthename.push.PushPrefs

@Composable
fun SettingsDialog(onDismiss: () -> Unit) {
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        val ctx = LocalContext.current

        var reminderEnabled by remember { mutableStateOf(PushPrefs.isEnabled(ctx)) }
        var reminderHour by remember { mutableStateOf(PushPrefs.reminderHour(ctx)) }
        var reminderMinute by remember { mutableStateOf(PushPrefs.reminderMinute(ctx)) }
        var showTimePicker by remember { mutableStateOf(false) }

        val requestPushPermission = rememberLauncherForActivityResult(
            contract = ActivityResultContracts.RequestPermission(),
        ) { granted ->
            if (granted) {
                PushPrefs.setEnabled(ctx, true)
                DailyReminderScheduler.scheduleNext(ctx)
                reminderEnabled = true
            } else {
                reminderEnabled = false
            }
        }

        fun handleToggle(checked: Boolean) {
            if (!checked) {
                PushPrefs.setEnabled(ctx, false)
                DailyReminderScheduler.cancel(ctx)
                reminderEnabled = false
                return
            }
            val needsRuntimePermission = Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU
            if (!needsRuntimePermission) {
                PushPrefs.setEnabled(ctx, true)
                DailyReminderScheduler.scheduleNext(ctx)
                reminderEnabled = true
                return
            }
            val granted = ContextCompat.checkSelfPermission(
                ctx, Manifest.permission.POST_NOTIFICATIONS,
            ) == PackageManager.PERMISSION_GRANTED
            if (granted) {
                PushPrefs.setEnabled(ctx, true)
                DailyReminderScheduler.scheduleNext(ctx)
                reminderEnabled = true
            } else {
                requestPushPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        Box(
            modifier = Modifier
                .fillMaxSize()
                .background(AppColors.Bg),
        ) {
            Column(modifier = Modifier.fillMaxSize()) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(start = 16.dp, end = 8.dp, top = 12.dp, bottom = 12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        "Settings",
                        color = AppColors.Text,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.weight(1f),
                    )
                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Default.Close, contentDescription = "Close", tint = AppColors.Text)
                    }
                }
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(1.dp)
                        .background(AppColors.Line),
                )

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp),
                ) {
                    Text(
                        "DAILY REMINDER",
                        color = AppColors.Muted,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 0.8.sp,
                    )
                    Spacer(Modifier.height(4.dp))

                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                "Daily reminder",
                                color = AppColors.Text,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.SemiBold,
                            )
                            Text(
                                "One ping a day when the new player drops.",
                                color = AppColors.Muted,
                                fontSize = 13.sp,
                            )
                        }
                        Switch(
                            checked = reminderEnabled,
                            onCheckedChange = { handleToggle(it) },
                        )
                    }

                    if (reminderEnabled) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { showTimePicker = true }
                                .padding(vertical = 12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Text(
                                "Reminder time",
                                color = AppColors.Text,
                                fontSize = 16.sp,
                                modifier = Modifier.weight(1f),
                            )
                            Text(
                                String.format("%02d:%02d", reminderHour, reminderMinute),
                                color = AppColors.Accent,
                                fontSize = 16.sp,
                                fontWeight = FontWeight.SemiBold,
                            )
                        }
                    }
                }
            }
        }

        if (showTimePicker) {
            PushTimePickerDialog(
                initialHour = reminderHour,
                initialMinute = reminderMinute,
                onConfirm = { hour, minute ->
                    showTimePicker = false
                    reminderHour = hour
                    reminderMinute = minute
                    PushPrefs.setReminderTime(ctx, hour, minute)
                    if (reminderEnabled) DailyReminderScheduler.scheduleNext(ctx)
                },
                onDismiss = { showTimePicker = false },
            )
        }
    }
}
