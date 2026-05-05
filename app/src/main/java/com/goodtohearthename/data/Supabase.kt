package com.goodtohearthename.data

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.builtins.ListSerializer
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.util.UUID

object Supabase {
    private const val URL_BASE = "https://bwohtrjkguveynfepqwi.supabase.co"
    private const val ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3b2h0cmprZ3V2ZXluZmVwcXdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ5NDQzNzksImV4cCI6MjA5MDUyMDM3OX0.Z0PwiN_EX_hNHyH4TT9K95SWlWyssUShxkV-0VasxpE"

    private val json = Json { ignoreUnknownKeys = true }

    @Serializable
    data class ScoreInsert(
        val display_name: String,
        val device_id: String,
        val player_id: String,
        val day_index: Int,
        val attempts: Int? = null,
        val correct: Boolean,
    )

    @Serializable
    data class LeaderboardRow(
        val display_name: String,
        val attempts: Int? = null,
        val correct: Boolean,
        val created_at: String? = null,
    )

    suspend fun submitScore(
        deviceId: String,
        displayName: String,
        playerId: String,
        dayIndex: Long,
        correct: Boolean,
        attempt: Int,
    ): Boolean = withContext(Dispatchers.IO) {
        val body = json.encodeToString(
            ScoreInsert.serializer(),
            ScoreInsert(
                display_name = displayName.trim().take(30),
                device_id = deviceId,
                player_id = playerId,
                day_index = dayIndex.toInt(),
                attempts = if (correct) attempt else null,
                correct = correct,
            )
        )
        runCatching {
            val conn = (URL("$URL_BASE/rest/v1/scores").openConnection() as HttpURLConnection).apply {
                requestMethod = "POST"
                doOutput = true
                connectTimeout = 6000
                readTimeout = 6000
                setRequestProperty("apikey", ANON_KEY)
                setRequestProperty("Authorization", "Bearer $ANON_KEY")
                setRequestProperty("Content-Type", "application/json")
                setRequestProperty("Prefer", "return=minimal")
            }
            conn.outputStream.use { OutputStreamWriter(it).use { w -> w.write(body) } }
            val code = conn.responseCode
            conn.disconnect()
            // 201 created, 204 no content (with return=minimal), 409 already submitted today — all fine
            code in 200..299 || code == 409
        }.getOrDefault(false)
    }

    suspend fun fetchTodayLeaderboard(dayIndex: Long): List<LeaderboardRow> = withContext(Dispatchers.IO) {
        runCatching {
            val q = "day_index=eq.$dayIndex&select=display_name,attempts,correct,created_at" +
                "&order=correct.desc,attempts.asc.nullslast,created_at.asc&limit=100"
            val conn = (URL("$URL_BASE/rest/v1/scores?$q").openConnection() as HttpURLConnection).apply {
                requestMethod = "GET"
                connectTimeout = 6000
                readTimeout = 6000
                setRequestProperty("apikey", ANON_KEY)
                setRequestProperty("Authorization", "Bearer $ANON_KEY")
            }
            val text = conn.inputStream.bufferedReader().use { it.readText() }
            conn.disconnect()
            json.decodeFromString(ListSerializer(LeaderboardRow.serializer()), text)
        }.getOrDefault(emptyList())
    }
}

object Profile {
    private const val PREFS = "gthn_profile"
    private const val K_DEVICE_ID = "device_id"
    private const val K_DISPLAY_NAME = "display_name"
    private const val K_NAME_DISMISSED = "name_dismissed"

    fun deviceId(context: Context): String {
        val p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        var id = p.getString(K_DEVICE_ID, null)
        if (id.isNullOrEmpty()) {
            id = UUID.randomUUID().toString().replace("-", "").take(32)
            p.edit().putString(K_DEVICE_ID, id).apply()
        }
        return id
    }

    fun displayName(context: Context): String? =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(K_DISPLAY_NAME, null)
            ?.takeIf { it.isNotBlank() }

    fun setDisplayName(context: Context, name: String?) {
        val p = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        if (name.isNullOrBlank()) p.edit().remove(K_DISPLAY_NAME).apply()
        else p.edit().putString(K_DISPLAY_NAME, name.trim().take(30)).apply()
    }

    fun nameDismissed(context: Context): Boolean =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(K_NAME_DISMISSED, false)

    fun setNameDismissed(context: Context) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit().putBoolean(K_NAME_DISMISSED, true).apply()
    }
}
