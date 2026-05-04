package com.goodtohearthename.data

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import kotlinx.serialization.json.Json

object ContentRepository {

    // Pin the current footballer for previewing. Set to null for normal rotation.
    private val PINNED_ID: String? = null

    // Footballer rotates every 6 hours = 4 per day.
    private const val ROTATION_HOURS = 6L
    private const val ROTATION_MILLIS = ROTATION_HOURS * 60 * 60 * 1000

    private val json = Json { ignoreUnknownKeys = true }

    @Volatile private var cached: List<Footballer>? = null

    fun all(context: Context): List<Footballer> {
        cached?.let { return it }
        val text = context.assets.open("content.json").bufferedReader().use { it.readText() }
        val parsed = json.decodeFromString(ContentFile.serializer(), text).footballers
        cached = parsed
        return parsed
    }

    fun forNow(context: Context, nowMillis: Long = System.currentTimeMillis()): Footballer {
        val players = all(context)
        PINNED_ID?.let { id -> players.firstOrNull { it.id == id }?.let { return it } }
        val bucket = (nowMillis / ROTATION_MILLIS).toInt()
        val index = bucket.mod(players.size)
        return players[index]
    }

    fun loadImage(
        context: Context,
        footballer: Footballer,
        reqWidth: Int = 1200,
        reqHeight: Int = 1600,
    ): Bitmap? {
        return runCatching {
            val path = "images/${footballer.image}"
            val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            context.assets.open(path).use { BitmapFactory.decodeStream(it, null, bounds) }

            val opts = BitmapFactory.Options().apply {
                inSampleSize = calcSampleSize(bounds.outWidth, bounds.outHeight, reqWidth, reqHeight)
            }
            context.assets.open(path).use { BitmapFactory.decodeStream(it, null, opts) }
        }.getOrNull()
    }

    private fun calcSampleSize(srcW: Int, srcH: Int, reqW: Int, reqH: Int): Int {
        if (srcW <= 0 || srcH <= 0) return 1
        var sample = 1
        while (srcW / (sample * 2) >= reqW && srcH / (sample * 2) >= reqH) {
            sample *= 2
        }
        return sample
    }
}
