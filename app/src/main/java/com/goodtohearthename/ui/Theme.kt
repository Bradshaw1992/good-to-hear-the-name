package com.goodtohearthename.ui

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

object AppColors {
    val Bg = Color(0xFFF4EFE6)
    val Card = Color(0xFFFFFFFF)
    val CardHover = Color(0xFFF8F5EE)
    val Line = Color(0xFFE6DFD0)
    val Text = Color(0xFF14202E)
    val TextSoft = Color(0xFF3A4858)
    val Muted = Color(0xFF8A8676)
    val Accent = Color(0xFF0F7A3E)
    val AccentSoft = Color(0xFFD6EDE0)
    val Bad = Color(0xFFB03434)
    val BadSoft = Color(0xFFF5E1DE)
    val Good = Color(0xFF0F7A3E)
    val GoodSoft = Color(0xFFD6EDE0)
}

private val LightScheme = lightColorScheme(
    primary = AppColors.Accent,
    onPrimary = Color.White,
    background = AppColors.Bg,
    onBackground = AppColors.Text,
    surface = AppColors.Card,
    onSurface = AppColors.Text,
    error = AppColors.Bad,
)

@Composable
fun AppTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = LightScheme, content = content)
}
