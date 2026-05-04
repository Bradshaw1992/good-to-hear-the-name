package com.goodtohearthename

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import com.goodtohearthename.data.ContentRepository
import com.goodtohearthename.ui.AppTheme
import com.goodtohearthename.ui.FootballerScreen

class MainActivity : ComponentActivity() {

    companion object {
        // Dev mode shows ← → arrows to step through players for previewing.
        // Flip to false for the public build.
        const val DEV_MODE = true
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val players = ContentRepository.all(applicationContext)
        val startIndex = players.indexOfFirst {
            it.id == ContentRepository.forNow(applicationContext).id
        }.coerceAtLeast(0)

        setContent {
            AppTheme {
                var index by remember { mutableIntStateOf(startIndex) }
                val current = players[index]
                val image = remember(current.id) {
                    ContentRepository.loadImage(applicationContext, current)
                }
                FootballerScreen(
                    footballer = current,
                    bitmap = image,
                    showNav = DEV_MODE,
                    position = index + 1,
                    total = players.size,
                    onPrev = { index = (index - 1 + players.size).mod(players.size) },
                    onNext = { index = (index + 1).mod(players.size) },
                )
            }
        }
    }
}
