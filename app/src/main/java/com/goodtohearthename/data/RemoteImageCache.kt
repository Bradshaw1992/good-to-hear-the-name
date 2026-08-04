package com.goodtohearthename.data

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL

/**
 * On-disk cache for the reveal PHOTOS, which are served remotely (Cloudflare R2) rather than
 * bundled in the APK — see project-remote-images-v17. Silhouettes stay bundled and are NOT
 * handled here. The game stays fully playable offline (silhouette + clues from bundled data);
 * only the reveal photo needs a connection, and once fetched it is cached forever.
 *
 * Photos live at  <BASE_URL>images/<id>.jpg  and are prefetched ~30 days ahead on launch.
 */
object RemoteImageCache {

    // The only line that changes if the image origin ever moves (e.g. from the existing
    // Pages domain to a dedicated cdn. subdomain). Trailing slash required.
    const val BASE_URL = "https://cdn.goodtohearthename.co.uk/"

    // Set true in a debug build to exercise the remote/offline/placeholder path WITHOUT first
    // deleting the bundled photos (ContentRepository.loadOriginal otherwise prefers bundled).
    // Leave false for normal builds; it is irrelevant once the photos are removed from assets.
    const val FORCE_REMOTE = false

    private fun dir(context: Context): File =
        File(context.cacheDir, "photos").apply { mkdirs() }

    private fun fileFor(context: Context, name: String): File = File(dir(context), name)

    private fun urlFor(name: String): String = "${BASE_URL}images/$name"

    /**
     * Decoded photo bitmap, or null if it cannot be produced (not cached and either offline or
     * [allowNetwork] is false). When [allowNetwork] is true and the file is missing, it is
     * downloaded and cached first. Safe to call off the main thread only.
     */
    fun loadPhoto(context: Context, name: String, reqW: Int, reqH: Int, allowNetwork: Boolean): Bitmap? {
        if (name.isBlank()) return null
        val f = fileFor(context, name)
        if (!f.exists() || f.length() == 0L) {
            if (!allowNetwork) return null
            if (!download(name, f)) return null
        }
        return decodeSampled(f, reqW, reqH)
    }

    /** Download any of [names] not already cached. Silently skips failures (e.g. offline). */
    fun prefetch(context: Context, names: List<String>) {
        for (n in names) {
            if (n.isBlank()) continue
            val f = fileFor(context, n)
            if (!f.exists() || f.length() == 0L) download(n, f)
        }
    }

    private fun download(name: String, dest: File): Boolean {
        var conn: HttpURLConnection? = null
        val tmp = File(dest.parentFile, "${dest.name}.tmp")
        return try {
            conn = (URL(urlFor(name)).openConnection() as HttpURLConnection).apply {
                connectTimeout = 8_000
                readTimeout = 15_000
                requestMethod = "GET"
                instanceFollowRedirects = true
            }
            if (conn.responseCode !in 200..299) return false
            conn.inputStream.use { input -> FileOutputStream(tmp).use { out -> input.copyTo(out) } }
            if (tmp.length() > 0L) {
                if (dest.exists()) dest.delete()
                tmp.renameTo(dest)
                true
            } else {
                tmp.delete(); false
            }
        } catch (e: Exception) {
            tmp.delete()
            false
        } finally {
            conn?.disconnect()
        }
    }

    private fun decodeSampled(file: File, reqW: Int, reqH: Int): Bitmap? {
        return try {
            val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
            BitmapFactory.decodeFile(file.path, bounds)
            val opts = BitmapFactory.Options().apply {
                inSampleSize = calcSampleSize(bounds.outWidth, bounds.outHeight, reqW, reqH)
            }
            BitmapFactory.decodeFile(file.path, opts)
        } catch (e: Exception) {
            null
        }
    }

    private fun calcSampleSize(srcW: Int, srcH: Int, reqW: Int, reqH: Int): Int {
        var sample = 1
        if (srcH > reqH || srcW > reqW) {
            var halfH = srcH / 2
            var halfW = srcW / 2
            while (halfH / sample >= reqH && halfW / sample >= reqW) sample *= 2
        }
        return sample
    }
}
