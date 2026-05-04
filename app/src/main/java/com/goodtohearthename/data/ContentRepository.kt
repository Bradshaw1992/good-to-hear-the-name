package com.goodtohearthename.data

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import kotlinx.serialization.json.Json
import java.time.LocalDate

object ContentRepository {

    private val json = Json { ignoreUnknownKeys = true }

    @Volatile private var cached: List<Footballer>? = null

    fun all(context: Context): List<Footballer> {
        cached?.let { return it }
        val text = context.assets.open("content.json").bufferedReader().use { it.readText() }
        val parsed = json.decodeFromString(ContentFile.serializer(), text).footballers
        cached = parsed
        return parsed
    }

    fun forToday(context: Context, date: LocalDate = LocalDate.now()): Footballer {
        val players = all(context)
        val index = (date.toEpochDay().toInt().mod(players.size))
        return players[index]
    }

    fun loadImage(context: Context, footballer: Footballer): Bitmap? {
        return runCatching {
            context.assets.open("images/${footballer.image}").use { BitmapFactory.decodeStream(it) }
        }.getOrNull()
    }
}
