package com.goodtohearthename

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.goodtohearthename.data.ContentRepository
import com.goodtohearthename.ui.AppTheme
import com.goodtohearthename.ui.FootballerScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val current = ContentRepository.forNow(applicationContext)
        val image = ContentRepository.loadImage(applicationContext, current)
        setContent {
            AppTheme {
                FootballerScreen(footballer = current, bitmap = image)
            }
        }
    }
}
