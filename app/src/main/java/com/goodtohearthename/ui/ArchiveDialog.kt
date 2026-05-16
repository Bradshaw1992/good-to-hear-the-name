package com.goodtohearthename.ui

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.goodtohearthename.data.GameStatePersistence
import java.time.LocalDate
import java.time.YearMonth
import java.time.format.TextStyle
import java.util.Locale

private val EPOCH_DATE: LocalDate = LocalDate.of(2026, 5, 5)
private val EPOCH_DAY: Long = EPOCH_DATE.toEpochDay()

@Composable
fun ArchiveDialog(
    onDismiss: () -> Unit,
    onDaySelected: (Long) -> Unit,  // dayIndex (epoch millis / 86400000)
) {
    val ctx = LocalContext.current
    val todayEpochDay = LocalDate.now().toEpochDay()
    val todayDate = LocalDate.now()

    var viewMonth by remember { mutableStateOf(YearMonth.from(todayDate)) }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false),
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(0.92f)
                .clip(RoundedCornerShape(20.dp))
                .background(Color.White)
                .padding(24.dp),
        ) {
            Column {
                // Header
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Text(
                        "📅 Previous days",
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Bold,
                        color = AppColors.Text,
                    )
                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .clip(CircleShape)
                            .background(AppColors.Bg)
                            .clickable { onDismiss() },
                        contentAlignment = Alignment.Center,
                    ) {
                        Text("✕", fontSize = 16.sp, color = AppColors.TextSoft)
                    }
                }

                Spacer(Modifier.height(18.dp))

                // Month navigation
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    val canGoPrev = viewMonth.isAfter(YearMonth.of(2026, 5)) || viewMonth == YearMonth.of(2026, 5)
                    val canGoNext = viewMonth.isBefore(YearMonth.from(todayDate))

                    MonthNavButton(
                        text = "‹",
                        enabled = viewMonth.isAfter(YearMonth.of(2026, 5)),
                        onClick = { viewMonth = viewMonth.minusMonths(1) },
                    )
                    Text(
                        "${viewMonth.month.getDisplayName(TextStyle.FULL, Locale.getDefault())} ${viewMonth.year}",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = AppColors.Text,
                    )
                    MonthNavButton(
                        text = "›",
                        enabled = canGoNext,
                        onClick = { viewMonth = viewMonth.plusMonths(1) },
                    )
                }

                Spacer(Modifier.height(14.dp))

                // Day-of-week headers
                Row(modifier = Modifier.fillMaxWidth()) {
                    listOf("S", "M", "T", "W", "T", "F", "S").forEach { dow ->
                        Box(
                            modifier = Modifier.weight(1f),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(
                                dow,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                color = AppColors.Muted,
                            )
                        }
                    }
                }

                Spacer(Modifier.height(8.dp))

                // Calendar grid
                val firstDayOfMonth = viewMonth.atDay(1)
                val startDow = firstDayOfMonth.dayOfWeek.value % 7 // Sunday = 0
                val daysInMonth = viewMonth.lengthOfMonth()

                // Build rows of 7
                val totalCells = startDow + daysInMonth
                val rows = (totalCells + 6) / 7

                for (row in 0 until rows) {
                    Row(modifier = Modifier.fillMaxWidth()) {
                        for (col in 0..6) {
                            val cellIndex = row * 7 + col
                            val dayOfMonth = cellIndex - startDow + 1

                            if (dayOfMonth < 1 || dayOfMonth > daysInMonth) {
                                // Empty cell
                                Box(modifier = Modifier.weight(1f).aspectRatio(1f))
                            } else {
                                val date = viewMonth.atDay(dayOfMonth)
                                val dayEpoch = date.toEpochDay()
                                val isFuture = dayEpoch > todayEpochDay
                                val isBeforeEpoch = dayEpoch < EPOCH_DAY
                                val isToday = dayEpoch == todayEpochDay
                                val isPlayable = !isFuture && !isBeforeEpoch

                                // Check result
                                val result = if (isPlayable) {
                                    val dayIdx = dayEpoch * 86_400_000L / 86_400_000L
                                    GameStatePersistence.getDayResult(ctx, dayIdx)
                                } else null

                                val alpha = when {
                                    isFuture || isBeforeEpoch -> 0.2f
                                    else -> 1f
                                }

                                val bgColor = when {
                                    isToday -> AppColors.AccentSoft
                                    else -> Color.Transparent
                                }

                                val ballColor = when {
                                    result != null && result.won -> AppColors.Good
                                    result != null && !result.won -> AppColors.Bad
                                    else -> AppColors.Muted
                                }

                                Box(
                                    modifier = Modifier
                                        .weight(1f)
                                        .aspectRatio(1f)
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(bgColor)
                                        .alpha(alpha)
                                        .then(
                                            if (isPlayable) Modifier.clickable {
                                                onDaySelected(dayEpoch)
                                            } else Modifier
                                        ),
                                    contentAlignment = Alignment.Center,
                                ) {
                                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                        Box(contentAlignment = Alignment.Center) {
                                            // Coloured circle behind the ball
                                            Box(
                                                modifier = Modifier
                                                    .size(24.dp)
                                                    .clip(CircleShape)
                                                    .background(ballColor.copy(alpha = 0.2f))
                                            )
                                            Text(
                                                "⚽",
                                                fontSize = 16.sp,
                                            )
                                        }
                                        Text(
                                            dayOfMonth.toString(),
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.SemiBold,
                                            color = AppColors.Muted,
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun MonthNavButton(text: String, enabled: Boolean, onClick: () -> Unit) {
    Box(
        modifier = Modifier
            .size(36.dp)
            .clip(CircleShape)
            .background(if (enabled) AppColors.Bg else Color.Transparent)
            .alpha(if (enabled) 1f else 0.3f)
            .then(if (enabled) Modifier.clickable { onClick() } else Modifier),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text,
            fontSize = 20.sp,
            color = AppColors.TextSoft,
            fontWeight = FontWeight.Bold,
        )
    }
}
