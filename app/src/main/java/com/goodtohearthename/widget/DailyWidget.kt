package com.goodtohearthename.widget

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.glance.GlanceId
import androidx.glance.GlanceModifier
import androidx.glance.GlanceTheme
import androidx.glance.Image
import androidx.glance.ImageProvider
import androidx.glance.action.actionStartActivity
import androidx.glance.action.clickable
import androidx.glance.appwidget.GlanceAppWidget
import androidx.glance.appwidget.cornerRadius
import androidx.glance.appwidget.provideContent
import androidx.glance.background
import androidx.glance.layout.Alignment
import androidx.glance.layout.Box
import androidx.glance.layout.Column
import androidx.glance.layout.ContentScale
import androidx.glance.layout.fillMaxSize
import androidx.glance.layout.fillMaxWidth
import androidx.glance.layout.padding
import androidx.glance.text.FontWeight
import androidx.glance.text.Text
import androidx.glance.text.TextStyle
import androidx.glance.unit.ColorProvider
import com.goodtohearthename.MainActivity
import com.goodtohearthename.data.ContentRepository
import com.goodtohearthename.data.GameStatePersistence

class DailyWidget : GlanceAppWidget() {

    override suspend fun provideGlance(context: Context, id: GlanceId) {
        val today = ContentRepository.forToday(context)
        val todayDay = System.currentTimeMillis() / 86_400_000L
        val state = GameStatePersistence.load(context, todayDay)
        val solved = state != null && state.playerId == today.id && state.wasCorrect

        val bitmap = if (solved) {
            ContentRepository.loadOriginal(context, today, w = 480, h = 480)
        } else {
            ContentRepository.loadSilhouette(context, today, w = 480, h = 480)
        }

        provideContent {
            GlanceTheme {
                WidgetBody(
                    image = bitmap?.let { ImageProvider(it) },
                    solvedName = if (solved) today.name else null,
                    onClick = actionStartActivity<MainActivity>(),
                )
            }
        }
    }

    @Composable
    private fun WidgetBody(
        image: ImageProvider?,
        solvedName: String?,
        onClick: androidx.glance.action.Action,
    ) {
        Box(
            modifier = GlanceModifier
                .fillMaxSize()
                .cornerRadius(20.dp)
                .background(ColorProvider(Color(0xFFF4EFE6))) // cream
                .clickable(onClick),
        ) {
            if (image != null) {
                Image(
                    provider = image,
                    contentDescription = if (solvedName != null) solvedName else "Today's mystery footballer",
                    contentScale = ContentScale.Crop,
                    modifier = GlanceModifier.fillMaxSize(),
                )
            }
            // Bottom plate: brand + tap to play / solved name
            Column(
                verticalAlignment = Alignment.Bottom,
                horizontalAlignment = Alignment.Start,
                modifier = GlanceModifier.fillMaxSize(),
            ) {
                Box(
                    modifier = GlanceModifier
                        .fillMaxWidth()
                        .background(ColorProvider(Color(0xCC0F7A3E))) // pitch green, semi-transparent
                        .padding(horizontal = 12.dp, vertical = 10.dp),
                ) {
                    if (solvedName != null) {
                        Column {
                            Text(
                                text = "✓ Today's player",
                                style = TextStyle(
                                    color = ColorProvider(Color(0xFFE0F0E5)),
                                    fontWeight = FontWeight.Normal,
                                    fontSize = 11.sp,
                                ),
                            )
                            Text(
                                text = solvedName,
                                style = TextStyle(
                                    color = ColorProvider(Color.White),
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                ),
                            )
                        }
                    } else {
                        Column {
                            Text(
                                text = "Today's player",
                                style = TextStyle(
                                    color = ColorProvider(Color.White),
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp,
                                ),
                            )
                            Text(
                                text = "Tap to play",
                                style = TextStyle(
                                    color = ColorProvider(Color(0xFFE0F0E5)),
                                    fontWeight = FontWeight.Normal,
                                    fontSize = 11.sp,
                                ),
                            )
                        }
                    }
                }
            }
        }
    }
}
