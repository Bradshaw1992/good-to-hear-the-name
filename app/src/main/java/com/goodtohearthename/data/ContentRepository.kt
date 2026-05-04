package com.goodtohearthename.data

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import kotlinx.serialization.json.Json
import kotlinx.serialization.builtins.ListSerializer
import java.text.Normalizer

object ContentRepository {

    // Pin the current footballer for previewing. Set to null for normal rotation.
    private val PINNED_ID: String? = null

    private val json = Json { ignoreUnknownKeys = true }

    @Volatile private var cachedPlayers: List<Footballer>? = null
    @Volatile private var cachedNames: List<NameEntry>? = null

    fun all(context: Context): List<Footballer> {
        cachedPlayers?.let { return it }
        val text = context.assets.open("content.json").bufferedReader().use { it.readText() }
        val parsed = json.decodeFromString(ContentFile.serializer(), text).footballers
        cachedPlayers = parsed
        return parsed
    }

    /** All players merged with the big autocomplete pool. Lazy-loaded — heavy on first call. */
    fun autocompleteNames(context: Context): List<NameEntry> {
        cachedNames?.let { return it }
        val players = all(context)
        val seeded = players.map { NameEntry(n = it.name, f = it.countryFlag, y = it.years) }
        val text = context.assets.open("names.json").bufferedReader().use { it.readText() }
        val big = json.decodeFromString(ListSerializer(NameEntry.serializer()), text)
        val seen = seeded.map { it.n.lowercase() }.toMutableSet()
        val merged = seeded.toMutableList()
        for (e in big) {
            val k = e.n.lowercase()
            if (k !in seen) { seen.add(k); merged.add(e) }
        }
        cachedNames = merged
        return merged
    }

    /** Today's player by date — same player worldwide on a given day. */
    fun forToday(context: Context, dayMillis: Long = System.currentTimeMillis()): Footballer {
        val players = all(context)
        PINNED_ID?.let { id -> players.firstOrNull { it.id == id }?.let { return it } }
        val day = dayMillis / 86_400_000L
        val index = ((day % players.size).toInt() + players.size) % players.size
        return players[index]
    }

    fun loadImage(
        context: Context,
        path: String,
        reqWidth: Int = 1200,
        reqHeight: Int = 1600,
    ): Bitmap? = runCatching {
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        context.assets.open(path).use { BitmapFactory.decodeStream(it, null, bounds) }
        val opts = BitmapFactory.Options().apply {
            inSampleSize = calcSampleSize(bounds.outWidth, bounds.outHeight, reqWidth, reqHeight)
        }
        context.assets.open(path).use { BitmapFactory.decodeStream(it, null, opts) }
    }.getOrNull()

    fun loadOriginal(context: Context, p: Footballer, w: Int = 1200, h: Int = 1600): Bitmap? =
        loadImage(context, "images/${p.image}", w, h)

    fun loadSilhouette(context: Context, p: Footballer, w: Int = 1200, h: Int = 1600): Bitmap? =
        loadImage(context, "silhouettes/${if (p.silhouette.isNotEmpty()) p.silhouette else p.image}", w, h)

    private fun calcSampleSize(srcW: Int, srcH: Int, reqW: Int, reqH: Int): Int {
        if (srcW <= 0 || srcH <= 0) return 1
        var sample = 1
        while (srcW / (sample * 2) >= reqW && srcH / (sample * 2) >= reqH) sample *= 2
        return sample
    }

    /** Normalise for guess matching — strip accents + non-alnum, lowercase. */
    fun normalize(s: String): String {
        val nfd = Normalizer.normalize(s, Normalizer.Form.NFD)
        return nfd.replace(Regex("\\p{InCombiningDiacriticalMarks}+"), "")
            .lowercase()
            .replace(Regex("[^a-z0-9 ]"), "")
            .trim()
    }

    fun isCorrect(player: Footballer, guess: String): Boolean {
        val g = normalize(guess)
        if (g.isEmpty()) return false
        if (g == normalize(player.name)) return true
        return player.aliases.any { normalize(it) == g }
    }
}
